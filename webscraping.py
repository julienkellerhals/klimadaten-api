import re
import math
import time
import yaml
import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
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

def getLastPageBool(driver, lastPageBool):
    arrowPath = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, '//*[@id="body_block"]/form/div[5]'))).find_elements_by_tag_name("img")[2].get_attribute("src")
    if arrowPath.split("/")[-1:][0] == "arrowrightblack.gif":
        lastPageBool = True
    else:
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]/a[@title="Next"]').click()

    return lastPageBool

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
    saved_documents = []
    configFileName = "idawebConfig.yaml"

    # login
    scrape_idaweb_login(driver)

    # read config file
    config = readConfig(configFileName)

    for searchGranularity in config:
        for searchGroupDict in config[searchGranularity]:
            searchGroup = list(searchGroupDict.keys())[0]
            for searchName in searchGroupDict[searchGroup]:
                orderNumber = 1
                # create order name
                now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')




                idaWebParameterPortal(driver)
                idaWebParameterPreselection(driver, searchGroup, searchGranularity, searchName)
                idaWebStationPreselection(driver)
                




                # Start time preselection
                since = "01.01.1800"
                until = date.today().strftime('%d.%m.%Y')
                idaWebTimePreselection(driver, since, until)




                tooManyEntriesBool = True
                noEntriesBool = False
                timeDeltaList = [1000, 100, 10, 1]
                while True:
                    tooManyEntriesBool, noEntriesBool = idaWebDataInventoryCount(driver, tooManyEntriesBool, noEntriesBool)
                    if not len(timeDeltaList) == 0:
                        if tooManyEntriesBool:
                            timeDeltaList.remove(timeDeltaList[0])
                            if (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).date() < date.today():
                                until = (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).strftime('%d.%m.%Y')
                            else:
                                until = date.today().strftime('%d.%m.%Y')
                            idaWebTimePreselection(driver, since, until)
                        else:
                            if not noEntriesBool:
                                idaWebDataInventory(driver)

                                orderName = f'{searchGroup[0]}{searchGranularity.lower()}{orderNumber}_{now}'    
                                idaWebOrder(driver, orderName)
                                orderNumber += 1

                                idaWebSummary(driver)
                                idaWebAgbs(driver)

                                # Go back to start and continue with next time frame
                                since = until
                                if (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).date() < date.today():
                                    until = (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).strftime('%d.%m.%Y')
                                else:
                                    until = date.today().strftime('%d.%m.%Y')

                                # redo the whole order process
                                idaWebParameterPortal(driver)
                                idaWebParameterPreselection(driver, searchGroup, searchGranularity, searchName)
                                idaWebStationPreselection(driver)
                                idaWebTimePreselection(driver, since, until)

                            else:
                                since = until
                                if (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).date() < date.today():
                                    until = (datetime.strptime(since, "%d.%m.%Y") + relativedelta(years=timeDeltaList[0])).strftime('%d.%m.%Y')
                                else:
                                    until = date.today().strftime('%d.%m.%Y')
                                idaWebTimePreselection(driver, since, until)

                    
                    else:
                        idaWebDataInventoryManual(driver)
                        inventoryDf = scrapeIdawebInventory(driver)
                        chunks = splitDf(inventoryDf, 400)
                        for chunk in chunks:
                            for value in chunk["value"]:
                                js = (
                                    "var form = document.getElementsByTagName('form')[0];" # get form
                                    "var checkbox = document.createElement('input');" # create input
                                    "checkbox.checked = true;" # set input to checked
                                    "checkbox.name = 'selection';" # set input name
                                    f"checkbox.value = '{value}';" # set input value
                                    "updateCount(checkbox.checked);" # update count
                                    "form.appendChild(checkbox);" # add checkbox
                                )
                                driver.execute_script(js)

                        # create order name
                        now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')
                        orderName = f'{searchGroup[0]}{searchGranularity.lower()}{orderNumber}_{now}'
                        
                        # Continue with order process
                        orderNavigationProcess(driver, orderName)

                        orderNumber += 1
                        # Add roder to list
                        saved_documents.append(orderName)

    print(saved_documents)

    return str(saved_documents)

def scrape_idaweb_login(driver):
    driver.get("https://gate.meteoswiss.ch/idaweb/login.do")

    # log into page
    driver.find_element_by_name('user').send_keys('simon.schmid1@fhnw.ch')
    driver.find_element_by_name('password').send_keys('AF3410985C')
    driver.find_element_by_xpath('//*[@id="content_block"]/form/fieldset/table/tbody/tr[3]/td/table/tbody/tr/td[1]/input').click()

def idaWebParameterPortal(driver):
    # go to parameter portal
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="menu_block"]/ul/li[5]/a').click()

def idaWebParameterPreselection(driver, searchGroup, searchGranularity, searchName):
    # select search parameter
    driver.find_element_by_xpath(f'//*[@id="paramGroup_input"]/option[@value="{searchGroup}"]').click()
    driver.find_element_by_xpath(f'//*[@id="granularity_input"]/option[@value="{searchGranularity}"]').click()
    driver.find_element_by_name('shortName').send_keys(searchName)

    # click search
    driver.find_element_by_xpath('//*[@id="filter_actions"]/input[1]').click()

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[1]').click()

def idaWebStationPreselection(driver):
    # go to station preselection
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Station preselection")]').click()

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[1]').click()  

def idaWebTimePreselection(driver, since, until):
    # go to time preselection
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Time preselection")]').click()

    # clear input
    driver.find_element_by_name('since').clear()
    driver.find_element_by_name('till').clear()
    
    # click from and until
    driver.find_element_by_name('since').send_keys(str(since)) 
    driver.find_element_by_name('till').send_keys(str(until))

def idaWebDataInventoryCount(driver, tooManyEntriesBool, noEntriesBool):
    # go to data inventory
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Data inventory")]').click()   

    # get length of entries
    lengthDiv = driver.find_element_by_class_name('pager').text
    length = int(re.findall(r'\[.*\/ (\d+)\]', lengthDiv)[0])

    if length > 400:
        tooManyEntriesBool = True
    else:
        tooManyEntriesBool = False
    
    if length == 0:
        noEntriesBool = True
    else:
        noEntriesBool = False
    
    return tooManyEntriesBool, noEntriesBool

def idaWebDataInventory(driver):
    # go to data inventory
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Data inventory")]').click()   

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[2]').click()  

def idaWebDataInventoryManual(driver):
    # go to data inventory
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Data inventory")]').click()   

    print("Here")

def idaWebOrder(driver, orderName):
    # go to order
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Order")]').click()

    # create order
    driver.find_element_by_name('orderText').send_keys(orderName)
    
    # change data format 
    driver.find_element_by_xpath('//*[@id="dataFormat_input"]/option[2]').click()

    # split delivery
    driver.find_element_by_name('split').click()

def idaWebSummary(driver):
    # go to summary
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "Summary")]').click()

def idaWebAgbs(driver):
    # go to general terms and conditions
    driver.find_element_by_xpath('//*[@id="wizard"]//*[contains(., "General Terms and Conditions")]').click()

    # accept general terms and conditions
    driver.find_element_by_name('acceptAgbs').click()

    # click order
    driver.find_element_by_xpath('//*[@id="form_block"]/div/fieldset/table[2]/tbody/tr/td[3]/table/tbody/tr/td/input').click()

    # click next
    driver.find_element_by_xpath('//*[@id="content_block"]/form/table/tbody/tr[14]/td[2]/input').click()

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

        lastPageBool = getLastPageBool(driver, lastPageBool)
        
    inventoryDf = pd.DataFrame(data=inventoryList)
    inventoryDf = inventoryDf.drop_duplicates()
    return inventoryDf

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

        lastPageBool = getLastPageBool(driver, lastPageBool)

    orderDf = pd.DataFrame(data=orderDataList)

    return orderDf
