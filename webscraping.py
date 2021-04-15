import re
import math
import time
import numpy as np
import pandas as pd
from lxml import etree
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# from selenium.common.exceptions import TimeoutException
# from selenium.common.exceptions import NoSuchElementException
import download


def createJs(value):
    """ Creates js for idaweb form

    Args:
        value (str): idaweb checkbox value

    Returns:
        str: Javascript to be executed on page
    """

    js = (
        "var form = document.getElementsByTagName('form')[0];"  # get form
        "var checkbox = document.createElement('input');"  # create input
        "checkbox.checked = true;"  # set input to checked
        "checkbox.name = 'selection';"  # set input name
        f"checkbox.value = '{value}';"  # set input value
        "updateCount(checkbox.checked);"  # update count
        "form.appendChild(checkbox);"  # add checkbox
    )
    return js


def createOrderName(config, orderNumber, now):
    """ Creates order name

    Args:
        config (xml): Config from idawebConfig.xml
        orderNumber (str): Order number
        now (str): Date time from order

    Returns:
        str: Order name for idaweb data
    """

    orderName = f"{config.attrib['group'][0]}" \
                f"{config.attrib['granularity'].lower()}" \
                f"{orderNumber}_{now}"
    return orderName


def readConfig(configFileName):
    """ Read config file

    Args:
        configFileName (str): config file name

    Returns:
        list: Configuration in config file
    """

    configList = []

    tree = etree.parse(configFileName)
    root = tree.getroot()
    for config in root:
        configList.append(config)
    return configList


def indexMarks(nrows, chunk_size):
    """ Return idx range for df spliting

    Args:
        nrows (int): Number of rows in dataframe
        chunk_size (int): Target chunk size

    Returns:
        range: Index range for split
    """

    indexMarksRange = range(
        chunk_size,
        math.ceil(nrows / chunk_size) * chunk_size,
        chunk_size
    )
    return indexMarksRange


def splitDf(dfm, chunk_size):
    """ Splits df into specified chunks

    Args:
        dfm (df): Input dataframe
        chunk_size (int): Target chunk size for df

    Returns:
        np: Splited df
    """

    indices = indexMarks(dfm.shape[0], chunk_size)
    return np.split(dfm, indices)


def getLastPageBool(driver, lastPageBool):
    """ Checks if the driver is at the last table page

    Args:
        driver (driver): Web driver
        lastPageBool (bool): If last page

    Returns:
        bool: If last page
    """

    arrowPath = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="body_block"]/form/div[5]')
        )
    ).find_elements_by_tag_name("img")[2].get_attribute("src")

    if arrowPath.split("/")[-1:][0] == "arrowrightblack.gif":
        lastPageBool = True
    else:
        time.sleep(1)
        driver.find_element_by_xpath(
            '//*[@id="body_block"]/form/div[5]/a[@title="Next"]'
        ).click()
    return lastPageBool


def getUntil(since, timeDeltaList):
    """ Creates until time for data request (max. today)

    Args:
        since (datetime): Since datetime
        timeDeltaList (array): Delta to add on since date

    Returns:
        datetime: Incremented since date
    """

    if (datetime.strptime(since, "%d.%m.%Y") + relativedelta(
            years=timeDeltaList[0])).date() < date.today():
        until = (datetime.strptime(since, "%d.%m.%Y") + relativedelta(
            years=timeDeltaList[0])).strftime('%d.%m.%Y')
    else:
        until = date.today().strftime('%d.%m.%Y')
    return until


# main function
def scrape_meteoschweiz(driver, engine, announcer):
    """ Scrape data from meteo suisse

    Args:
        driver (driver): Selenium driver
        engine (engine): Database engine
        announcer (announcer): Message announcer

    Returns:
        str: Scrapped data
    """

    url_list = []
    allStationsDf = pd.DataFrame(columns=[
        'year',
        'month',
        'temperature',
        'precipitation',
        'station'
    ])

    driver.get(
        "https://www.meteoschweiz.admin.ch/home/klima/"
        + "schweizer-klima-im-detail/"
        + "homogene-messreihen-ab-1864.html?region=Tabelle"
    )
    urls = driver.find_elements_by_xpath(
        "//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a"
    )

    for urlEl in urls:
        url = urlEl.get_attribute('href')

        msgTxt = "Scrapping: " + url
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

        url_list.append(url)

        dataPage, _, _ = download.getRequest(url)
        data = dataPage.text.splitlines()

        nestedData = []

        for i in range(len(data)):
            nestedData.append(data[i].split())

        # get station name
        station = ' '.join(nestedData[5][1:])  # get station name

        # find size of header and remove the header
        for i in range(len(nestedData)):
            if len(nestedData[i]) > 2:
                if nestedData[i][0] == 'Year' and nestedData[i][1] == 'Month':
                    index_beginning = i
                    break
        nestedData = nestedData[index_beginning:]

        # create data frame
        columnHeaders = [i.lower() for i in nestedData[0]]
        stationDf = pd.DataFrame(nestedData[1:], columns=columnHeaders)

        # add station name as column to data frame
        station_list = [station for i in range(len(nestedData)-1)]
        stationDf['station'] = station_list

        # append the data frame to the data frame of all stations
        allStationsDf = allStationsDf.append(stationDf, ignore_index=True)

    # change column data types
    allStationsDf = allStationsDf.astype(
        {
            'year': int,
            'month': int,
            'station': str
        },
        errors='ignore'
    )
    allStationsDf["temperature"] = pd.to_numeric(
        allStationsDf["temperature"],
        errors='coerce'
    )
    allStationsDf["precipitation"] = pd.to_numeric(
        allStationsDf["precipitation"],
        errors='coerce'
    )

    allStationsDf["load_date"] = pd.to_datetime('today').normalize()

    allStationsDf.to_sql(
        'meteoschweiz_t',
        engine,
        schema='stage',
        if_exists='append',
        index=False
    )

    # allStationsDf.isnull().sum().head()
    # pd.to_numeric(allStationsDf["Temperature"], errors='coerce')
    # allStationsDf.dtypes

    # TODO See what to return
    return str(allStationsDf)


# main function
def scrape_idaweb(driver, engine):
    """ Scrape idaweb

    Args:
        driver (driver): Selenium driver
        engine (engine): Database engine

    Returns:
        str: Downloaded documents list
    """

    saved_documents = []
    configFileName = "idawebConfig.xml"

    # read config file
    configList = readConfig(configFileName)

    # login
    scrape_idaweb_login(driver)


    # for every variable in idawebConfig.xml
    for config in configList:
        orderNumber = 1
        # get date and time for order name
        now = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')

        # select params according to confic in param preselecton
        idaWebParameterPortal(driver)
        idaWebParameterPreselection(
            driver,
            config.attrib['group'],
            config.attrib['granularity'],
            config.text
        )
        idaWebStationPreselection(driver)

        # Start time preselection
        since = "01.01.1800"
        until = date.today().strftime('%d.%m.%Y')
        idaWebTimePreselection(driver, since, until)

        tooManyEntriesBool = True
        noEntriesBool = False
        timeDeltaList = [300, 100, 30, 10, 3, 1]
        notFinished = True
        # selection and ordering of data
        while notFinished:
            tooManyEntriesBool, noEntriesBool = idaWebDataInventoryCount(
                driver,
                tooManyEntriesBool,
                noEntriesBool
            )
            # try selecting with select all as long as there are elements in timeDeltaList
            if not len(timeDeltaList) == 0:

                # if time delta too big, make it smaller
                if tooManyEntriesBool:
                    timeDeltaList.remove(timeDeltaList[0])
                    until = getUntil(since, timeDeltaList)
                    idaWebTimePreselection(driver, since, until)
                else:

                    # if the selection has entries, but no too many
                    # order the data, move the time period, redo order process
                    if not noEntriesBool:
                        idaWebDataInventory(driver)

                        orderName = createOrderName(config, orderNumber, now)
                        idaWebOrder(driver, orderName)
                        orderNumber += 1

                        idaWebSummary(driver)
                        idaWebAgbs(driver)

                        # Add order to list
                        saved_documents.append(orderName)

                        # Go back to start and continue
                        since = until
                        until = getUntil(since, timeDeltaList)

                        # redo the whole order process
                        idaWebParameterPortal(driver)
                        idaWebParameterPreselection(
                            driver,
                            config.attrib['group'],
                            config.attrib['granularity'],
                            config.text
                        )
                        idaWebStationPreselection(driver)
                        idaWebTimePreselection(driver, since, until)

                    # if selection has no entries, change time period
                    else:
                        since = until
                        until = getUntil(since, timeDeltaList)
                        idaWebTimePreselection(driver, since, until)
                        if since == until:
                            notFinished = False

            # select junks manually if select all doesn't work
            else:
                idaWebDataInventoryManual(driver)
                inventoryDf = scrapeIdawebInventory(driver)
                chunks = splitDf(inventoryDf, 400)
                for chunk in chunks:
                    for value in chunk["value"]:
                        js = createJs(value)
                        driver.execute_script(js)

                orderName = createOrderName(config, orderNumber, now)
                idaWebOrder(driver, orderName)
                orderNumber += 1

                idaWebSummary(driver)
                idaWebAgbs(driver)

                # Add order to list
                saved_documents.append(orderName)

                # redo the whole order process
                idaWebParameterPortal(driver)
                idaWebParameterPreselection(
                    driver,
                    config.attrib['group'],
                    config.attrib['granularity'],
                    config.text
                )
                idaWebStationPreselection(driver)
                idaWebTimePreselection(driver, since, until)

    print(saved_documents)

    return str(saved_documents)


def scrape_idaweb_login(driver):
    """ Login into idaweb

    Args:
        driver (driver): Selenium driver
    """

    driver.get("https://gate.meteoswiss.ch/idaweb/login.do")
    
    # login data user: joel.grosjean@students.fhnw.ch password: AGEJ649GJAL02 
    # log into page
    driver.find_element_by_name('user').send_keys('joel.grosjean@students.fhnw.ch')
    driver.find_element_by_name('password').send_keys('AGEJ649GJAL02')
    driver.find_element_by_xpath(
        '//*[@id="content_block"]/form/fieldset/'
        + 'table/tbody/tr[3]/td/table/tbody/tr/td[1]/input'
    ).click()


def idaWebParameterPortal(driver):
    """ Go to parameter portal

    Args:
        driver (driver): Selenium driver
    """

    # go to parameter portal
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="menu_block"]/ul/li[5]/a').click()


def idaWebParameterPreselection(
        driver,
        searchGroup,
        searchGranularity,
        searchName):
    """ Go to parameter preselection, filter and select all

    Args:
        driver (driver): Selenium driver
        searchGroup (str): Search group (lightning, wind, ...)
        searchGranularity (str): Search granularity (D, M, ...)
        searchName (str): Parameter name
    """

    # select search parameter
    driver.find_element_by_xpath(
        f'//*[@id="paramGroup_input"]/option[@value="{searchGroup}"]'
    ).click()

    driver.find_element_by_xpath(
        f'//*[@id="granularity_input"]/option[@value="{searchGranularity}"]'
    ).click()

    driver.find_element_by_name('shortName').send_keys(searchName)

    # click search
    driver.find_element_by_xpath(
        '//*[@id="filter_actions"]/input[1]'
    ).click()

    # click select all
    driver.find_element_by_xpath(
        '//*[@id="list_actions"]/input[1]'
    ).click()


def idaWebStationPreselection(driver):
    """ Go to station preselection and select all

    Args:
        driver (driver): Selenium driver
    """

    # go to station preselection
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Station preselection")]'
    ).click()

    # click select all
    driver.find_element_by_xpath(
        '//*[@id="list_actions"]/input[1]'
    ).click()


def idaWebTimePreselection(driver, since, until):
    """ Go to web time preselection and filer

    Args:
        driver (driver): Selenium driver
        since (str): Since date
        until (str): Until date
    """

    # go to time preselection
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Time preselection")]'
    ).click()

    # clear input
    driver.find_element_by_name('since').clear()
    driver.find_element_by_name('till').clear()

    # click from and until
    driver.find_element_by_name('since').send_keys(str(since))
    driver.find_element_by_name('till').send_keys(str(until))


def idaWebDataInventoryCount(driver, tooManyEntriesBool, noEntriesBool):
    """ Count entries in inventory

    Args:
        driver (driver): Selenium driver
        tooManyEntriesBool (bool): To many entries
        noEntriesBool (bool): No entries

    Returns:
        bools: Bools with inventory result
    """

    # go to data inventory
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Data inventory")]'
    ).click()

    # get length of entries
    lengthDiv = driver.find_element_by_class_name('pager').text
    length = int(re.findall(r'\[.*\/ (\d+)\]', lengthDiv)[0])

    if length > 400:
        tooManyEntriesBool = True
    else:
        tooManyEntriesBool = False

    if length == 0:
        noEntriesBool = True
    else:
        noEntriesBool = False

    return tooManyEntriesBool, noEntriesBool


def idaWebDataInventory(driver):
    """ Go to data inventory and select all

    Args:
        driver (driver): Selenium driver
    """

    # go to data inventory
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Data inventory")]'
    ).click()

    # click select all
    driver.find_element_by_xpath(
        '//*[@id="list_actions"]/input[2]'
    ).click()


def idaWebDataInventoryManual(driver):
    """ Go to inventory and .... to be implemented

    Args:
        driver (driver): Selenium driver
    """

    # TODO implement run js here?

    # go to data inventory
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Data inventory")]'
    ).click()

    print("Here")


def idaWebOrder(driver, orderName):
    """ Go to order and order data

    Args:
        driver (driver): Selenium driver
        orderName (str): Order name
    """

    # go to order
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Order")]'
    ).click()

    # create order
    driver.find_element_by_name('orderText').send_keys(orderName)

    # change data format
    driver.find_element_by_xpath(
        '//*[@id="dataFormat_input"]/option[2]'
    ).click()

    # split delivery
    driver.find_element_by_name('split').click()


def idaWebSummary(driver):
    """ Go to summary

    Args:
        driver (driver): Selenium driver
    """

    # go to summary
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "Summary")]'
    ).click()


def idaWebAgbs(driver):
    """ Go to agbs and accepts

    Args:
        driver (driver): Selenium driver
    """

    # go to general terms and conditions
    driver.find_element_by_xpath(
        '//*[@id="wizard"]//*[contains(., "General Terms and Conditions")]'
    ).click()

    # accept general terms and conditions
    driver.find_element_by_name('acceptAgbs').click()

    # click order
    driver.find_element_by_xpath(
        '//*[@id="form_block"]/div/fieldset/table[2]/tbody/tr/td[3]'
        + '/table/tbody/tr/td/input'
    ).click()

    # click next
    driver.find_element_by_xpath(
        '//*[@id="content_block"]/form/table/tbody/tr[14]/td[2]/input'
    ).click()


def scrapeIdawebInventory(driver):
    """ Scrape data inventory for manual select

    Args:
        driver (driver): Selenium driver

    Returns:
        df: Dataframe with all tables concated
    """

    rowHeaders = [
        "station",
        "alt",
        "parameter",
        "unit",
        "granularity",
        "from",
        "until",
        "value"
    ]
    inventoryList = []
    lastPageBool = False

    while not lastPageBool:
        for row in driver.find_elements_by_xpath(
                    '//*[@id="body_block"]/form/div[4]/table/tbody/tr[*]'):
            cols = row.find_elements_by_tag_name("td")
            rowContent = [col.text for col in cols[:-1]]
            rowContent.append(
                cols[-1].find_element_by_tag_name(
                    "input"
                ).get_attribute("value")
            )
            inventoryList.append(dict(zip(rowHeaders, rowContent)))

        lastPageBool = getLastPageBool(driver, lastPageBool)
    inventoryDf = pd.DataFrame(data=inventoryList)
    inventoryDf = inventoryDf.drop_duplicates()

    return inventoryDf


def scrapeIdawebOrders(driver):
    """ Scrape made orders

    Args:
        driver (driver): Selenium driver

    Returns:
        df: Dataframe containing all orders
    """

    # TODO join to made order and only download the new ones
    # TODO if not available wait a few min
    rowHeaders = [
        "no",
        "reference",
        "orderDate",
        "status",
        "deliveryNote",
        "delivery",
        "action",
        "downloadLink"
    ]
    orderDataList = []
    lastPageBool = False

    while not lastPageBool:
        for row in driver.find_elements_by_xpath(
                    '//*[@id="body_block"]/form/div[4]/table/tbody/tr[*]'):
            rowContent = []
            for col in row.find_elements_by_tag_name("td"):
                rowContent.append(col.text)

            downloadLink = ""
            if len(row.find_elements_by_xpath('./td[6]/nobr/a')) > 0:
                downloadLink = row.find_element_by_xpath(
                    './td[6]/nobr/a'
                ).get_attribute("href")
            rowContent.append(downloadLink)
            orderDataList.append(dict(zip(rowHeaders, rowContent)))

        lastPageBool = getLastPageBool(driver, lastPageBool)

    orderDf = pd.DataFrame(data=orderDataList)

    return orderDf
