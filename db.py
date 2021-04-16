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

    def readConfig(self, shortName):
        tree = etree.parse("idawebConfig.xml")
        root = tree.getroot()
        config = root.xpath("//*[contains(text(), '{}')]".format(shortName))[0]
        return config

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
        inspector = inspect(self.engine)
        stageTables = inspector.get_table_names("stage")
        coreTables = inspector.get_table_names("core")
        if len(stageTables) > 0 or len(coreTables) > 0:
            dbTables = {}
            dbTables["stage"] = inspector.get_table_names("stage")
            dbTables["core"] = inspector.get_table_names("core")

            msgTxt = "Status: 0; " + json.dumps(dbTables)
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
            self.meteoschweiz_t = Table(
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
            table_name='measurements_t',
            schema='core'
        ):
            self.measurements_t = Table(
                'measurements_t',
                self.meta,
                Column('meas_date', Date),
                Column('station', String),
                Column('granularity', String),
                Column('meas_name', String),
                Column('meas_value', Float),
                Column('source', String),
                Column("valid_from", Date),
                Column("valid_to", Date),
                schema='core')

        self.meta.create_all(self.engine)

    def runStageETL(self):
        self.idaWebStageETL()

    def idaWebStageETL(self):
        idaWebDf = pd.DataFrame()
        dataDir = Path.cwd() / "data"
        dataFiles = dataDir.glob("**/*_data.txt")
        for dataFile in dataFiles:
            print(dataFile.stem)
            dataFileDf = pd.read_csv(dataFile, sep=";")
            shortName = dataFileDf.columns[-1]
            config = self.readConfig(shortName)
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
            idaWebDf = idaWebDf.append(dataFileDf)
        validFromDf = idaWebDf.groupby(
            ["meas_name"]
        ).agg(valid_from=("meas_date", np.max))
        idaWebDf = idaWebDf.merge(
            validFromDf,
            on="meas_name",
            how="outer"
        )
        idaWebDf.to_sql(
            'idaweb_t',
            self.engine,
            schema='stage',
            if_exists='append',
            index=False
        )

    def runCoreETL(self):
        self.meteoschweizCoreETL()

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
            'measurements_t',
            self.engine,
            schema='core',
            if_exists='append',
            index=False
        )
