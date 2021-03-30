import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge


def createDriver(browser, driverPath, headless):
    """ Start selenium web driver

    Args:
        browser (str): Browser type
        driverPath (Path): Path to driver
        headless (bool): Headless bool

    Returns:
        driver: selenium driver
    """

    if browser == "Edg":
        edge_options = EdgeOptions()
        if headless:
            # make Edge headless
            edge_options.use_chromium = True
            edge_options.add_argument("headless")
            edge_options.add_argument("disable-gpu")
            edge_options.add_argument("--log-level=3")
            edge_options.add_experimental_option(
                'excludeSwitches',
                ['enable-logging']
            )
            # edge_options.page_load_strategy("eager")
        driver = Edge(
            executable_path=str(driverPath),
            options=edge_options
        )
    elif browser == "Chrome":
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_experimental_option(
                'excludeSwitches',
                ['enable-logging']
            )
            # chrome_options.page_load_strategy("eager")
            # don't know the chrome command
        driver = webdriver.Chrome(
            executable_path=str(driverPath),
            options=chrome_options
        )
    else:
        print("Browser not supported yet")

    driver.set_window_size(1800, 1080)
    driver.set_page_load_timeout(100000)

    return driver
