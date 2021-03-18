import os
import io
import re
import zipfile
import abstractDriver
from pathlib import Path
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import Flask
from flask import request
import download
import webscraping

app = Flask(__name__)

def getDriverPath(driverfolder, browser = None):
    driverInstalledBool = False
    driverPath = ""
    for driverPath in list(driverfolder.glob('**/*.exe')):
        if browser is not None:
            if browser.lower() in driverPath.name:
                driverInstalledBool = True
                driverPath = driverPath
        else:
            driverPath = driverPath
    return driverInstalledBool, driverPath

def testGlobal():
    """
    Tests if the global variable are set.
    initiates them if they aren't. 
    """
    try:
        global driver
        driver
    except NameError:
        print("Driver not started")
        print("Starting programatically")
        print("Assuming you installed only required drivers")
        cwd = Path.cwd()
        driverfolder = cwd / "driver"
        _, driverPath = getDriverPath(driverfolder, None)
        if driverPath.name == "msedgedriver.exe":
            browser = "Edg"
        elif driverPath.name == "chromedriver.exe":
            browser = "Chrome"
        else:
            print("Browser not supported yet")
        driver = abstractDriver.createDriver(browser, driverPath, True)

    try:
        global engine
        engine
    except NameError:
        print("Engine not started")
        print("Starting programatically")
        print("Assuming you installed the database")
        engine = create_engine("postgresql://postgres:postgres@localhost:5432/klimadb", echo=True)
    

@app.route("/")
def mainPage():
    return "Load web fe"

@app.route("/api")
def api():
    return "API"

@app.route("/admin/driver/<browser>", methods=['GET'])
def createDriver(browser):
    """
    Run this function on first install to create a driver.
    """
    output = ""
    cwd = Path.cwd()
    driverFolder = cwd / "driver"
    if not driverFolder.exists():
        os.mkdir("driver")
    headlessStr = request.args['headless']

    # user agent
    userAgent = request.headers.get('User-Agent')
    output += "User agent: " + userAgent + "</br>"
    for browserVersion in userAgent.split(" "):
        if browserVersion.split("/")[0] == browser:
            version = browserVersion.split("/")[1]
    if len(version) == 0:
        # output += "Browser not found, options are - Mozilla, AppleWebKit, Chrome, Safari, Edg" + "</br>"
        output += "Browser not found, options are - Chrome, Edg" + "</br>"

    # get driver path
    driverInstalledBool, driverPath = getDriverPath(driverFolder, browser)

    # download driver
    if not driverInstalledBool:
        output += "Installing driver" + "</br>"
        if browser == "Chrome":
            browserDriverDownloadPage, _, _ = download.getRequest("https://chromedriver.chromium.org/downloads")
            pattern = r"ChromeDriver (" + version.split(".")[0] + r"\.\d*\.\d*\.\d*)"
            existingDriverVersion = re.findall(pattern, browserDriverDownloadPage.content.decode("utf-8"))[0]
            browserDriverDownloadUrl = "https://chromedriver.storage.googleapis.com/" + existingDriverVersion + "/chromedriver_win32.zip"
        elif browser == "Edg":
            browserDriverDownloadUrl = "https://msedgedriver.azureedge.net/" + version + "/edgedriver_win64.zip"
        else:
            print("Browser not supported yet")
        output += "Driver URL: " + browserDriverDownloadUrl + "</br>"
        driverRequest = download.getRequest(browserDriverDownloadUrl)[0]
        driverZip = zipfile.ZipFile(io.BytesIO(driverRequest.content))
        driverZip.extractall(driverFolder)
        output += "Downloaded and extracted driver" + "</br>"
        # get driver path
        driverInstalledBool, driverPath = getDriverPath(driverFolder, browser)
    else:
        output += "Driver already satisfied" + "</br>"

    # Convert to string
    if headlessStr.lower() == "true":
        headlessBool = True
    else:
        headlessBool = False

    # Create driver
    global driver
    driver = abstractDriver.createDriver(browser, driverPath, headlessBool)
    output += "Started Driver" + "</br>"

    return output

@app.route("/admin/refresh")
def refreshData():
    return "Run webscraping"

@app.route("/admin/test")
def getTest():
    return "hello world"

@app.route("/admin/scrape/meteoschweiz")
def scrapeMeteoschweiz():
    testGlobal() # to test if the global variable are set
    resp = webscraping.scrape_meteoschweiz(driver)
    return resp

@app.route("/admin/db/connect")
def createConnection():
    global engine
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/klimadb", echo=True)
    print(engine)
    return "Created connection"

@app.route("/admin/db/create")
def createDatabase():
    if not database_exists(engine.url): #Check if Database exists else create
        create_database(engine.url)
    if not engine.dialect.has_schema(engine, "core"): #Check if schema core exists else create
        engine.execute(sqlalchemy.schema.CreateSchema("core"))
    if not engine.dialect.has_schema(engine, "stage"): #Check if schema etl exists else create
        engine.execute(sqlalchemy.schema.CreateSchema("stage"))
    return "Database created"