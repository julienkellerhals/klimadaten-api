from typing import List
import pytest
import abstractDriver
import messageAnnouncer
import pandas as pd
from webscraping import readConfig
from webscraping import scrape_idaweb_login
from webscraping import scrapeIdawebOrders


announcer = messageAnnouncer.MessageAnnouncer()
abstractDriver = abstractDriver.AbstractDriver(announcer)


@pytest.mark.meteoschweiz
class TestMeteoSchweiz():
    def test_meteoschweiz_title(self):
        driver = abstractDriver.getDriver()
        driver.get(
            "https://www.meteoschweiz.admin.ch/home/klima/" +
            "schweizer-klima-im-detail/homogene-messreihen-ab-1864.html" +
            "?region=Tabelle"
        )
        title = driver.title
        driver.quit()
        assert title == 'Homogene Messreihen ab 1864 - MeteoSchweiz'

    def test_meteoschweiz_xpath(self):
        driver = abstractDriver.getDriver()
        driver.get(
            "https://www.meteoschweiz.admin.ch/home/klima/" +
            "schweizer-klima-im-detail/homogene-messreihen-ab-1864.html" +
            "?region=Tabelle"
        )
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

    def test_idaweb_login_sucess(self):
        username = "joel.grosjean@students.fhnw.ch"
        password = "AGEJ649GJAL02"
        driver = abstractDriver.getDriver()
        url = "https://gate.meteoswiss.ch/idaweb/login.do"
        scrape_idaweb_login(driver, username, password)
        assert driver.current_url is not url

    def test_idaweb_login_faild(self):
        username = "joel.grosjean@students.fhnw.ch"
        password = "Wrong"
        driver = abstractDriver.getDriver()
        url = "https://gate.meteoswiss.ch/idaweb/login.do"
        scrape_idaweb_login(driver, username, password)
        assert driver.current_url == url

    def testScrapeIdawebOrders(self):
        driver = abstractDriver.getDriver()
        orderDF = scrapeIdawebOrders(driver)
        if isinstance(orderDF, pd.DataFrame):
            assert len(orderDF) != 0
        else:
            assert False

    def testReadConfigSuccess(self):
        configFileName = "idawebConfig.xml"
        configFile = readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) != 0
        else:
            assert False

    def testReadConfigFail(self):
        configFileName = "wrongFile.xml"
        configFile = readConfig(configFileName)
        if isinstance(configFile, List):
            assert len(configFile) == 0
        else:
            assert False
