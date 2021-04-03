from flask import Flask
import db
from api import dbAPI
from api import adminAPI
from api import streamAPI
from api import scrapeAPI
import abstractDriver
import messageAnnouncer

app = Flask(__name__)

announcer = messageAnnouncer.MessageAnnouncer()
abstractDriver = abstractDriver.AbstractDriver(announcer)
instance = db.Database(announcer)

app.register_blueprint(adminAPI.constructBlueprint(
    announcer,
    instance,
    abstractDriver
    ),
    url_prefix="/admin"
)
app.register_blueprint(streamAPI.constructBlueprint(
        announcer,
        instance,
        abstractDriver
    ),
    url_prefix="/admin/stream"
)
app.register_blueprint(dbAPI.constructBlueprint(
        announcer,
        instance,
        abstractDriver
    ),
    url_prefix="/admin/db"
)
app.register_blueprint(scrapeAPI.constructBlueprint(
        announcer,
        instance,
        abstractDriver
    ),
    url_prefix="/admin/scrape"
)


@app.route("/")
def mainPage():
    """ Main page

    Returns:
        str: Temp main return
    """

    return "Hello World, story will be here"


@app.route("/api")
def api():
    """ API

    Returns:
        str: Temp
    """

    return "API"
