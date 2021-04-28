import json
from flask import request
from flask import Blueprint
from flask import render_template


def constructBlueprint(announcer, instance, abstractDriver):
    adminApi = Blueprint("adminApi", __name__)

    @adminApi.route("/")
    def adminPage():
        """ Admin page

        Returns:
            html: Returns admin page
        """

        return render_template(
            "admin.html",
        )

    @adminApi.route("/getServiceList", methods=["POST"])
    def getServiceList():
        serviceList = {
            "runningService": {
                "1": {
                    "eventSourceUrl": "/admin/stream/getDriverPathStatus",
                    "title": "Driver name",
                    "url": "",
                    "headerBadge": {
                        "caption": "",
                        "content": "",
                    },
                    "action": [
                        {
                            "name": "Download driver",
                            "actionUrl": "",
                            "enabled": False
                        }
                    ],
                    "bodyBadge": {
                        "caption": "",
                        "content": "",
                    },
                },
                "2": {
                    "eventSourceUrl": "/admin/stream/getDriverStatus",
                    "title": "Driver status",
                    "url": "",
                    "headerBadge": {
                        "caption": "",
                        "content": "",
                    },
                    "action": [
                        {
                            "name": "Start driver",
                            "actionUrl": "",
                            "enabled": False
                        }
                    ],
                    "bodyBadge": {
                        "caption": "",
                        "content": "",
                    },
                },
                "3": {
                    "eventSourceUrl": "/admin/stream/getDatabaseStatus",
                    "title": "Database connection",
                    "url": "",
                    "headerBadge": {
                        "caption": "",
                        "content": "",
                    },
                    "action": [
                        {
                            "name": "Connect to db",
                            "actionUrl": "",
                            "enabled": False
                        },
                        {
                            "name": "Create db",
                            "actionUrl": "",
                            "enabled": False
                        }
                    ],
                    "bodyBadge": {
                        "caption": "",
                        "content": "",
                    },
                },
                "4": {
                    "eventSourceUrl": "/admin/stream/getEngineStatus",
                    "title": "Engine status",
                    "url": "",
                    "headerBadge": {
                        "caption": "",
                        "content": "",
                    },
                    "action": [
                        {
                            "name": "Start engine",
                            "actionUrl": "",
                            "enabled": False
                        }
                    ],
                    "bodyBadge": {
                        "caption": "",
                        "content": "",
                    },
                },
            }
        }
        return json.dumps(serviceList, default=str)

    @adminApi.route("/getDbServiceList", methods=["POST"])
    def getDbServiceList():
        dbServiceList = {
            "runningService": {
                "eventSourceUrl": "/admin/stream/getDbServiceStatus",
                "dbConnection": {
                    "currentAction": False,
                    "actionUrl": None,
                },
                "dbCreate": {
                    "currentAction": False,
                    "actionUrl": None,
                },
                "tbCreate": {
                    "currentAction": False,
                    "actionUrl": None,
                },
            }
        }
        return json.dumps(dbServiceList, default=str)

    @adminApi.route("/getTablesList", methods=["POST"])
    def getTablesList():
        tablesList = {
            "stage": {
                "eventSourceUrl": "/admin/stream/getStageTablesStatus",
            },
            "core": {
                "eventSourceUrl": "/admin/stream/getCoreTablesStatus",
            },
            "datamart": {
                "eventSourceUrl": "/admin/stream/getDatamartTablesStatus",
            },
        }
        return json.dumps(tablesList, default=str)

    @adminApi.route("/getEngineStatus", methods=["POST"])
    def getEngineStatus():
        """ Runs function get engine status
        """

        instance.getEngineStatus()
        return ""

    @adminApi.route("/getDatabaseStatus", methods=["POST"])
    def getDatabaseStatus():
        """ Runs function get database status
        """

        instance.getDatabaseStatus()
        return ""

    @adminApi.route("/getDriverPathStatus", methods=["POST"])
    def getDriverPathStatus():
        """ Gets driver path
        """

        abstractDriver.getDriverPathStatus()
        return ""

    @adminApi.route("/getDriverStatus", methods=["POST"])
    def getDriverStatus():
        """ Runs driver status function
        """

        abstractDriver.getDriverStatus()
        return ""

    @adminApi.route("/getStageTablesStatus", methods=["POST"])
    def getStageTablesStatus():

        instance.getStageTablesStatus()
        return ""

    @adminApi.route("/getCoreTablesStatus", methods=["POST"])
    def getCoreTablesStatus():

        instance.getStageTablesStatus()
        return ""

    @adminApi.route("/getDbServiceStatus", methods=["POST"])
    def getDbServiceStatus():

        instance.getDbServiceStatus()
        return ""

    @adminApi.route("/database")
    def databasePage():
        """ database page

        Returns:
            html: Returns database page
        """

        return render_template(
            "database.html",
        )

    @adminApi.route("/tests")
    def testsPage():
        """ Tests page

        Returns:
            html: Returns tests page
        """

        return render_template(
            "tests.html",
        )

    @adminApi.route("/doc")
    def docPage():
        """ Doc page

        Returns:
            html: Returns doc page
        """

        return render_template(
            "doc.html",
        )

    @adminApi.route("/errors")
    def errorPage():
        """ Error page

        Returns:
            html: Returns error page
        """

        return render_template(
            "error.html",
        )

    @adminApi.route("/driver/<browser>", methods=["GET"])
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

    @adminApi.route("/driver/<browser>", methods=["POST"])
    def driverInstallPost(browser):

        headlessStr = request.args['headless']
        userAgent = request.headers.get('User-Agent')

        abstractDriver.downloadDriver(browser, headlessStr, userAgent)
        return ""

    @adminApi.route("/startDriver", methods=["POST"])
    def startDriver():

        abstractDriver.checkDriver()
        return ""

    @adminApi.route("/test")
    def runTests():
        """ Return test page

        Returns:
            html: Renders html template
        """

        return render_template(
            "stream.html",
            streamUrl="/admin/stream/test"
        )

    return adminApi
