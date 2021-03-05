from flask import Flask

app = Flask(__name__)


@app.route('/')
def mainPage():
    return 'Load web fe'

@app.route('/api')
def api():
    return 'API'

@app.route('/admin/refresh')
def refreshData():
    return 'Run webscraping'