# Klima API Readme

- [Klima API Readme](#klima-api-readme)
  - [Requirements](#requirements)
  - [Installation & Usage](#installation--usage)
    - [With provided database](#with-provided-database)
    - [Without provided database](#without-provided-database)
    - [With VSCode and Edge](#with-vscode-and-edge)
    - [Start flask app](#start-flask-app)
    - [Install Browser driver](#install-browser-driver)
  - [Extensions](#extensions)
    - [Add new parameters](#add-new-parameters)
    - [New credentials](#new-credentials)
  - [How it works](#how-it-works)
    - [Scraping](#scraping)
      - [webscraping.py](#webscrapingpy)
    - [API](#api)
      - [app.py & API folder](#apppy--api-folder)
        - [app.py](#apppy)
        - [API folder](#api-folder)
          - [adminAPI.py](#adminapipy)
          - [dbAPI.py](#dbapipy)
          - [scrapeAPI.py](#scrapeapipy)
          - [streamAPI.py](#streamapipy)
      - [db.py](#dbpy)
      - [download.py](#downloadpy)
      - [idawebConfig.xml](#idawebconfigxml)
      - [idawebConfigInitial.xml](#idawebconfiginitialxml)
      - [messageAnnouncer.py](#messageannouncerpy)
      - [responseDict.py](#responsedictpy)
      - [abstractDriver.py](#abstractdriverpy)
    - [Dashboard](#dashboard)
      - [dashboard.py](#dashboardpy)
    - [Story](#story)
      - [story.py](#storypy)
    - [Tests](#tests)
      - [webscrapping_test.py](#webscrapping_testpy)
      - [db_test.py TODO Check name when branch is merged](#db_testpy-todo-check-name-when-branch-is-merged)
    - [Database implementation](#database-implementation)
      - [Stage](#stage)
      - [Core](#core)
      - [ERD](#erd)

## Requirements

Following programms and modules are required to run KlimaAPI

- [ ] Python 3.7
- [ ] Postgres
- [ ] Modules

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

## Installation & Usage

### With provided database

Add images for clarity between steps

1. Install Python
2. Install all required modules for Klima API ([Requirements](#requirements))
3. Install Postgres
4. Start flask app ([Instruction](#start-flask-app))
5. Open webbrowser
6. Navigate to [localhost:5000](http://localhost:5000)
7. Configure database connection string (Insert image of config page)
8. Navigate to database tab of administration overview
9. Press action button to connect to database
10. Open pgAdmin or equivalent
11. Import database
12. Uncomment dashboard creation line in [app.py](app.py)
13. Start server ([Instruction](#start-flask-app))
14. Navigate to [localhost:5000/admin](http://localhost:5000/admin)
15. Use app

---

### Without provided database

Add images for clarity between steps

1. Install Python
2. Install all required modules for Klima API ([Requirements](#requirements))
3. Install Postgres
4. Start flask app ([Instruction](#start-flask-app))
5. Open webbrowser
6. Navigate to [localhost:5000](http://localhost:5000)
7. Configure database connection string (Insert image of config page)
8. Navigate to database tab of administration overview
9. Press action button to connect to database
10. Press action button to create database tables
11. Run ETL load
12. Run Core load
13. Stop server
14. Uncomment dashboard creation line in [app.py](app.py)
15. Start server ([Instruction](#start-flask-app))
16. Navigate to [localhost:5000/admin](http://localhost:5000/admin)
17. Use app

---

### With VSCode and Edge

1. Install Python
2. Install all required modules for Klima API ([Requirements](#requirements))
3. Install Postgres
4. Open VSCode
5. Launch debug config FE + Flask
6. Configure database connection string (Insert image of config page)
7. Navigate to database tab of administration overview
8. Press action button to connect to database
9. Press action button to create database tables
10. Run ETL load
11. Run Core load
12. Stop server
13. Uncomment dashboard creation line in [app.py](app.py)
14. Launch debug config FE + Flask
15. Use app

---

### Start flask app

Command Prompt

~~~ cmd
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
export FLASK_APP=app.py
export FLASK_ENV=production
flask run
~~~

**Important**, start anaconda / pip env before starting flask app

### Install Browser driver

In order to get new data selenium requires a browser driver to scrape websites

> Browser version are checked automatically

Installation as follows:

Edge

1. Navigate to [localhost:5000/admin](http://localhost:5000/admin)
2. Press `Driver name`
3. Press `Download driver`

Chrome

1. Navigate to [localhost:5000/admin/driver/Chrome?headless=false](http://localhost:5000/admin/driver/Chrome?headless=false)

## Extensions

### Add new parameters

1. Open [idawebConfig.xml](idawebConfig.xml)
2. Add new parameter with name, group and granularity
3. Restart Server
4. Navigate to [localhost:5000/admin/database](http://localhost:5000/admin/database)
5. Click on idaweb_t
6. Run increment load

---

### New credentials

In case of blocked idaweb credentials in code

1. Open [webscraping.py](webscraping.py)
2. Change credentials at the start of the file

## How it works

### Scraping

---

#### [webscraping.py](webscraping.py)

[webscraping.py](webscraping.py) contain both meteoschweiz and idaweb scraping functions

### API

---

#### [app.py](app.py) & API folder

##### [app.py](app.py)

1. Instanciates blueprint for all subAPI's in API folder
2. Contains main routes for API

##### API folder

1. All blueprint for different parts of the API

###### [adminAPI.py](api/adminAPI.py)

1. Contains main admin page routes

###### [dbAPI.py](api/dbAPI.py)

1. Contains database routes on [admin page](http://localhost:5000/admin)
2. Contains all database interface routes

###### [scrapeAPI.py](api/scrapeAPI.py)

1. Contains all scraping routes

###### [streamAPI.py](api/streamAPI.py)

1. Handels all sse streams to the front end

#### [db.py](db.py)

[db.py](db.py) handels following:

1. All interaction with database
   1. Database creation
   2. Table creation
   3. Selects
   4. Inserts
2. Creates announcer for front end
3. Creates messages from database status and sends them over sse to front end

#### [download.py](download.py)

Helper file with functions for `POST` and `GET` requests

1. Helper functions for idaweb file download

#### [idawebConfig.xml](idawebConfig.xml)

1. Contains idaweb parameters to download and refresh

#### [idawebConfigInitial.xml](idawebConfigInitial.xml)

1. Used for developement as temporary storage of configs

#### [messageAnnouncer.py](messageAnnouncer.py)

[messageAnnouncer.py](messageAnnouncer.py) contains following:

1. sse
2. Queueing
3. Formating

#### [responseDict.py](responseDict.py)

[responseDict.py](responseDict.py) contains following:

1. Response sending for front end
2. Button disabling for FE
3. Progressbar for FE
4. Start materialized view refresh after data inserts

#### [abstractDriver.py](abstractDriver.py)

[abstractDriver.py](abstractDriver.py) handels all selenium driver interactions

1. Driver install
2. Front end information about driver status

### [Dashboard](http//localhost:5000/dashboard)

---

#### [dashboard.py](dashboard.py)

[dashboard.py](dashboard.py) handels following:

1. Creation of dashboard and structure
2. Selection of data displayed in dashboard
3. Wrangling of selected data
4. Callbacks handeling for interaction

### [Story](http://localhost:5000)

---

#### [story.py](story.py)

[story.py](story.py) handels following:

1. Creation of story and structure
2. Selection of data displayed in story
3. Wrangling of selected data

### [Tests](http://localhost:5000/admin/tests)

---

#### [webscrapping_test.py](webscraping.py)

Contains all webscraping unit tests

#### db_test.py TODO Check name when branch is merged

Contains all database unit tests

### Database implementation

---

TODO fix wording and structure

- Database is divided into two main schemas, Stage and Core
- All tables have corresponding materialized views for number of rows and last update
- Data is copied from left to right
  - Text files / Web into stage tables
  - Stage tables into Core tables

#### Stage

Stage schema contain all new data

- Can contain duplicate entries
- No primary keys
- Raw data

#### Core

- Cannot contain duplicate entries due to natural primary key violation
- Data is indexed for faster selects
- idaweb_t & meteoschweiz_t is merged into measurements_t table
- Colums get added for datasource description
- Data gets parsed into format used for future analysis
- Core data never gets deleted, can be used to add new data

#### ERD

![databaseERD](/static/databaseERD.png)
