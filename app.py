import io
import re
import zipfile
import abstractDriver
from pathlib import Path
import sqlalchemy
from sqlalchemy import create_engine
from flask import Flask
from flask import request
import download

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

def testDriver():
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

@app.route("/")
def mainPage():
    return "Load web fe"

@app.route("/api")
def api():
    return "API"

@app.route("/admin/driver/<browser>", methods=['GET'])
def createDriver(browser):
    output = ""
    cwd = Path.cwd()
    driverfolder = cwd / "driver"
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
    driverInstalledBool, driverPath = getDriverPath(driverfolder, browser)

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
        driverZip.extractall(driverfolder)
        output += "Downloaded and extracted driver" + "</br>"
        # get driver path
        driverInstalledBool, driverPath = getDriverPath(driverfolder, browser)
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
    testDriver()

    driver.get("https://www.meteoschweiz.admin.ch/home/klima/schweizer-klima-im-detail/homogene-messreihen-ab-1864.html?region=Tabelle")
    url_list = []
    urls = driver.find_elements_by_xpath("//table[@id='stations-table']/tbody/tr/td/span[@class='overflow']/a")
    for url in urls:
        url_list.append(url.get_attribute('href'))
    
    resp = "Got following urls" + "</br>"
    for url in url_list:
        resp += url + "</br>"
    return resp

@app.route("/admin/homog")
def getHomog():
    content = download.getData()
    # write data to database in etl schema
    return content.content

@app.route("/admin/db/create")
def createConnection():
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/klimadb", echo=True)
    print(engine)
    return "Created connection"