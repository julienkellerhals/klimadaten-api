import pandas as pd
import download

def scrape_meteoschweiz(driver):
    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

    url_list = []

    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    for url in urls:
        url_list.append(url.get_attribute('href'))
    
    homoALTPage, _, _ = download.getRequest("https://www.meteoschweiz.admin.ch/product/output/climate-data/homogenous-monthly-data-processing/data/homog_mo_ALT.txt")
    data = homoALTPage.text.splitlines()
    columnNames = data[27].split()
    stripedData = data[28:]
    ALTDictList = []
    for data in stripedData:
        row = data.split()
        rowDict = dict(zip(columnNames, row))
        ALTDictList.append(rowDict)
    ALTDf = pd.DataFrame(data= ALTDictList, columns = columnNames)

    print(ALTDf)

    return str(ALTDf)
