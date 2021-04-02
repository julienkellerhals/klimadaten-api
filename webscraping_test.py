import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import abstractDriver

abstractDriver = abstractDriver.AbstractDriver()


@pytest.mark.meteoschweiz
class TestMeteoSchweiz():
    def test_meteoschweiz_title(self):
        driver = abstractDriver.getDriver()
        driver.get('https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle')
        title = driver.title
        driver.quit()
        assert title == 'Homogene Messreihen ab 1864 - MeteoSchweiz'

    def test_meteoschweiz_xpath(self):
        driver = abstractDriver.getDriver()
        driver.get('https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle')
        urls = driver.find_elements_by_xpath(
            "//table[@id='stations-table']/tbody/tr"
            + "/td/span[@class='overflow']/a")
        driver.quit()
        assert len(urls) == 30


@pytest.mark.idaweb
class TestIDAWeb():
    def test_idaweb_title(self):
        driver = abstractDriver.getDriver()
        driver.get("https://gate.meteoswiss.ch/idaweb/login.do")
        title = driver.title
        driver.quit()
        assert title == 'MeteoSchweiz IDAWEB: Anmelden bei IDAWEB'
