import io
import zipfile
from pathlib import Path
import sqlalchemy
from sqlalchemy import create_engine
from flask import Flask
from flask import request
import download

app = Flask(__name__)


@app.route("/")
def mainPage():
    return "Load web fe"

@app.route("/api")
def api():
    return "API"

@app.route("/admin/driver/<browser>", methods=['GET'])
def driver(browser):
    output = ""
    cwd = Path.cwd()
    driverfolder = cwd / "driver"
    headlessBool = request.args['headless']

    # user agent
    userAgent = request.headers.get('User-Agent')
    output += "User agent: " + userAgent + "</br>"
    for browserVersion in userAgent.split(" "):
        if browserVersion.split("/")[0] == browser:
            version = browserVersion.split("/")[1]
    if len(version) == 0:
        # output += "Browser not found, options are - Mozilla, AppleWebKit, Chrome, Safari, Edg" + "</br>"
        output += "Browser not found, options are - Chrome, Edg" + "</br>"

    driverInstalledBool = False
    for driverPath in list(driverfolder.glob('**/*.exe')):
        if browser.lower() in driverPath.name:
            driverInstalledBool = True

    if not driverInstalledBool:
        # download driver
        output += "Installing driver" + "</br>"
        browserDriverConf = {
            "Edg": "https://msedgedriver.azureedge.net/" + version + "/edgedriver_win64.zip",
            "Chrome": "https://chromedriver.storage.googleapis.com/" + version + "/chromedriver_win32.zip"
        }
        output += "Driver URL: " + browserDriverConf[browser] + "</br>"
        driverRequest = download.getRequest(browserDriverConf[browser])[0]
        driverZip = zipfile.ZipFile(io.BytesIO(driverRequest.content))
        driverZip.extractall(driverfolder)
        output += "Downloaded and extracted driver" + "</br>"
    else:
        output += "Driver already satisfied" + "</br>"

    return output

@app.route("/admin/refresh")
def refreshData():
    return "Run webscraping"

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