import threading
import sqlalchemy
from sqlalchemy import MetaData, create_engine
from sqlalchemy import Table, Column, Integer, String, Float
from sqlalchemy_utils import database_exists, create_database
import messageAnnouncer


class Database:
    """ Database functions
    """

    engine = None
    databaseUrl = "postgresql://postgres:postgres@localhost:5432/klimadb"
    meta = MetaData()
    announcer = None
    databaseStatusStream = None
    engineStatusStream = None

    def __init__(self, announcer):
        """ Init engine
        """

        self.databaseStatusStream = messageAnnouncer.MessageAnnouncer()
        self.engineStatusStream = messageAnnouncer.MessageAnnouncer()
        self.announcer = announcer

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
            msgTxt = "Status: 1; Database not started; Error: " + str(e)
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
            Table(
                'meteoschweiz_t',
                self.meta,
                Column('year', Integer),
                Column('month', Integer),
                Column('station', String),
                Column('temperature', Float),
                Column('precipitation', Float),
                schema='stage')

            self.meta.create_all(self.engine)
