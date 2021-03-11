import sqlalchemy
from sqlalchemy import create_engine
from flask import Flask

import download

app = Flask(__name__)


@app.route("/")
def mainPage():
    return "Load web fe"

@app.route("/api")
def api():
    return "API"

@app.route("/admin/refresh")
def refreshData():
    return "Run webscraping"

@app.route("/admin/homog")
def getHomog():
    content = download.getData()
    # write data to database in etl schema
    return content.content

@app.route("/admin/db/create")
def createConnection():
    engine = create_engine("postgresql://postgres:postgres@localhost:5432/klimadb", echo=True)
    print(engine)
    return "Created connection"