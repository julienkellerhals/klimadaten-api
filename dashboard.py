import pandas as pd
import plotly.express as px
# import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from flask import Flask
from dash.dependencies import Input, Output, State
from dash import Dash
from dash.exceptions import PreventUpdate


def mydashboard(flaskApp, instance):
    flaskApp = flaskApp
    instance.checkEngine()
    engine = instance.engine
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    dashApp = Dash(
        __name__,
        server=flaskApp,
        url_base_pathname='/dashboard/',
        external_stylesheets=external_stylesheets
    )

    def createDashboard():
        # meteoSchweizTempGraph = createMeteoSchweizTempGraph()
        # meteoSchweizPrecpGraph = createMeteoSchweizPrecpGraph()

        # add colors
        colors = {
            'background_d': '#05090C',
            'background_l1': '#EBEFF2',
            'background_l2': '#D8E0E5',
            'text_d': '#05090C',
            'text_l': '#EBEFF2'
        }

        # db queries for plots
        """
        "tre200d0"
        "temperature"
        "brefard0"
        "fu3010m1"
        "breclod0"
        "tre200dx"
        "tre200dn"
        "hns000d0"
        "hns000mx"
        "fklnd3m0"
        "precipitation"
        "rhs150m0" Precipitation; homogeneous monthly total
        "rzz150mx" Precipitation; maximum ten minute total of the month
        "rhh150mx" Precipitation; maximum total per hour of the month
        "rre150m0" Precipitation; monthly total
        "rsd700m0" Days of the month with precipitation total exceeding 69.9 mm
        "rs1000m0" Days of the month with precipitation total exceeding 99.9 mm
        """
        rhh150mx = pd.read_sql(
            """SELECT
            AVG(meas_value) avg_highest_hour,
            meas_date
            FROM core.measurements_t
            WHERE meas_name = 'rhh150mx'
            GROUP BY meas_date""",
            engine
        )

        dashApp.layout = html.Div([
            # header
            html.Div([
                html.Div([], style={'width': '5%', 'display': 'inline-block'}),
                html.Div([
                    html.H2(
                        'Datenstory',
                        style={
                            'textAlign': 'center',
                            'color': colors['text_l']
                        }
                    ),
                ], style={'display': 'inline-block'}
                ),
                html.Div([
                    html.Button('Datenstory', id='linkDatastory', n_clicks=0)
                ], style={'display': 'inline-block'}
                ),
                html.Div([
                    dcc.Link('Datenstory', href='/')
                ], style={'display': 'inline-block'}
                ),
                html.Div([], style={'width': '5%', 'display': 'inline-block'}),
                html.Div([
                    html.H2(
                        'Dashboard',
                        style={
                            'textAlign': 'center',
                            'color': colors['text_l']
                        }
                    )
                ], style={'display': 'inline-block'}
                )
            ], style={'backgroundColor': colors['background_d']}
            ),
            # first row of plots
            html.Div([
                html.Div([

                ],
                    style={
                        'width': '10%',
                        'display': 'inline-block'
                    }
                ),
                html.Div([
                    # scatterplot top left
                    dcc.Graph(
                        id='scatterplot_1',
                        figure={
                            'data': [go.Scatter(
                                x=rhh150mx["meas_date"],
                                y=rhh150mx['avg_highest_hour'],
                                mode='markers',
                                marker={
                                    'size': 12,
                                    'color': 'rgb(51,204,153)',
                                    'line': {'width': 2}
                                }
                            )],
                            'layout': go.Layout(
                                title='My Scatterplot',
                                xaxis={'title': 'x title'},
                                yaxis={'title': 'y title'})
                        }
                    )
                ], style={'width': '60%', 'display': 'inline-block'}
                ),
                html.Div([
                    html.H1(id='thisis')
                ], style={'width': '30%', 'display': 'inline-block'}
                ),
            ], style={'backgroundColor': colors['background_l1']}
            ),
        ])

    @dashApp.callback(
        Output('thisis', 'children'),
        [Input('linkDatastory', 'n_clicks')])
    def redirectToStory(n_clicks):
        if n_clicks is 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/", id="hello")

    """
    @dashApp.callback(
        Output('thisis', 'children'),
        [Input('linkDatastory', 'n_clicks')])
    def countClicking(n_clicks):
        return f"You entered: {n_clicks}"
    """
    '''
    df = pd.read_sql(('select "Timestamp","Value" from "MyTable" '
                     'where "Timestamp" BETWEEN %(dstart)s AND %(dfinish)s'),
                   db,params={"dstart":datetime(2014,6,24,16,0),"dfinish":datetime(2014,6,24,17,0)},
                   index_col=['Timestamp'])
    '''

    def createMeteoSchweizTempGraph():
        # use pd.read_sql() instead
        measurementsDf = pd.read_sql_table(
                "measurements_t",
                engine,
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

    def createMeteoSchweizPrecpGraph():
        measurementsDf = pd.read_sql_table(
                "measurements_t",
                engine,
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

    createDashboard()
    return dashApp
