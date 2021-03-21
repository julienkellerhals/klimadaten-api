import sqlalchemy
from sqlalchemy import *
from sqlalchemy_utils import database_exists, create_database

class Database:
    engine = None
    meta = MetaData()

    def __init__(self):
        self.engine = create_engine("postgresql://postgres:postgres@localhost:5432/klimadb", echo=True)
        print(self.engine)

    def createDatabase(self):
        if not database_exists(self.engine.url): #Check if Database exists else create
            create_database(self.engine.url)
        if not self.engine.dialect.has_schema(self.engine, 'core'): #Check if schema core exists else create
            self.engine.execute(sqlalchemy.schema.CreateSchema('core'))
        if not self.engine.dialect.has_schema(self.engine, 'stage'): #Check if schema etl exists else create
            self.engine.execute(sqlalchemy.schema.CreateSchema('stage'))

    def createTable(self):
        if not self.engine.dialect.has_table(connection = self.engine, table_name = 'meteoschweiz_t', schema = 'stage'):
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
 