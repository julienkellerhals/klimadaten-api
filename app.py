from flask import Flask
import db
import dashboard
import abstractDriver
import messageAnnouncer
from api import dbAPI
from api import adminAPI
from api import streamAPI
from api import scrapeAPI

announcer = messageAnnouncer.MessageAnnouncer()
abstractDriver = abstractDriver.AbstractDriver(announcer)
instance = db.Database(announcer)

app = Flask(__name__)
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

dashApp = dashboard.Dashboard(app, instance)
dashApp.createDashboard()


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


@app.route('/dashboard')
def render_dashboard():
    return Flask.redirect('/dash')
