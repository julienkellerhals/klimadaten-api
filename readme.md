# Klima API Readme

## Requirements
Python 3.7 <br>
Postgres

| modules                   | version |
|---------------------------|---------|
| dash_bootstrap_components | 0.12.2  |
| SQLAlchemy_Utils          | 0.36.8  |
| Flask                     | 1.1.2   |
| dash                      | 1.19.0  |
| msedge_selenium_tools     | 3.141.3 |
| statsmodels               | 0.12.0  |
| urllib3                   | 1.25.11 |
| plotly                    | 4.14.3  |
| dash_core_components      | 1.3.1   |
| numpy                     | 1.19.2  |
| selenium                  | 3.141.0 |
| SQLAlchemy                | 1.3.20  |
| requests                  | 2.24.0  |
| dash_html_components      | 1.0.1   |
| pytest                    | 0.0.0   |
| lxml                      | 4.6.1   |
| pandas                    | 1.1.3   |
| python_dateutil           | 2.8.1   |
| scikit_learn              | 0.24.2  |

# Installation & Usage
## Installation with provided database
---
Add images for clarity between steps

1. Install Python
2. Install all required modules for Klima API (see above)
3. Install postgres
4. Start flask app

   Command Prompt
    ~~~json
    > set FLASK_APP=app.py
    > set FLASK_ENV=production
    > flask run
    ~~~
    PowerShell
    ~~~ powershell
    > $env:FLASK_APP = "app.py"
    > $env:FLASK_ENV = "production"
    > flask run
    ~~~
    Linux (untested)
    ~~~ bash
    $ export FLASK_APP=app.py
    $ export FLASK_ENV=production
    $ flask run
    ~~~
    Important, start anaconda / pip env before starting flask app

5. Open webbrowser
6. Navigate to localhost:5000
7. Configure database connection string (Insert image of config page)
8. Navigate to database tab of administration overview
9. Press action button to connect to database
10. Open pgAdmin or equivalent
11. Import database
12. Uncomment dashboard creation line
13. Start server (see step 4)
14. Navigate to localhost:5000/admin
15. Use app

## Installation without provided database
---
Add images for clarity between steps

1. Install Python
2. Install all required modules for Klima API (see above)
3. Install postgres
4. Start flask app

   Command Prompt
    ~~~json
    > set FLASK_APP=app.py
    > set FLASK_ENV=production
    > flask run
    ~~~
    PowerShell
    ~~~ powershell
    > $env:FLASK_APP = "app.py"
    > $env:FLASK_ENV = "production"
    > flask run
    ~~~
    Linux (untested)
    ~~~ bash
    $ export FLASK_APP=app.py
    $ export FLASK_ENV=production
    $ flask run
    ~~~
    Important, start anaconda / pip env before starting flask app

5. Open webbrowser
6. Navigate to localhost:5000
7. Configure database connection string (Insert image of config page)
8. Navigate to database tab of administration overview
9. Press action button to connect to database
10. Press action button to create database tables
11. Run ETL load
12. Run Core load
13. Stop server
14. Uncomment dashboard creation line
15. Start server (see step 4)
16. Navigate to localhost:5000/admin
17. Use app

# Extensions
## Add new parameters
1. Open idawebConfig.xml
2. Add new parameter with name, group and granularity
3. Restart Server
4. Navigate to localhost:5000/admin/database
5. Click on idaweb_t
6. Run increment load

## New credentials
In case of blocked idaweb credentials in code
1. Open webscraping.py
2. Change credentials at the start of the file

# How it works
## Scraping
---
### webscraping.py
Webscraping.py contain both meteoschweiz and idaweb scraping functions

## API
---
### app.py & Api folder
app.py and following contain all routes for the API

#### app.py 
1. Instanciates blueprint for all subAPI's in API folder
2. Contains main routes for API

#### Api folder
1. All blueprint for different parts of the API
##### adminAPI.py
1. Contains main admin page routes
##### dbAPI.py
1. Contains database routes on admin page
2. Contains all database interface routes
#### scrapeAPI.py
1. Contains all scraping routes
#### streamAPI.py
1. Handels all sse streams to the front end

### db.py
db.py handels following:
1. All interaction with database
   1. Database creation
   2. Table creation
   3. Selects
   4. Inserts
2. Creates announcer for front end
3. Creates messages from database status and sends them over sse to front end

### download.py
Request to idaweb server over post
1. Contains helper functions for idaweb file download

### idawebConfig.xml
1. Contains idaweb parameters to download and refresh

### idawebConfigInitial.xml
1. Used for developement as temporary storage of configs

### messageAnnouncer.py
messageAnnouncer.py contains following:
1. sse sending
2. Queueing
3. Formating

### responseDict.py
responseDict.py contains following:
1. Response sending for front end
2. Button disabling for FE
3. Progressbar for FE
4. Start materialized view refresh after data inserts

## Dashboard
---
### dashboard.py
dashboard.py handels following:
1. Creation of dashboard and structure
2. Selection of data displayed in dashboard
3. Wrangling of selected data
4. Callbacks handeling for interaction

## Story
---
### story.py
story.py handels following:
1. Creation of story and structure
2. Selection of data displayed in story
3. Wrangling of selected data

## Tests
---
### webscrapping_test.py
Contains all webscraping unit tests
### db_test.py ?
Contains all database unit tests

## Database implementation
Add ERD
explain pk
explain dedupi
index?
explain schemas
explain loading process