import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import abstractDriver


def getDriverPath(driverFolder, browser=None):
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
# make browser headless or not
driver = abstractDriver.createDriver(browser, driverPath, False)


@pytest.mark.meteoschweiz
class TestMeteoSchweiz():
    def test_meteoschweiz_title(self):
        driver.get('https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle')
        assert driver.title == 'Homogene Messreihen ab 1864 - MeteoSchweiz'

    def test_meteoschweiz_xpath(self):
        urls = driver.find_elements_by_xpath(
            "//table[@id='stations-table']/tbody/tr"
            + "/td/span[@class='overflow']/a")
        assert len(urls) == 30


@pytest.mark.idaweb
class TestIDAWeb():
    def test_idaweb_title(self):
        driver.get("https://gate.meteoswiss.ch/idaweb/login.do")
        assert driver.title == 'MeteoSchweiz IDAWEB: Anmelden bei IDAWEB'
