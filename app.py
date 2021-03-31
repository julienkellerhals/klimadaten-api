import os
import io
import re
import time
import psutil
import zipfile
import threading
import subprocess
import sqlalchemy
import abstractDriver
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from flask import Flask
from flask import request
from flask import render_template
from flask import Response
import db
import download
import webscraping
import messageAnnouncer

app = Flask(__name__)
announcer = messageAnnouncer.MessageAnnouncer()


def createDriver(browser, headlessStr, userAgent):
    """ Creates selenium driver for webscrapping automation
        Downloads it into driver folder if not installed

    Args:
        browser (string): Browser type (Edge, Chrome, etc.)
        headlessStr (string): Start in headless bool
        userAgent (string): Browser user agent from header
    """

    cwd = Path.cwd()
    driverFolder = cwd / "driver"
    if not driverFolder.exists():
        os.mkdir("driver")

    msgTxt = "User agent: " + userAgent + "<br>"
    msg = announcer.format_sse(data=msgTxt)
    announcer.announce(msg=msg)

    for browserVersion in userAgent.split(" "):
        if browserVersion.split("/")[0] == browser:
            version = browserVersion.split("/")[1]
    if len(version) == 0:
        # output += "Browser not found, options are -
        # Mozilla,
        # AppleWebKit,
        # Chrome,
        # Safari,
        # Edg
        msgTxt = "Error: Browser not found, options are - Chrome, Edg <br>"
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

    # get driver path
    driverInstalledBool, driverPath = getDriverPath(driverFolder, browser)

    # download driver
    if not driverInstalledBool:
        msgTxt = "Installing driver <br>"
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

        if browser == "Chrome":
            browserDriverDownloadPage, _, _ = download.getRequest(
                "https://chromedriver.chromium.org/downloads"
            )
            pattern = r"ChromeDriver (" \
                + version.split(".")[0] \
                + r"\.\d*\.\d*\.\d*)"
            existingDriverVersion = re.findall(
                pattern,
                browserDriverDownloadPage.content.decode("utf-8")
            )[0]
            browserDriverDownloadUrl = \
                "https://chromedriver.storage.googleapis.com/" \
                + existingDriverVersion \
                + "/chromedriver_win32.zip"
        elif browser == "Edg":
            browserDriverDownloadUrl = "https://msedgedriver.azureedge.net/" \
                + version \
                + "/edgedriver_win64.zip"
        else:
            print("Browser not supported yet")

        msgTxt = "Driver URL: " + browserDriverDownloadUrl + "<br>"
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

        driverRequest = download.getRequest(browserDriverDownloadUrl)[0]
        driverZip = zipfile.ZipFile(io.BytesIO(driverRequest.content))
        driverZip.extractall(driverFolder)

        msgTxt = "Downloaded and extracted driver <br>"
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

        # get driver path
        driverInstalledBool, driverPath = getDriverPath(driverFolder, browser)
    else:
        msgTxt = "Driver already satisfied <br>"
        msg = announcer.format_sse(data=msgTxt)
        announcer.announce(msg=msg)

    # Convert to string
    if headlessStr.lower() == "true":
        headlessBool = True
    else:
        headlessBool = False

    # Create driver
    global driver
    driver = abstractDriver.createDriver(browser, driverPath, headlessBool)

    msgTxt = "Started Driver <br>"
    msg = announcer.format_sse(data=msgTxt)
    announcer.announce(msg=msg)


def getDriverPath(driverFolder, browser=None):
    """ Check if driver is installed and returns path

    Args:
        driverFolder (Path): Pathlib path to driver folder
        browser (string, optional): Browser type. Defaults to None.

    Returns:
        driverInstalledBool (bool): True if driver was found
        driverPath (Path): Driver + driver name path
    """

    driverInstalledBool = False
    driverPath = ""
    for driverPath in list(driverFolder.glob('**/*.exe')):
        if browser is not None:
            if browser.lower() in driverPath.name:
                driverInstalledBool = True
                driverPath = driverPath
        else:
            driverPath = driverPath
    return driverInstalledBool, driverPath


def testGlobal():
    """ Tests if the global variable are set.
        Initiates them if they aren't.
    """

    try:
        global driver
        driver
    except NameError:
        print("Driver not started")
        print("Starting programatically")
        print("Assuming you installed only required drivers")
        cwd = Path.cwd()
        driverFolder = cwd / "driver"
        _, driverPath = getDriverPath(driverFolder, None)
        if driverPath.name == "msedgedriver.exe":
            browser = "Edg"
        elif driverPath.name == "chromedriver.exe":
            browser = "Chrome"
        else:
            print("Browser not supported yet")
        # make browser headless or not
        driver = abstractDriver.createDriver(browser, driverPath, False)

    try:
        global engine
        engine
    except NameError:
        print("Engine not started")
        print("Starting programatically")
        print("Assuming you installed the database")
        engine = create_engine(
            "postgresql://postgres:postgres@localhost:5432/klimadb",
            echo=True
        )


@app.route("/")
def mainPage():
    """ Main page

    Returns:
        str: Temp main return
    """

    return "Hello World, story will be here"


@app.route("/api")
def api():
    """ API

    Returns:
        str: Temp
    """

    return "API"


@app.route("/admin")
@app.route("/admin/")
def adminPage():
    """ Admin page

    Returns:
        html: Returns admin page
    """

    return render_template(
        "admin.html",
    )


@app.route("/admin/getEngineStatus")
def getEngineStatus():
    instance = db.Database()
    instance.runThreaded(announcer)
    return Response(announcer.stream(), mimetype='text/event-stream')


@app.route("/admin/testFunc")
def testFunc():
    # instance = db.Database()
    # instance.test(announcer)
    return Response(announcer.stream(), mimetype='text/event-stream')


@app.route("/admin/tables")
def tablesPage():
    """ Tables page

    Returns:
        html: Returns tables page
    """

    return render_template(
        "tables.html",
    )


@app.route("/admin/source")
def sourcePage():
    """ Source page

    Returns:
        html: Returns source page
    """

    return render_template(
        "source.html",
    )


@app.route("/admin/status")
def statusPage():
    """ Status page

    Returns:
        html: Returns status page
    """

    return render_template(
        "status.html",
    )


@app.route("/admin/tests")
def testsPage():
    """ Tests page

    Returns:
        html: Returns tests page
    """

    return render_template(
        "tests.html",
    )


@app.route("/admin/doc")
def docPage():
    """ Doc page

    Returns:
        html: Returns doc page
    """

    return render_template(
        "doc.html",
    )


@app.route("/admin/errors")
def errorPage():
    """ Error page

    Returns:
        html: Returns error page
    """

    return render_template(
        "error.html",
    )


@app.route("/admin/driver/<browser>")
def driver(browser):
    """ Returns driver page

    Args:
        browser (str): Browser type

    Returns:
        html: Renders html template
    """

    reqUrl = request.full_path
    streamUrl = reqUrl.replace(
        "/admin",
        "/admin/stream"
    )
    return render_template(
        "stream.html",
        streamUrl=streamUrl
    )


@app.route("/admin/stream/driver/<browser>")
def streamDriver(browser):
    """ Creates driver and data stream for driver page

    Args:
        browser (str): Browser type

    Returns:
        stream: Data stream for driver creation
    """

    headlessStr = request.args['headless']
    userAgent = request.headers.get('User-Agent')

    x = threading.Thread(
        target=createDriver,
        args=(browser, headlessStr, userAgent)
    )
    x.start()
    return Response(announcer.stream(), mimetype='text/event-stream')


@app.route("/admin/refresh")
def refreshData():
    """ Temp route

    Returns:
        str: Temp
    """

    return "Run webscraping"


@app.route("/admin/test")
def runTests():
    """ Return test page

    Returns:
        html: Renders html template
    """

    return render_template(
        "stream.html",
        streamUrl="/admin/stream/test"
    )


@app.route("/admin/stream/test")
def streamTest():
    """ Runs tests and creates data stream for tests page

    Returns:
        stream: Data stream for test runs
    """

    def runTestSubprocess():
        # TODO try to take this func out and test it
        """ Run subprocess in local thread
        """

        testNameList = [
            "meteoschweiz",
            "idaweb"
        ]
        for testName in testNameList:
            p = subprocess.Popen(
                ["pytest", "-v", "-m", testName],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            while True:
                time.sleep(2)
                proc = psutil.Process(p.pid)
                print(proc.threads())
                if len(proc.threads()) < 2:
                    proc.kill()
                    break
            out, err = p.communicate()
            msgTxt = "Testing: " + out.decode()
            msgTxt = msgTxt.replace("\r\n", "<br>")
            msg = announcer.format_sse(data=msgTxt)
            announcer.announce(msg=msg)

    x = threading.Thread(
        target=runTestSubprocess
    )
    x.start()

    return Response(announcer.stream(), mimetype='text/event-stream')


@app.route("/admin/scrape/meteoschweiz")
def scrapeMeteoschweiz():
    """ Return meteosuisse page

    Returns:
        html: Renders html template
    """

    return render_template(
        "stream.html",
        streamUrl="/admin/stream/meteoschweiz"
    )


@app.route("/admin/stream/meteoschweiz")
def streamMeteoschweiz():
    """ Runs meteo suisse scrapping process and returns stream

    Returns:
        stream: Meteosuisse stream
    """

    testGlobal()  # to test if the global variable are set
    x = threading.Thread(
        target=webscraping.scrape_meteoschweiz,
        args=(driver, engine, announcer)
    )
    x.start()

    return Response(announcer.stream(), mimetype='text/event-stream')


@app.route("/admin/scrape/idaweb")
def scrapeIdaweb():
    """ Runs idaweb scrapping

    Returns:
        str: temp
    """

    testGlobal()  # to test if the global variable are set
    resp = webscraping.scrape_idaweb(driver, engine)
    return resp


@app.route("/admin/db/connect")
def createConnection():
    """ Creates database connection

    Returns:
        str: Connected
    """

    global instance
    instance = db.Database()
    return "Connected"


@app.route("/admin/db/create")
def createDatabase():
    """ Create database

    Returns:
        str: Database created
    """

    instance.createDatabase()
    return "Database created"


@app.route("/admin/db/table")
def createTable():
    """ Create tables

    Returns:
        str: Table created
    """

    instance.createTable()
    return "Table created"
