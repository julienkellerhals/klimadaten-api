from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from msedge.selenium_tools import EdgeOptions
from msedge.selenium_tools import Edge

def createDriver(browser, driverPath, headless):
    if browser == "Edg":
        edge_options = EdgeOptions()
        if headless:
            # make Edge headless
            edge_options.use_chromium = True
            edge_options.add_argument('headless')
            edge_options.add_argument('disable-gpu')
        driver = Edge(executable_path=driverPath, options=edge_options)
    elif browser == "Chrome":
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path=driverPath, options=chrome_options)
    else:
        print("Browser not supported yet")

    driver.set_window_size(1800, 1080)

    return driver
