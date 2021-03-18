import pandas as pd
import download

def scrape_meteoschweiz(driver):
    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

    url_list = []

    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    allStationsDf = pd.DataFrame(columns= ['Year','Month','Temperature','Precipitation','Station'])

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
        stationDf = pd.DataFrame(nestedData[1:],columns=nestedData[0])
        
        # add station name as column to data frame
        station_list = [station for i in range(len(nestedData) -1)]
        stationDf['Station'] = station_list 

        # append the data frame to the data frame of all stations
        allStationsDf = allStationsDf.append(stationDf, ignore_index = True)

    return str(allStationsDf)