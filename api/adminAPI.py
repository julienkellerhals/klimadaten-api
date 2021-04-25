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

    @adminApi.route("/getTablesStatus", methods=["POST"])
    def getTablesStatus():
        """ Runs function get database status
        """

        instance.getTablesStatus()
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

    @adminApi.route("/driver/<browser>")
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
