from flask import Blueprint


def constructBlueprint(announcer, instance, abstractDriver):
    dbApi = Blueprint("dbApi", __name__)

    @dbApi.route("/connect", methods=["GET", "POST"])
    def createConnection():
        """ Creates database connection

        Returns:
            str: Connected
        """

        instance.checkEngine()
        return "Connected"

    @dbApi.route("/create", methods=["GET", "POST"])
    def createDatabase():
        """ Create database

        Returns:
            str: Database created
        """

        instance.checkEngine()
        instance.createDatabase()
        return "Database created"

    @dbApi.route("/table")
    def createTable():
        """ Create tables

        Returns:
            str: Table created
        """

        instance.checkEngine()
        instance.createTable()
        return "Table created"

    @dbApi.route("/etl/core", methods=["GET", "POST"])
    def runCoreETL():

        instance.checkEngine()
        instance.runCoreETL()
        return "Run Core ETL"

    return dbApi
