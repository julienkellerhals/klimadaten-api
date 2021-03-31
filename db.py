import threading
import sqlalchemy
from sqlalchemy import *
from sqlalchemy_utils import database_exists, create_database


class Database:
    """ Database functions
    """

    engine = None
    meta = MetaData()
    announcer = None

    def __init__(self):
        """ Init engine
        """

        self.engine = create_engine(
            "postgresql://postgres:postgres@localhost:5432/klimadb",
            echo=True
        )
        print(self.engine)

    def runThreaded(self, announcer):
        self.announcer = announcer
        x = threading.Thread(
            target=self.getEngineStatus
        )
        x.start()

    def getEngineStatus(self):
        try:
            self.engine.connect()
        except sqlalchemy.exc.OperationalError as e:
            msgTxt = "Status: 1; Error: " + str(e)
            self.announcer.announce(self.announcer.format_sse(msgTxt))
        else:
            msgTxt = "Status: 0;"
            self.announcer.announce(self.announcer.format_sse(msgTxt))

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
            meteoschweiz_t = Table(
                'meteoschweiz_t',
                self.meta,
                Column('year', Integer),
                Column('month', Integer),
                Column('station', String),
                Column('temprature', Float),
                Column('precipitation', Float),
                schema='stage')

            self.meta.create_all(self.engine)
