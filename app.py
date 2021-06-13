import os
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
import db
import story
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

db = dashboard.Dashboard(app, instance)
# dashApp = db.mydashboard(app, instance)
# dashAppStory = story.mystory(app, instance)


@app.before_request
def before_request():
    if request.endpoint not in ["static", "adminApi.createConnectionString"]:
        if instance.databaseUrl is None:
            print("Database url not set")
            return render_template(
                "connectionString.html",
            )


@app.route("/")
def render_story():
    return Flask.redirect('/dash')


@app.route('/dashboard')
def render_dashboard():
    return Flask.redirect('/dash')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
