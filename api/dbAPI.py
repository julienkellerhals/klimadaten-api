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

    @dbApi.route("/table", methods=["GET", "POST"])
    def createTable():
        """ Create tables

        Returns:
            str: Table created
        """

        instance.checkEngine()
        instance.createTable()
        return "Table created"

    @dbApi.route("/etl/stage", methods=["GET", "POST"])
    def runStageETL():

        instance.checkEngine()
        instance.runStageETL()
        return "Run Stage ETL"

    @dbApi.route("/etl/stage/station", methods=["GET", "POST"])
    @dbApi.route("/etl/stage/parameter", methods=["GET", "POST"])
    def runStationParamStageETL():

        instance.checkEngine()
        instance.stationParamStageETL()
        return "Run Station parameter ETL"

    @dbApi.route("/etl/stage/idaweb", methods=["GET", "POST"])
    def runIdawebStageETL():

        instance.checkEngine()
        instance.idaWebStageETL()
        return "Run Station parameter ETL"

    @dbApi.route("/etl/core", methods=["GET", "POST"])
    def runCoreETL():

        instance.checkEngine()
        instance.runCoreETL()
        return "Run Core ETL"

    @dbApi.route("/etl/core/measurements", methods=["GET", "POST"])
    def runMeasurementsETL():

        instance.checkEngine()
        instance.runMeasurementsETL()
        return "Run Measurements ETL"

    return dbApi
