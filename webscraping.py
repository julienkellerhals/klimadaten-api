import pandas as pd
import download
import numpy as np
import time
from datetime import date

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
    driver.get("https://gate.meteoswiss.ch/idaweb/login.do")

    # log into page
    driver.find_element_by_name('user').send_keys('simon.schmid1@fhnw.ch')
    driver.find_element_by_name('password').send_keys('AF3410985C')
    driver.find_element_by_xpath('//*[@id="content_block"]/form/fieldset/table/tbody/tr[3]/td/table/tbody/tr/td[1]/input').click()

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

    # go to time preselection
    driver.find_element_by_xpath('//*[@id="wizard"]/a[4]').click()  

    # click select all
    driver.find_element_by_xpath('//*[@id="list_actions"]/input[1]').click()  
    
    # to go order
    driver.find_element_by_xpath('//*[@id="wizard"]/a[5]').click()  

    return 'helloworld'

