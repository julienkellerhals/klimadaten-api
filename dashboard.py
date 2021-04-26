import pandas as pd
import plotly.express as px
# import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash


class Dashboard():
    flaskApp = None
    dashApp = None
    engine = None

    def __init__(self, flaskApp, instance):
        self.flaskApp = flaskApp
        instance.checkEngine()
        self.engine = instance.engine

    def createDashboard(self):
        self.dashApp = Dash(
            __name__,
            server=self.flaskApp,
            url_base_pathname='/dashboard/'
        )
        #meteoSchweizTempGraph = self.createMeteoSchweizTempGraph()
        #meteoSchweizPrecpGraph = self.createMeteoSchweizPrecpGraph()

        self.dashApp.layout = html.Div([
            html.Br(), ' This is the outermost div!', html.Br(),'-',
            html.Div([
                'This is an inner div!'],
                style={
                    'color': 'red',
                    'border': '2px red solid'}),
            html.Div([
                'This is an inner div!'],
                style={
                    'color': 'blue',
                    'border': '2px blue solid'})], 
            style={
                'textAlign': 'center', 
                'color': 'green',
                'border': '2px green solid'})

    def createMeteoSchweizTempGraph(self):
        # use pd.read_sql() instead
        measurementsDf = pd.read_sql_table(
                "measurements_t",
                self.engine,
                schema="core"
            )
        # in future create datamart with only the required data
        measurementsDf = measurementsDf[
            measurementsDf["meas_name"] == "temperature"
        ]

        # pv = pd.pivot_table(
        #     measurementsDf,
        #     index=['meas_date'],
        #     columns=["station"],
        #     values=['meas_value'],
        #     aggfunc="mean",
        #     fill_value=0
        # )

        # avgTemp = go.Line(x=pv.index, y=pv.values)

        fig = px.line(
            measurementsDf,
            x="meas_date",
            y="meas_value",
            color="station"
        )

        meteoSchweizTempGraph = html.Div(children=[
            html.H1(children='Meteosuisse'),
            html.Div(children='''Temperature evolution over time'''),
            dcc.Graph(
                id='ms-temp-overtime',
                figure=fig
            )
        ])

        return meteoSchweizTempGraph

    def createMeteoSchweizPrecpGraph(self):
        measurementsDf = pd.read_sql_table(
                "measurements_t",
                self.engine,
                schema="core"
            )
        measurementsDf = measurementsDf[
            measurementsDf["meas_name"] == "precipitation"
        ]

        fig = px.line(
            measurementsDf,
            x="meas_date",
            y="meas_value",
            color="station"
        )

        meteoSchweizPrecpGraph = html.Div(children=[
            html.H1(children='Meteosuisse'),
            html.Div(children='''Precipitation evolution over time'''),
            dcc.Graph(
                id='ms-precp-overtime',
                figure=fig
            )
        ])

        return meteoSchweizPrecpGraph
