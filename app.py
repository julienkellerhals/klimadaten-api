import os
from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
import db
import abstractDriver
import messageAnnouncer
from api import dbAPI
from story import Story
from api import adminAPI
from api import streamAPI
from api import scrapeAPI
from dashboard import Dashboard


announcer = messageAnnouncer.MessageAnnouncer()
abstractDriver = abstractDriver.AbstractDriver(announcer)
instance = db.Database(announcer)
app = Flask(__name__)
Dashboard(app, instance)
Story(app, instance)


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


@app.before_request
def before_request():
    if request.endpoint not in ["static", "adminApi.createConnectionString"]:
        if instance.databaseUrl is None:
            print("Database url not set")
            return render_template(
                "connectionString.html",
            )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )
