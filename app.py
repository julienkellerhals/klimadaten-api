import dash_html_components as html
from dash import Dash
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import db
import abstractDriver
import messageAnnouncer
from api import dbAPI
from api import adminAPI
from api import streamAPI
from api import scrapeAPI

app = Flask(__name__)
dash_app = Dash(__name__, server=app, url_base_pathname='/dashboard/')
dash_app.layout = html.Div([html.H1('Hi there, I am app1 for dashboards')])

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


@app.route('/dashboard')
def render_dashboard():
    return Flask.redirect('/dash')
