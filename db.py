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
    tablesStatusStream = None

    def __init__(self, announcer):
        """ Init engine
        """

        self.databaseStatusStream = messageAnnouncer.MessageAnnouncer()
        self.engineStatusStream = messageAnnouncer.MessageAnnouncer()
        self.tablesStatusStream = messageAnnouncer.MessageAnnouncer()
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

    def getDatabaseStatus(self):
        x = threading.Thread(
            target=self._getDatabaseStatus
        )
        x.start()

    def _getDatabaseStatus(self):
        try:
            create_engine(
                self.databaseUrl
            ).connect()
        except sqlalchemy.exc.OperationalError as e:
            try:
                database_exists(self.databaseUrl)
            except sqlalchemy.exc.OperationalError as e:
                msgTxt = "Status: 2; Database not started; Error: " + str(e)
                self.databaseStatusStream.announce(
                    self.databaseStatusStream.format_sse(msgTxt)
                )
            else:
                msgTxt = "Status: 1; Database not created; Error: " + str(e)
                self.databaseStatusStream.announce(
                    self.databaseStatusStream.format_sse(msgTxt)
                )
        else:
            msgTxt = "Status: 0; Database connection: " + str(self.databaseUrl)
            self.databaseStatusStream.announce(
                self.databaseStatusStream.format_sse(msgTxt)
            )

    def getEngineStatus(self):
        x = threading.Thread(
            target=self._getEngineStatus
        )
        x.start()

    def _getEngineStatus(self):
        if self.engine is None:
            msgTxt = "Status: 1; Engine not started; Error: Connect to db"
            self.engineStatusStream.announce(
                self.engineStatusStream.format_sse(msgTxt)
            )
        else:
            msgTxt = "Status: 0; Engine started"
            self.engineStatusStream.announce(
                self.engineStatusStream.format_sse(msgTxt)
            )

    def getTablesStatus(self):
        x = threading.Thread(
            target=self._getTablesStatus
        )
        x.start()

    def _getTablesStatus(self):
        self.getEngine()
        try:
            inspector = inspect(self.engine)
        except sqlalchemy.exc.OperationalError:
            msgTxt = "Status: 1; Database not found"
            self.tablesStatusStream.announce(
                self.tablesStatusStream.format_sse(msgTxt)
            )
        else:
            self.conn = self.engine.connect()

            stageTables = inspector.get_table_names("stage")
            coreTables = inspector.get_table_names("core")
            if len(stageTables) > 0 or len(coreTables) > 0:
                dbTables = {}

                dbTables["stage"] = []
                for stageTable in stageTables:
                    tableDict = {}

                    tableDict["name"] = stageTable

                    nrowQuery = \
                        "SELECT count(*) FROM stage.{}".format(stageTable)
                    tableDict["nrow"] = self.conn.execute(
                        nrowQuery
                    ).first()[0]

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

                    tableDict["lastRefresh"] = self.conn.execute(
                        lastRefreshQuery
                    ).first()[0]

                    tableDict["action"] = []

                    if stageTable == "idaweb_t":
                        tableDict["action"].append("Initial load")
                        tableDict["action"].append("Run scrapping")
                    elif stageTable == "meteoschweiz_t":
                        tableDict["action"].append("Run scrapping")
                    elif stageTable == "station_t":
                        tableDict["action"].append("Initial load")
                    elif stageTable == "parameter_t":
                        tableDict["action"].append("Initial load")

                    dbTables["stage"].append(tableDict)

                dbTables["core"] = []
                for coreTable in coreTables:
                    if "temp_" not in coreTable:
                        tableDict = {}

                        tableDict["name"] = coreTable

                        tableDict["nrow"] = self.conn.execute(
                            "SELECT count(*) FROM core.{}".format(
                                coreTable
                            )
                        ).first()[0]

                        tableDict["lastRefresh"] = self.conn.execute(
                            "SELECT max(valid_from) FROM core.{}".format(
                                coreTable
                            )
                        ).first()[0]

                        tableDict["action"] = ["Load"]
                        dbTables["core"].append(tableDict)

                msgTxt = "Status: 0; " + json.dumps(
                    dbTables,
                    default=str
                )
                self.tablesStatusStream.announce(
                    self.tablesStatusStream.format_sse(msgTxt)
                )
            else:
                msgTxt = "Status: 1; No tables found"
                self.tablesStatusStream.announce(
                    self.tablesStatusStream.format_sse(msgTxt)
                )

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
                Column("load_date", Date),
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
                Column("valid_from", Date),
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
                Column("valid_from", Date),
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
                Column("valid_from", Date),
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
                Column("valid_from", Date),
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
                                corr = ["0/0"]
                    idx = re.search(
                        r"\d+\/\d+",
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

    def idaWebStageETL(self):
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
            dataFiles = dataDir.glob("**/*_{}_*_data.txt".format(config.text))
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

    def idawebCoreETL(self):
        if self.conn is None:
            self.conn = self.engine.connect()
        self.conn.execute(
            "INSERT INTO core.measurements_t " +
            "SELECT * FROM stage.idaweb_t " +
            "ON CONFLICT DO NOTHING;"
        )
