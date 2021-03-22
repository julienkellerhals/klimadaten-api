import re
import math
import time
import yaml
import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import download

def readConfig(configFileName):
    with open(configFileName) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config

def indexMarks(nrows, chunk_size):
    return range(chunk_size, math.ceil(nrows / chunk_size) * chunk_size, chunk_size)

def splitDf(dfm, chunk_size):
    indices = indexMarks(dfm.shape[0], chunk_size)
    return np.split(dfm, indices)

def scrape_meteoschweiz(driver, engine):
    url_list = []
    allStationsDf = pd.DataFrame(columns= ['year','month','temperature','precipitation','station'])

    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")
    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    for url in urls:
        url_list.append(url.get_attribute('href'))
    
        dataPage, _, _ = download.getRequest(url.get_attribute('href'))
        data = dataPage.text.splitlines()

        nestedData = []

        for i in range(len(data)):
            nestedData.append(data[i].split())

        # get station name
        station = ' '.join(nestedData[5][1:]) # get station name
      
        # find size of header and remove the header
        for i in range(len(nestedData)):
            if len(nestedData[i]) > 2:
                if nestedData[i][0] == 'Year' and nestedData[i][1] == 'Month':
                    index_beginning = i
                    break
        nestedData = nestedData[index_beginning:] 

        # create data frame
        columnHeaders = [i.lower() for i in nestedData[0]]
        stationDf = pd.DataFrame(nestedData[1:],columns=columnHeaders)
        
        # add station name as column to data frame
        station_list = [station for i in range(len(nestedData) -1)]
        stationDf['station'] = station_list 

        # append the data frame to the data frame of all stations
        allStationsDf = allStationsDf.append(stationDf, ignore_index = True)

    # change column data types
    allStationsDf = allStationsDf.astype({'year': int, 'month': int, 'station': str}, errors = 'ignore')
    allStationsDf["temperature"] = pd.to_numeric(allStationsDf["temperature"], errors='coerce')
    allStationsDf["precipitation"] = pd.to_numeric(allStationsDf["precipitation"], errors='coerce')

    allStationsDf.to_sql('meteoschweiz_t', engine, schema = 'stage', if_exists = 'append', index = False)

    """
    allStationsDf.isnull().sum().head()
    pd.to_numeric(allStationsDf["Temperature"], errors='coerce')
    allStationsDf.dtypes
    """
    return str(allStationsDf)

def scrape_idaweb(driver, engine):
    offset = 0
    number = 1 # numbers the queries
    saved_documents = []
    configFileName = "idawebConfig.yaml"

    # login
    scrape_idaweb_login(driver)

    # read config file
    config = readConfig(configFileName)

    for searchGranularity in config:
        for searchGroup in config[searchGranularity]:
            scrape_idaweb_navigate(driver, searchGroup, searchGranularity)

            # get inventory and split into 160 chunks
            inventoryDf = scrapeIdawebInventory(driver)
            chunks = splitDf(inventoryDf, 160)
            for chunk in chunks:
                formData = 'var data = new FormData(document.getElementsByTagName("form")[0])'
                
            number, saved_documents = scrape_idaweb_order(driver, number, saved_documents)

    print(saved_documents)

    return 'done'

def scrape_idaweb_login(driver):
    driver.get("https://gate.meteoswiss.ch/idaweb/login.do")

    # log into page
    driver.find_element_by_name('user').send_keys('simon.schmid1@fhnw.ch')
    driver.find_element_by_name('password').send_keys('AF3410985C')
    driver.find_element_by_xpath('//*[@id="content_block"]/form/fieldset/table/tbody/tr[3]/td/table/tbody/tr/td[1]/input').click()

def scrape_idaweb_navigate(driver, searchGroup, searchGranularity):
    # go to parameter portal
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="menu_block"]/ul/li[5]/a').click()

    # select search parameter
    driver.find_element_by_xpath(f'//*[@id="paramGroup_input"]/option[@value="{searchGroup}"]').click()
    driver.find_element_by_xpath(f'//*[@id="granularity_input"]/option[@value="{searchGranularity}"]').click()

    # click search
    driver.find_element_by_xpath('//*[@id="filter_actions"]/input[1]').click()

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[1]').click()

    # go to station preselection
    driver.find_element_by_xpath('//*[@id="wizard"]/a[1]').click()

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[1]').click()  

    # go to time preselection
    driver.find_element_by_xpath('//*[@id="wizard"]/a[3]').click()  

    # click from and until
    driver.find_element_by_name('since').send_keys('01.01.1800') 
    driver.find_element_by_name('till').send_keys(str(date.today().strftime('%d.%m.%Y')))

    # go to data inventory
    driver.find_element_by_xpath('//*[@id="wizard"]/a[4]').click()   

def scrape_idaweb_order(driver, number, saved_documents):
    # go to order
    driver.find_element_by_xpath('//*[@id="wizard"]/a[5]').click()

    now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')
    # create order name
    driver.find_element_by_name('orderText').send_keys(f'ld{number}_{now}')
    number += 1
    # append document name to saved documents
    saved_documents.append(f'ld{number}_{now}')

    # change data format 
    driver.find_element_by_xpath('//*[@id="dataFormat_input"]/option[2]').click()

    # go to summary
    driver.find_element_by_xpath('//*[@id="wizard"]/a[6]').click()

    # go to general terms and conditions
    driver.find_element_by_xpath('//*[@id="wizard"]/a[7]').click()

    # accept general terms and conditions
    driver.find_element_by_name('acceptAgbs').click()

    # click order
    driver.find_element_by_xpath('//*[@id="form_block"]/div/fieldset/table[2]/tbody/tr/td[3]/table/tbody/tr/td/input').click()
    
    # click next
    driver.find_element_by_xpath('//*[@id="content_block"]/form/table/tbody/tr[14]/td[2]/input').click()

    return (number, saved_documents)

def scrapeIdawebOrders(driver):
    rowHeaders = ["no", "reference", "orderDate", "status", "deliveryNote", "delivery", "action", "downloadLink"]
    orderDataList = []
    lastPageBool = False

    while not lastPageBool:
        for row in driver.find_elements_by_xpath('//*[@id="body_block"]/form/div[4]/table/tbody/tr[*]'):
            rowContent = []
            for col in row.find_elements_by_tag_name("td"):
                rowContent.append(col.text)
            
            downloadLink = ""
            if len(row.find_elements_by_xpath('./td[6]/nobr/a')) > 0:
                downloadLink = row.find_element_by_xpath('./td[6]/nobr/a').get_attribute("href")
            rowContent.append(downloadLink)
                
            orderDataList.append(dict(zip(rowHeaders, rowContent)))
        driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]')
        arrowPath = driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]').find_elements_by_tag_name("img")[2].get_attribute("src")
        if arrowPath.split("/")[-1:][0] == "arrowrightblack.gif":
            lastPageBool = True
        else:
            driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]/a[@title="Next"]').click()
    orderDf = pd.DataFrame(data=orderDataList)

    return orderDf

def scrapeIdawebInventory(driver):
    rowHeaders = ["station", "alt", "parameter", "unit", "granularity", "from", "until", "value"]
    inventoryList = []
    lastPageBool = False

    while not lastPageBool:
        for row in driver.find_elements_by_xpath('//*[@id="body_block"]/form/div[4]/table/tbody/tr[*]'):
            cols = row.find_elements_by_tag_name("td")
            rowContent = [col.text for col in cols[:-1]]
            rowContent.append(cols[-1].find_element_by_tag_name("input").get_attribute("value"))
            inventoryList.append(dict(zip(rowHeaders, rowContent)))

        driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]')
        arrowPath = driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]').find_elements_by_tag_name("img")[2].get_attribute("src")
        if arrowPath.split("/")[-1:][0] == "arrowrightblack.gif":
            lastPageBool = True
        else:
            driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]/a[@title="Next"]').click()
    inventoryDf = pd.DataFrame(data=inventoryList)
    inventoryDf = inventoryDf.drop_duplicates()
    return inventoryDf
