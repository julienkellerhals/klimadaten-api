import pandas as pd
from flask import Blueprint
import webscraping


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
        return "Run Idaweb ETL"

    @dbApi.route("/etl/stage/increment/idaweb", methods=["GET", "POST"])
    def runIdawebIncrementStageETL():
        engine = instance.getEngine()
        driver = abstractDriver.getDriver()
        paramRefreshDateDf = instance.getParameterRefreshDate()
        configList = instance.readConfig(instance.configFileName)
        configDf = pd.DataFrame(
            [x.text for x in configList],
            columns=["meas_name"]
        )
        configDf["valid_from"] = None
        paramRefreshDateDf = pd.merge(
            paramRefreshDateDf,
            configDf,
            how="outer",
            on=["meas_name"],
            suffixes=("", "_y")
        )
        del paramRefreshDateDf["valid_from_y"]
        if not paramRefreshDateDf.empty:
            # savedDocumentsDf = webscraping._scrape_idaweb(
            #     driver,
            #     engine,
            #     paramRefreshDateDf
            # )
            # instance.idaWebStageETL(savedDocumentsDf)
            instance.idaWebStageETL()
        return "Run Idaweb increment ETL"

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

    @dbApi.route("/etl/core/station", methods=["GET", "POST"])
    def runStationETL():

        instance.checkEngine()
        instance.stationCoreETL()
        return "Run Station ETL"

    @dbApi.route("/etl/core/parameter", methods=["GET", "POST"])
    def runParameterETL():

        instance.checkEngine()
        instance.parameterCoreETL()
        return "Run Parameter ETL"

    @dbApi.route(
        "/update/<string:station_name>/<int:elevation>",
        methods=["PATCH"]
    )
    def updateStationHeight(station_name, elevation):

        instance.checkEngine()
        instance.updateStageStation(station_name, elevation)
        return "Update station elevation in stage"

    @dbApi.route(
        "/delete/<string:station_name>",
        methods=["DELETE"]
    )
    def deleteStation(station_name):

        instance.checkEngine()
        instance.deleteStageStation(station_name)
        return "Delete station in stage"

    return dbApi
