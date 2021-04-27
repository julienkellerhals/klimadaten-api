from flask import Flask
import pandas as pd
import plotly.express as px
# import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import Dash
import plotly.graph_objs as go


class Dashboard():
    flaskApp = None
    dashApp = None
    engine = None

    def __init__(self, flaskApp, instance):
        self.flaskApp = flaskApp
        instance.checkEngine()
        self.engine = instance.engine

    def createDashboard(self):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        self.dashApp = Dash(
            __name__,
            server=self.flaskApp,
            url_base_pathname='/dashboard/',
            external_stylesheets=external_stylesheets
        )
        # meteoSchweizTempGraph = self.createMeteoSchweizTempGraph()
        # meteoSchweizPrecpGraph = self.createMeteoSchweizPrecpGraph()

        # add colors
        colors = {
            'background_d': '#05090C',
            'background_l1': '#EBEFF2',
            'background_l2': '#D8E0E5',
            'text_d': '#05090C',
            'text_l': '#EBEFF2'
        }

        self.dashApp.layout = html.Div([
            # header
            html.Div([
                html.Div([
                    html.H2(
                        'Datenstory',
                        style={
                            'textAlign': 'center',
                            'color': colors['text_l']
                        }
                    )
                    # html.Button('Datenstory', id='linkDatastory', n_clicks=0)
                ], style={'width': '30%', 'display': 'inline-block'}
                ),
                html.Div([
                    html.H2(
                        'Dashboard',
                        style={
                            'textAlign': 'center',
                            'color': colors['text_l']
                        }
                    )
                ], style={'width': '30%', 'display': 'inline-block'}
                )
            ], style={'backgroundColor': colors['background_d']}
            ),
            # first row of plots
            html.Div([
                html.Div([

                ], style={'width': '70%', 'display': 'inline-block'}
                ),
                html.Div([

                ], style={'width': '30%', 'display': 'inline-block'}
                ),
            ], style={'backgroundColor': colors['background_l1']}
            ),
        ])

        """
        @self.dashApp.callback(
            Output('number_out', 'children'),
            [Input('linkDatastory', 'n_clicks')])
        def redirectToStory(self, n_clicks):
            return " times"
            #Flask.redirect('/')
        """

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
