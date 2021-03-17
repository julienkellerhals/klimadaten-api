import pandas as pd
import download

def scrape_meteoschweiz(driver):
    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

    url_list = []

    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

    for url in urls:
        url_list.append(url.get_attribute('href'))
    
    browserDriverDownloadPage, _, _ = download.getRequest("https://www.meteoschweiz.admin.ch/product/output/climate-data/homogenous-monthly-data-processing/data/homog_mo_ALT.txt")
    mynewdata = str(browserDriverDownloadPage.content)

    print(url_list)
    
    resp = mynewdata

    return resp
