import pandas as pd
import download

def scrape_meteoschweiz(driver):
    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

    url_list = []

    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    df_all_stations = pd.DataFrame(columns= ['Year','Month','Temperature','Precipitation','Station'])

    for url in urls:
        url_list.append(url.get_attribute('href'))
    
        browserDriverDownloadPage, _, _ = download.getRequest(url.get_attribute('href'))
        data = str(browserDriverDownloadPage.content)

        s_list = data.split(sep='\\r\\n')
        s_list_2 = []

        for i in range(len(s_list)):
            s_list_2.append(s_list[i].split())

        station = ' '.join(s_list_2[5][1:]) # get station name

        index_beginning = []
        
        for i in range(len(s_list_2)): 
            try:
                if s_list_2[i][0] == 'Year' and s_list_2[i][1] == 'Month':
                    index_beginning.append(i)
            except:
                pass
        
        s_list_2 = s_list_2[index_beginning[0]:-1] # remove header and last item

        mydf = pd.DataFrame(s_list_2[1:],columns=s_list_2[0])
        station_list = [station for i in range(len(s_list_2) -1)]
        mydf['Station'] = station_list

        df_all_stations = df_all_stations.append(mydf, ignore_index = True)
        df_all_stations.to_json(r'.\all_stations.json', index = True)

    resp = df_all_stations
    return resp
