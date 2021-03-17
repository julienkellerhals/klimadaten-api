from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shutil import which
import pandas as pd

chrome_options = Options()
chrome_options.add_argument("--headless")

chrome_path = which('chromedriver')
print(which('chromedriver'))
driver = webdriver.Chrome(executable_path=str(chrome_path), options=chrome_options)
driver.set_window_size(1800, 1080)
driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")

url_list = []

urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")

for url in urls:
    url_list.append(url.get_attribute('href'))

#
# driver.get("https://www.meteoschweiz.admin.ch/product/output/climate-data/homogenous-monthly-data-processing/data/homog_mo_ALT.txt")

# mylist = []

# mydata = driver.find_elements_by_xpath("//body/pre")

# for data in mydata:
#     mylist.append(data.text)

driver.close()

print(url_list)

# print(mydata)