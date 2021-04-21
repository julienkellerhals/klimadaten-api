import threading
import subprocess
from flask import request
from flask import Response
from flask import Blueprint
import webscraping


def constructBlueprint(announcer, instance, abstractDriver):
    streamApi = Blueprint("streamApi", __name__)

    @streamApi.route("/eventLog")
    def streamEventLog():
        """ Create event log stream

        Returns:
            stream: announcer stream
        """

        return Response(
            announcer.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/getEngineStatus")
    def streamEngineStatus():
        """ Stream engine status

        Returns:
            stream: engine status stream
        """

        instance.getEngineStatus()
        return Response(
            instance.engineStatusStream.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/getDatabaseStatus")
    def streamDatabaseStatus():
        """ Stream database status

        Returns:
            stream: database status stream
        """

        instance.getDatabaseStatus()
        return Response(
            instance.databaseStatusStream.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/getTablesStatus")
    def streamTablesStatus():
        instance.getTablesStatus()
        return Response(
            instance.tablesStatusStream.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/getDriverPathStatus")
    def streamDriverPathStatus():
        """ Stream driver path status

        Returns:
            stream: path status stream
        """

        abstractDriver.getDriverPathStatus()
        return Response(
            abstractDriver.pathStatusStream.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/getDriverStatus")
    def streamDriverStatus():
        """ Stream driver status

        Returns:
            stream: driver status stream
        """

        abstractDriver.getDriverStatus()
        return Response(
            abstractDriver.driverStatusStream.stream(),
            mimetype='text/event-stream'
        )

    @streamApi.route("/driver/<browser>")
    def streamDriver(browser):
        """ Creates driver and data stream for driver page

        Args:
            browser (str): Browser type

        Returns:
            stream: Data stream for driver creation
        """

        headlessStr = request.args['headless']
        userAgent = request.headers.get('User-Agent')

        abstractDriver.downloadDriver(browser, headlessStr, userAgent)

        return Response(announcer.stream(), mimetype='text/event-stream')

    @streamApi.route("/test")
    def streamTest():
        """ Runs tests and creates data stream for tests page

        Returns:
            stream: Data stream for test runs
        """

        def runTestSubprocess():
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
                    stderr=subprocess.PIPE,
                    shell=False
                )
                out, _ = p.communicate()
                msgTxt = "Testing: " + out.decode()
                msgTxt = msgTxt.replace("\r\n", "<br>")
                announcer.announce(announcer.format_sse(msgTxt))

        x = threading.Thread(
            target=runTestSubprocess
        )
        x.start()

        return Response(announcer.stream(), mimetype='text/event-stream')

    @streamApi.route("/meteoschweiz")
    def streamMeteoschweiz():
        """ Runs meteo suisse scrapping process and returns stream

        Returns:
            stream: Meteosuisse stream
        """

        driver = abstractDriver.getDriver()
        engine = instance.getEngine()
        x = threading.Thread(
            target=webscraping.scrape_meteoschweiz,
            args=(driver, engine, announcer)
        )
        x.start()

        return Response(announcer.stream(), mimetype='text/event-stream')

    @streamApi.route("/idaweb")
    def streamIdaWeb():
        driver = abstractDriver.getDriver()
        engine = instance.getEngine()
        x = threading.Thread(
            target=webscraping.scrape_idaweb,
            args=(driver, engine)
        )
        x.start()

        return Response(announcer.stream(), mimetype='text/event-stream')

    return streamApi
