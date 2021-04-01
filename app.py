import os
import io
import re
import time
import psutil
import zipfile
import threading
import subprocess
import sqlalchemy
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
import abstractDriver
import messageAnnouncer

app = Flask(__name__)
announcer = messageAnnouncer.MessageAnnouncer()
abstractDriver = abstractDriver.AbstractDriver()
instance = db.Database()


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


@app.route("/admin/getEngineStatus", methods=["POST"])
def getEngineStatus():
    instance.getDatabaseStatus()
    return ""


@app.route("/admin/stream/getEngineStatus")
def streamEngineStatus():
    instance.getDatabaseStatus()
    return Response(
        instance.databaseStatusStream.stream(),
        mimetype='text/event-stream'
    )


@app.route("/admin/getDatabaseStatus", methods=["POST"])
def getDatabaseStatus():
    instance.getDatabaseStatus()
    return ""


@app.route("/admin/stream/getDatabaseStatus")
def streamDatabaseStatus():
    instance.getDatabaseStatus()
    return Response(
        instance.databaseStatusStream.stream(),
        mimetype='text/event-stream'
    )


@app.route("/admin/getDriverPathStatus", methods=["POST"])
def getDriverPathStatus():
    abstractDriver.getDriverPathStatus()
    return ""


@app.route("/admin/stream/getDriverPathStatus")
def streamDriverPathStatus():
    abstractDriver.getDriverPathStatus()
    return Response(
        abstractDriver.pathStatusStream.stream(),
        mimetype='text/event-stream'
    )


@app.route("/admin/getDriverStatus", methods=["POST"])
def getDriverStatus():
    abstractDriver.getDriverStatus()
    return ""


@app.route("/admin/stream/getDriverStatus")
def streamDriverStatus():
    abstractDriver.getDriverStatus()
    return Response(
        abstractDriver.driverStatusStream.stream(),
        mimetype='text/event-stream'
    )


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
        target=abstractDriver.runThreaded,
        args=(announcer, browser, headlessStr, userAgent)
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
            announcer.announce(announcer.format_sse(msgTxt))

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

    driver = abstractDriver.getDriver()
    engine = instance.engine
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

    driver = abstractDriver.getDriver()
    engine = instance.engine
    resp = webscraping.scrape_idaweb(driver, engine)
    return resp


@app.route("/admin/db/connect")
def createConnection():
    """ Creates database connection

    Returns:
        str: Connected
    """

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
