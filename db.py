import re
import json
import threading
import sqlalchemy
import numpy as np
import pandas as pd
from lxml import etree
from pathlib import Path
from sqlalchemy import inspect
from sqlalchemy import MetaData, create_engine
from sqlalchemy import Table, Column, Integer, String, Float, Date
from sqlalchemy_utils import database_exists, create_database
import messageAnnouncer


class Database:
    """ Database functions
    """

    engine = None
    conn = None
    databaseUrl = "postgresql://postgres:postgres@localhost:5432/klimadb"
    meta = MetaData()
    announcer = None
    databaseStatusStream = None
    engineStatusStream = None
    stageTablesStatusStream = None
    coreTablesStatusStream = None
    datamartTablesStatusStream = None
    dbServiceStatusStream = None

    def __init__(self, announcer):
        """ Init engine
        """

        self.databaseStatusStream = messageAnnouncer.MessageAnnouncer()
        self.engineStatusStream = messageAnnouncer.MessageAnnouncer()
        self.stageTablesStatusStream = messageAnnouncer.MessageAnnouncer()
        self.coreTablesStatusStream = messageAnnouncer.MessageAnnouncer()
        self.datamartTablesStatusStream = messageAnnouncer.MessageAnnouncer()
        self.dbServiceStatusStream = messageAnnouncer.MessageAnnouncer()
        self.announcer = announcer

    def readConfig(self, configFileName):
        """ Read config file

        Args:
            configFileName (str): config file name

        Returns:
            list: Configuration in config file
        """

        configList = []

        tree = etree.parse(configFileName)
        root = tree.getroot()
        for config in root:
            configList.append(config)
        return configList

    def getEngine(self):
        self.checkEngine()
        return self.engine

    def checkEngine(self):
        if self.engine is None:
            print("Engine not started")
            print("Starting programatically")
            print("Assuming you installed database")
            self.createEngine()

    def createEngine(self):
        self.engine = create_engine(
            self.databaseUrl,
            echo=True
        )

    def getDbServiceStatus(self):
        x = threading.Thread(
            target=self._getDbServiceStatus
        )
        x.start()

    def _getDbServiceStatus(self):
        respDict = {
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

        if self.engine is None:
            respDict["runningService"][
                "dbConnection"
            ]["currentAction"] = True
            respDict["runningService"][
                "dbConnection"
            ]["actionUrl"] = "/admin/db/connect"
            msgText = json.dumps(
                respDict,
                default=str
            )
        else:
            respDict["runningService"]["dbConnection"]["currentAction"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        self.dbServiceStatusStream.announce(
            self.dbServiceStatusStream.format_sse(msgText)
        )

        try:
            create_engine(
                self.databaseUrl
            ).connect()
        except sqlalchemy.exc.OperationalError:
            try:
                database_exists(self.databaseUrl)
            except sqlalchemy.exc.OperationalError:
                respDict["runningService"][
                    "dbConnection"
                ]["currentAction"] = True
                respDict["runningService"][
                    "dbConnection"
                ]["actionUrl"] = "/admin/db/connect"
                msgText = json.dumps(
                    respDict,
                    default=str
                )
            else:
                respDict["runningService"][
                    "dbCreate"
                ]["currentAction"] = True
                respDict["runningService"][
                    "dbCreate"
                ]["actionUrl"] = "/admin/db/create"
                msgText = json.dumps(
                    respDict,
                    default=str
                )
        else:
            respDict["runningService"]["dbCreate"]["currentAction"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        finally:
            self.dbServiceStatusStream.announce(
                self.dbServiceStatusStream.format_sse(msgText)
            )

        try:
            inspector = inspect(self.engine)
        except sqlalchemy.exc.NoInspectionAvailable:
            respDict["runningService"]["dbCreate"]["currentAction"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        except sqlalchemy.exc.OperationalError:
            respDict["runningService"]["dbCreate"]["currentAction"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        else:
            self.conn = self.engine.connect()

            stageTables = inspector.get_table_names("stage")
            coreTables = inspector.get_table_names("core")
            if len(stageTables) > 0 or len(coreTables) > 0:
                respDict["runningService"]["tbCreate"]["currentAction"] = False
                respDict["runningService"]["tbCreate"]["dbReady"] = True
                msgText = json.dumps(
                    respDict,
                    default=str
                )
            else:
                respDict["runningService"][
                    "tbCreate"
                ]["currentAction"] = True
                respDict["runningService"][
                    "tbCreate"
                ]["actionUrl"] = "/admin/db/table"
                msgText = json.dumps(
                    respDict,
                    default=str
                )
        finally:
            self.dbServiceStatusStream.announce(
                    self.dbServiceStatusStream.format_sse(msgText)
                )

    def getDatabaseStatus(self):
        x = threading.Thread(
            target=self._getDatabaseStatus
        )
        x.start()

    def _getDatabaseStatus(self):
        respDict = {
            "status": 0,
            "eventSourceUrl": "/admin/stream/getDatabaseStatus",
            "title": "Database connection",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Connect to db",
                    "actionUrl": "http://localhost:5000/admin/db/connect",
                    "enabled": True
                },
                {
                    "name": "Create db",
                    "actionUrl": "http://localhost:5000/admin/db/create",
                    "enabled": True
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        }
        errorIcon = '<i class="material-icons">error</i>'

        try:
            create_engine(
                self.databaseUrl
            ).connect()
        except sqlalchemy.exc.OperationalError as e:
            try:
                database_exists(self.databaseUrl)
            except sqlalchemy.exc.OperationalError as e:
                respDict["status"] = 2
                respDict["headerBadge"]["caption"] = "Database not started"
                respDict["headerBadge"]["content"] = errorIcon
                respDict["action"][0]["enabled"] = True
                respDict["action"][1]["enabled"] = False
                respDict["bodyBadge"]["caption"] = str(e)
                respDict["bodyBadge"]["content"] = errorIcon
                msgText = json.dumps(
                    respDict,
                    default=str
                )
                self.databaseStatusStream.announce(
                    self.databaseStatusStream.format_sse(msgText)
                )
            else:
                respDict["status"] = 1
                respDict["headerBadge"]["caption"] = "Database not created"
                respDict["headerBadge"]["content"] = errorIcon
                respDict["action"][0]["enabled"] = False
                respDict["action"][1]["enabled"] = True
                respDict["bodyBadge"]["caption"] = str(e)
                respDict["bodyBadge"]["content"] = errorIcon
                msgText = json.dumps(
                    respDict,
                    default=str
                )
        else:
            respDict["status"] = 0
            respDict["headerBadge"]["caption"] = "connection"
            respDict["headerBadge"]["content"] = str(self.databaseUrl)
            respDict["action"][0]["enabled"] = False
            respDict["action"][1]["enabled"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        finally:
            self.databaseStatusStream.announce(
                self.databaseStatusStream.format_sse(msgText)
            )

    def getEngineStatus(self):
        x = threading.Thread(
            target=self._getEngineStatus
        )
        x.start()

    def _getEngineStatus(self):
        respDict = {
            "status": 0,
            "eventSourceUrl": "/admin/stream/getEngineStatus",
            "title": "Engine status",
            "headerBadge": {
                "caption": "",
                "content": "",
            },
            "action": [
                {
                    "name": "Start engine",
                    "actionUrl": "http://localhost:5000/admin/db/connect",
                    "enabled": True
                }
            ],
            "bodyBadge": {
                "caption": "",
                "content": "",
            },
        }
        errorIcon = '<i class="material-icons">error</i>'

        if self.engine is None:
            respDict["status"] = 1
            respDict["headerBadge"]["caption"] = "Engine not started"
            respDict["headerBadge"]["content"] = errorIcon
            respDict["bodyBadge"]["caption"] = "Connect to db"
            respDict["bodyBadge"]["content"] = errorIcon

            msgText = json.dumps(
                respDict,
                default=str
            )
        else:
            respDict["status"] = 0
            respDict["headerBadge"]["content"] = "Engine started"
            respDict["action"][0]["enabled"] = False
            msgText = json.dumps(
                respDict,
                default=str
            )
        self.engineStatusStream.announce(
            self.engineStatusStream.format_sse(msgText)
        )

    def getStageTablesStatus(self):
        x = threading.Thread(
            target=self._getStageTablesStatus
        )
        x.start()

    def _getStageTablesStatus(self):
        respDict = {
            "stage": {
                "eventSourceUrl": "/admin/stream/getStageTablesStatus",
            }
        }
        inspector = inspect(self.engine)
        stageTables = inspector.get_table_names("stage")
        for stageTable in stageTables:
            respDict["stage"][stageTable] = {}
            respDict["stage"][stageTable]["title"] = stageTable

            nrowQuery = "SELECT count(*) FROM stage.{}".format(stageTable)
            respDict["stage"][stageTable]["headerBadge"] = {}
            respDict["stage"][stageTable]["headerBadge"]["caption"] = "rows"
            respDict["stage"][stageTable]["headerBadge"]["content"] = \
                "{:,}".format(self.conn.execute(
                    nrowQuery
                ).first()[0])

            actionList = []

            if stageTable == "idaweb_t":
                actionDict = {}
                actionDict["name"] = "Initial load"
                actionDict["actionUrl"] = "/admin/db/etl/stage/idaweb"
                actionDict["enabled"] = True
                actionList.append(actionDict)
                actionDict = {}
                actionDict["name"] = "Increment load"
                actionDict["actionUrl"] = \
                    "/admin/db/etl/stage/increment/idaweb"
                actionDict["enabled"] = True
                actionList.append(actionDict)
                actionDict = {}
                actionDict["name"] = "Run scrapping"
                actionDict["actionUrl"] = "/admin/scrape/idaweb"
                actionDict["enabled"] = True
                actionList.append(actionDict)
            elif stageTable == "meteoschweiz_t":
                actionDict = {}
                actionDict["name"] = "Run scrapping"
                actionDict["actionUrl"] = "/admin/scrape/meteoschweiz"
                actionDict["enabled"] = True
                actionList.append(actionDict)
            elif stageTable == "station_t":
                actionDict = {}
                actionDict["name"] = "Initial load"
                actionDict["actionUrl"] = "/admin/etl/stage/station"
                actionDict["enabled"] = True
                actionList.append(actionDict)
            elif stageTable == "parameter_t":
                actionDict = {}
                actionDict["name"] = "Initial load"
                actionDict["actionUrl"] = "/admin/etl/stage/parameter"
                actionDict["enabled"] = True
                actionList.append(actionDict)

            respDict["stage"][stageTable]["action"] = actionList

            if stageTable == "meteoschweiz_t":
                lastRefreshQuery = \
                    "SELECT max(load_date) FROM stage.{}".format(
                        stageTable
                    )
            else:
                lastRefreshQuery = \
                    "SELECT max(valid_from) FROM stage.{}".format(
                        stageTable
                    )

            respDict["stage"][stageTable]["bodyBadge"] = {}
            lastRefresh = self.conn.execute(
                lastRefreshQuery
            ).first()[0]
            if lastRefresh is not None:
                respDict["stage"][stageTable]["bodyBadge"]["caption"] = \
                    "last refresh"
                respDict["stage"][stageTable]["bodyBadge"]["content"] = \
                    lastRefresh

        msgText = json.dumps(
            respDict,
            default=str
        )
        self.stageTablesStatusStream.announce(
            self.stageTablesStatusStream.format_sse(msgText)
        )

    def getCoreTablesStatus(self):
        x = threading.Thread(
            target=self._getCoreTablesStatus
        )
        x.start()

    def _getCoreTablesStatus(self):
        respDict = {
            "core": {
                "eventSourceUrl": "/admin/stream/getCoreTablesStatus",
            }
        }
        inspector = inspect(self.engine)
        coreTables = inspector.get_table_names("core")
        for coreTable in coreTables:
            if "temp_" not in coreTable:
                respDict["core"][coreTable] = {}
                respDict["core"][coreTable]["title"] = coreTable

                nrowQuery = "SELECT count(*) FROM core.{}".format(coreTable)
                respDict["core"][coreTable]["headerBadge"] = {}
                respDict["core"][coreTable]["headerBadge"]["caption"] = "rows"
                respDict["core"][coreTable]["headerBadge"]["content"] = \
                    "{:,}".format(self.conn.execute(
                        nrowQuery
                    ).first()[0])

                actionList = []

                actionDict = {}
                actionDict["name"] = "Load"
                actionDict["actionUrl"] = \
                    "/admin/db/etl/core/" + coreTable.strip("_t")
                actionDict["enabled"] = True
                actionList.append(actionDict)

                respDict["core"][coreTable]["action"] = actionList

                lastRefreshQuery = \
                    "SELECT max(valid_from) FROM core.{}".format(
                        coreTable
                    )

                respDict["core"][coreTable]["bodyBadge"] = {}
                lastRefresh = self.conn.execute(
                    lastRefreshQuery
                ).first()[0]
                if lastRefresh is not None:
                    respDict["core"][coreTable]["bodyBadge"]["caption"] = \
                        "last refresh"
                    respDict["core"][coreTable]["bodyBadge"]["content"] = \
                        lastRefresh

        msgText = json.dumps(
            respDict,
            default=str
        )
        self.coreTablesStatusStream.announce(
            self.coreTablesStatusStream.format_sse(msgText)
        )

    def getParameterRefreshDate(self):
        paramRefreshDateDf = pd.read_sql(
            "SELECT "
            "meas_name, "
            "max(valid_from) AS valid_from "
            "FROM core.measurements_t "
            "WHERE source = 'IdaWeb' "
            "GROUP BY meas_name",
            self.engine
        )
        return paramRefreshDateDf

    def createDatabase(self):
        """ Creates database
        """

        if not database_exists(
            self.engine.url
        ):  # Check if Database exists else create
            create_database(self.engine.url)
        if not self.engine.dialect.has_schema(
            self.engine,
            'core'
        ):  # Check if schema core exists else create
            self.engine.execute(sqlalchemy.schema.CreateSchema('core'))
        if not self.engine.dialect.has_schema(
            self.engine,
            'stage'
        ):  # Check if schema etl exists else create
            self.engine.execute(sqlalchemy.schema.CreateSchema('stage'))

    def createTable(self):
        """ Creates tables
        """

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='meteoschweiz_t',
            schema='stage'
        ):
            self.meteoschweiz_t = Table(
                'meteoschweiz_t',
                self.meta,
                Column('year', Integer),
                Column('month', Integer),
                Column('station', String),
                Column('temperature', Float),
                Column('precipitation', Float),
                Column("load_date", Date, index=True),
                schema='stage')

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='idaweb_t',
            schema='stage'
        ):
            self.idaweb_t = Table(
                'idaweb_t',
                self.meta,
                Column('meas_date', Date),
                Column('station', String),
                Column('granularity', String),
                Column('meas_name', String),
                Column('meas_value', Float),
                Column('source', String),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date),
                schema='stage')

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='station_t',
            schema='stage'
        ):
            self.station_t = Table(
                'station_t',
                self.meta,
                Column('station_short_name', String),
                Column('station_name', String),
                Column('parameter', String),
                Column('data_source', String),
                Column('longitude', String),
                Column('latitude', String),
                Column('coordinates_x', Integer),
                Column('coordinates_y', Integer),
                Column('elevation', Integer),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date),
                schema='stage')

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='parameter_t',
            schema='stage'
        ):
            self.parameter_t = Table(
                'parameter_t',
                self.meta,
                Column('parameter', String),
                Column('unit', String),
                Column('description', String),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date),
                schema='stage')

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='measurements_t',
            schema='core'
        ):
            self.measurements_t = Table(
                'measurements_t',
                self.meta,
                Column('meas_date', Date, primary_key=True),
                Column('station', String, primary_key=True),
                Column('granularity', String, primary_key=True),
                Column('meas_name', String, primary_key=True),
                Column('meas_value', Float),
                Column('source', String, primary_key=True),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date, primary_key=True),
                schema='core')

        self.conn.execute(
            "CREATE MATERIALIZED VIEW core.measurements_count_mv" +
            "AS SELECT count(*) FROM core.measurements_t"
        )

        self.conn.execute(
            "CREATE MATERIALIZED VIEW core.measurements_max_valid_from_mv" +
            "AS SELECT max(valid_from) FROM core.measurements_t"
        )

        self.conn.execute(
            "CREATE OR REPLACE FUNCTION core.refresh_meas_t_fn() " +
            "RETURNS TRIGGER LANGUAGE plpgsql " +
            "AS $$ " +
            "BEGIN " +
            "REFRESH MATERIALIZED VIEW CONCURRENTLY core.measurements_count_mv; " +
            "REFRESH MATERIALIZED VIEW CONCURRENTLY core.measurements_max_valid_from_mv; " +
            "RETURN NULL; " +
            "END $$; " +
            "CREATE TRIGGER refresh_meas_t " +
            "AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE " +
            "ON core.measurements_t " +
            "FOR EACH STATEMENT " +
            "EXECUTE PROCEDURE core.refresh_meas_t_fn();"
        )

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='station_t',
            schema='core'
        ):
            self.station_t = Table(
                'station_t',
                self.meta,
                Column('station_short_name', String, primary_key=True),
                Column('station_name', String, primary_key=True),
                Column('parameter', String, primary_key=True),
                Column('data_source', String, primary_key=True),
                Column('longitude', String, primary_key=True),
                Column('latitude', String, primary_key=True),
                Column('coordinates_x', Integer, primary_key=True),
                Column('coordinates_y', Integer, primary_key=True),
                Column('elevation', Integer, primary_key=True),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date, primary_key=True),
                schema='core')

        if not self.engine.dialect.has_table(
            connection=self.engine,
            table_name='parameter_t',
            schema='core'
        ):
            self.parameter_t = Table(
                'parameter_t',
                self.meta,
                Column('parameter', String, primary_key=True),
                Column('unit', String, primary_key=True),
                Column('description', String, primary_key=True),
                Column("valid_from", Date, index=True),
                Column("valid_to", Date, primary_key=True),
                schema='core')

        self.meta.create_all(self.engine)

    def runStageETL(self):
        self.stationParamStageETL()
        self.idaWebStageETL()

    def stationParamStageETL(self):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "TRUNCATE TABLE stage.station_t;"
        )
        self.conn.execute(
            "TRUNCATE TABLE stage.parameter_t;"
        )

        configFileName = "idawebConfig.xml"
        configList = self.readConfig(configFileName)
        for config in configList:
            stationPartDf = pd.DataFrame()
            parameterPartDf = pd.DataFrame()
            dataDir = Path.cwd() / "data"
            legendFiles = dataDir.glob(
                "**/*_{}_*legend.txt".format(config.text)
            )
            for legendFilePath in legendFiles:
                with open(legendFilePath, 'r') as legendFile:
                    print(legendFilePath.stem)
                    legendFileList = legendFile.readlines()
                    rawStationRow = legendFileList[31]
                    longLat = re.findall(
                        r"\d*°\d*'\/\d*°\d*'",
                        rawStationRow
                    )
                    if type(longLat) is list:
                        longLat = longLat[0]
                    corr = re.findall(
                        r"\d+\/\d+",
                        rawStationRow
                    )
                    if type(corr) is list:
                        if len(corr) > 0:
                            corr = corr[0]
                        else:
                            corr = re.findall(
                                r"\d+\/\d+|-\/-",
                                rawStationRow
                            )
                            if corr == ["-/-"]:
                                corr = "0/0"
                    idx = re.search(
                        r"\d+\/\d+|-\/-",
                        rawStationRow
                    ).span()[1] + 1
                    stationDict = {
                        "station_short_name": rawStationRow[0:10].strip(),
                        "station_name": rawStationRow[10:47].strip(),
                        "parameter": rawStationRow[47:63].strip(),
                        "data_source": rawStationRow[64:115].strip(),
                        "longitude": longLat.split("/")[0],
                        "latitude": longLat.split("/")[1],
                        "coordinates_x": int(corr.split("/")[0]),
                        "coordinates_y": int(corr.split("/")[1]),
                        "elevation": int(rawStationRow[idx:].strip())
                    }
                    stationPartDf = stationPartDf.append(
                        stationDict,
                        ignore_index=True
                    )
                    rawParameterRow = legendFileList[36]
                    parameterDict = {
                        "parameter": rawParameterRow[0:10].strip(),
                        "unit": rawParameterRow[10:47].strip(),
                        "description": rawParameterRow[47:].strip()
                    }
                    parameterPartDf = parameterPartDf.append(
                        parameterDict,
                        ignore_index=True
                    )

            stationPartDf["valid_from"] = pd.datetime.now().date()
            stationPartDf["valid_to"] = pd.to_datetime("2262-04-11").date()
            stationPartDf.to_sql(
                'station_t',
                self.engine,
                schema='stage',
                if_exists='append',
                index=False
            )
            parameterPartDf["valid_from"] = pd.datetime.now().date()
            parameterPartDf["valid_to"] = pd.to_datetime("2262-04-11").date()
            parameterPartDf.to_sql(
                'parameter_t',
                self.engine,
                schema='stage',
                if_exists='append',
                index=False
            )

    def idaWebStageETL(self, orderList=["*"]):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "TRUNCATE TABLE stage.idaweb_t;"
        )

        configFileName = "idawebConfig.xml"
        configList = self.readConfig(configFileName)
        for config in configList:
            idaWebPartDf = pd.DataFrame()
            dataDir = Path.cwd() / "data"
            if type(orderList) is pd.DataFrame:
                orderList = orderList["no"]
            for order in orderList:
                dataFiles = dataDir.glob(
                    "**/order_{}_*_{}_*_data.txt".format(order, config.text)
                )
                print(config.text)
                for dataFile in dataFiles:
                    print(dataFile.stem)
                    dataFileDf = pd.read_csv(dataFile, sep=";")
                    shortName = dataFileDf.columns[-1]
                    dataFileDf.rename(
                        columns={
                            "stn": "station",
                            "time": "meas_date"
                        },
                        inplace=True
                    )
                    dataFileDf["valid_to"] = pd.to_datetime("2262-04-11")
                    dataFileDf["source"] = "IdaWeb"
                    dataFileDf["granularity"] = config.attrib['granularity']
                    if config.attrib['granularity'] == "M":
                        dataFileDf["meas_date"] = pd.to_datetime(
                            dataFileDf["meas_date"].map(str) + "01",
                            format="%Y%m%d"
                        )
                    elif config.attrib['granularity'] == "D":
                        dataFileDf["meas_date"] = pd.to_datetime(
                            dataFileDf["meas_date"],
                            format="%Y%m%d"
                        )
                    else:
                        NotImplementedError()
                    dataFileDf = pd.melt(
                        dataFileDf,
                        id_vars=[
                            "station",
                            "valid_to",
                            "meas_date",
                            "granularity",
                            "source"
                        ],
                        value_vars=[shortName],
                        var_name="meas_name",
                        value_name="meas_value"
                    )
                    idaWebPartDf = idaWebPartDf.append(dataFileDf)
            validFromDf = idaWebPartDf.groupby(
                ["meas_name"]
            ).agg(valid_from=("meas_date", np.max))
            idaWebPartDf = idaWebPartDf.merge(
                validFromDf,
                on="meas_name",
                how="outer"
            )
            idaWebPartDf["meas_value"].replace("-", np.NaN, inplace=True)
            idaWebPartDf.to_sql(
                'idaweb_t',
                self.engine,
                schema='stage',
                if_exists='append',
                index=False
            )

    def runCoreETL(self):
        self.runMeasurementsETL()

    def runMeasurementsETL(self):
        self.meteoschweizCoreETL()
        self.idawebCoreETL()

    def meteoschweizCoreETL(self):
        meteoschweizDf = pd.read_sql_table(
            "meteoschweiz_t",
            self.engine,
            schema="stage"
        )

        meteoschweizDf["meas_date"] = pd.to_datetime(
            meteoschweizDf["year"].map(str)
            + "." + meteoschweizDf["month"].map(str)
            + ".01",
            format="%Y.%m.%d"
        )

        meteoschweizDf["granularity"] = "M"
        meteoschweizDf["source"] = "meteoschweiz"
        meteoschweizDf.rename(
            columns={"load_date": "valid_from"},
            inplace=True
        )
        meteoschweizDf["valid_to"] = pd.to_datetime("2262-04-11")
        del meteoschweizDf['year']
        del meteoschweizDf['month']
        meteoschweizDf = pd.melt(
            meteoschweizDf,
            id_vars=[
                "station",
                "valid_from",
                "valid_to",
                "meas_date",
                "granularity",
                "source"
            ],
            value_vars=[
                "temperature",
                "precipitation"
            ],
            var_name="meas_name",
            value_name="meas_value"
        )
        meteoschweizDf.to_sql(
            'temp_measurements_t',
            self.engine,
            schema='core',
            if_exists='append',
            index=False,
            dtype={
                "meas_date": Date,
                "station": String,
                "granularity": String,
                "meas_name": String,
                "meas_value": Float,
                "source": String,
                "valid_from": Date,
                "valid_to": Date
            }
        )

        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "INSERT INTO core.measurements_t " +
            "SELECT " +
            "meas_date, " +
            "station, " +
            "granularity, " +
            "meas_name, " +
            "meas_value, " +
            "source, " +
            "valid_from, " +
            "valid_to " +
            "FROM core.temp_measurements_t " +
            "ON CONFLICT DO NOTHING;"
        )
        self.conn.execute(
            "DROP TABLE IF EXISTS core.temp_measurements_t;"
        )

    def stationCoreETL(self):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "INSERT INTO core.station_t " +
            "SELECT * FROM stage.station_t " +
            "ON CONFLICT DO NOTHING;"
        )

    def parameterCoreETL(self):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "INSERT INTO core.parameter_t " +
            "SELECT * FROM stage.parameter_t " +
            "ON CONFLICT DO NOTHING;"
        )

    def idawebCoreETL(self):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "INSERT INTO core.measurements_t " +
            "SELECT * FROM stage.idaweb_t " +
            "ON CONFLICT DO NOTHING;"
        )
