import pytest
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

def test_meteoschweiz_title():
    driver = webdriver.Chrome("C:/Users/Lars Altschul/Documents/Home/FH/FHNW/2. Semester/cdk1/klimadaten-api/driver/chromedriver.exe")
    driver.get('https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle')
    assert driver.title == 'Homogene Messreihen ab 1864 - MeteoSchweiz'