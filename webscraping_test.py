import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import abstractDriver

def getDriverPath(driverFolder, browser = None):
    driverInstalledBool = False
    driverPath = ""
    for driverPath in list(driverFolder.glob('**/*.exe')):
        if browser is not None:
            if browser.lower() in driverPath.name:
                driverInstalledBool = True
                driverPath = driverPath
        else:
            driverPath = driverPath
    return driverInstalledBool, driverPath

cwd = Path.cwd()
driverFolder = cwd / "driver"
_, driverPath = getDriverPath(driverFolder, None)
if driverPath.name == "msedgedriver.exe":
    browser = "Edg"
elif driverPath.name == "chromedriver.exe":
    browser = "Chrome"
else:
    print("Browser not supported yet")
driver = abstractDriver.createDriver(browser, driverPath, False) # make browser headless or not 

def test_meteoschweiz_title():
    driver.get('https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle')
    assert driver.title == 'Homogene Messreihen ab 1864 - MeteoSchweiz'