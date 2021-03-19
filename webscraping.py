import re
import time
import numpy as np
import pandas as pd
from datetime import date
from datetime import datetime
import download
import math
from selenium.common.exceptions import NoSuchElementException

def scrape_meteoschweiz(driver, engine):

    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

    url_list = []

    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    allStationsDf = pd.DataFrame(columns= ['year','month','temperature','precipitation','station'])

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

    scrape_idaweb_login(driver, engine)
    scrape_idaweb_navigate(driver, engine)
    # find out length
    length, total_length = scrape_idaweb_length(driver, engine)
    # total number of pages
    num_of_pages = math.ceil(total_length / 16)
    # find out new offset and length
    offset, length, num_of_pages = scrape_idaweb_select(driver, engine, length, offset, num_of_pages)
    number, saved_documents = scrape_idaweb_order(driver, engine, number, saved_documents)
    

    while length > 0:
        scrape_idaweb_navigate(driver, engine)
        # find out new offset and length
        offset, length, num_of_pages = scrape_idaweb_select(driver, engine, length, offset, num_of_pages)
        number, saved_documents = scrape_idaweb_order(driver, engine, number, saved_documents)
    
    return 'done'

def scrape_idaweb_login(driver, engine):
    driver.get("https://gate.meteoswiss.ch/idaweb/login.do")

    # log into page
    driver.find_element_by_name('user').send_keys('simon.schmid1@fhnw.ch')
    driver.find_element_by_name('password').send_keys('AF3410985C')
    driver.find_element_by_xpath('//*[@id="content_block"]/form/fieldset/table/tbody/tr[3]/td/table/tbody/tr/td[1]/input').click()

def scrape_idaweb_navigate(driver, engine):
    # go to parameter portal
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="menu_block"]/ul/li[5]/a').click()

    # select search parameter
    driver.find_element_by_xpath('//*[@id="paramGroup_input"]/option[5]').click()
    driver.find_element_by_xpath('//*[@id="granularity_input"]/option[2]').click()

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

def scrape_idaweb_length(driver, engine):
    # find out how many orders we are making, so we can limit it.
    lengthDiv = driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]').text
    length = int(re.findall('\[.*\/ (\d+)\]', lengthDiv)[0])
    total_length = length

    return (length, total_length)

def scrape_idaweb_select(driver, engine, length, offset, num_of_pages):
    # go to the right offset position
    for i in range(offset):
        driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]/a[@title="Next"]').click()
    
    # decide how many pages to scrape
    if num_of_pages > 10:
        pages_to_scrape = 10
    else:
        pages_to_scrape = num_of_pages

    # select
    for j in range(pages_to_scrape):
        for i in range(1,17):
            # check if checkbox is missing
            try:
                driver.find_element_by_xpath(f'//*[@id="body_block"]/form/div[4]/table/tbody/tr[{i}]/td[8]/nobr/input').click()
            except NoSuchElementException:
                pass
        
        offset += 1
        num_of_pages -= 1

        # go to next page
        if j + 1 < pages_to_scrape:
            driver.find_element_by_xpath('//*[@id="body_block"]/form/div[5]/a[@title="Next"]').click()
            

    # where we are
    length -= 160

    return (offset, length, num_of_pages)

def scrape_idaweb_order(driver, engine, number, saved_documents):
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
