import pytest
import abstractDriver
import messageAnnouncer
import pandas as pd
from typing import List
from webscraping import readConfig
from webscraping import scrape_idaweb_login
from webscraping import scrapeIdawebOrders
from webscraping import setAllStations
from webscraping import getUrls
from webscraping import startWebscraping
from webscraping import password as webscrapingPassword

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

    def testSetAllStations(self):
        allStationsDf = setAllStations()
        if isinstance(allStationsDf, pd.DataFrame):
            assert len(allStationsDf) == 0
        else:
            assert False

    def getUrls(self):
        driver = abstractDriver.getDriver()
        urls = getUrls(driver)
        if isinstance(urls, pd.DataFrame):
            assert len(urls) != 0
        else:
            assert False

    def testStartWebscrapingUrlList(self):
        driver = abstractDriver.getDriver()
        urls = getUrls(driver)
        url_list = []
        allStationsDf = setAllStations()

        url_list, allStationsDf = startWebscraping(
            url_list,
            urls,
            announcer,
            allStationsDf
        )
        if isinstance(url_list, List):
            assert len(url_list) != 0
        else:
            assert False


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
        password = webscrapingPassword
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
