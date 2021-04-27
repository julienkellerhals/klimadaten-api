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
    '''
    external_stylesheets = [
        {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }]
    '''

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
            'd1': '#05090C',
            'd2': '#0C1419',
            'd3': '#121F26',
            'l0': '#FFFFFF',
            'l1': '#EBEFF2',
            'l2': '#D8E0E5',
            'l3': '#C5D1D8',
            'l4': '#B6C3CC',
            'l5': '#A3B5BF',
            'l6': '#96A8B2'
        }

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

        # db queries for plots
        '''
        df = pd.read_sql(
            """SELECT
            AVG(meas_value) avg_highest_hour,
            meas_date
            FROM core.measurements_t
            WHERE meas_name = 'rhh150mx'
            GROUP BY meas_date""",
            engine
        )
        '''
        # df['meas_date'] = pd.to_datetime(df['meas_date'])
        features = [
            'breclod0', 'brefard0', 'tre200dx', 'tre200d0', 'tre200dn',
            'hns000d0', 'fklnd3m0', 'fu3010m1', 'hns000mx', 'rsd700m0',
            'rs1000m0', 'rzz150mx', 'rhh150mx', 'rre150m0', 'rhs150m0'
        ]

        dashApp.layout = html.Div([
            # header
            html.Div([
                html.Div([], style={'width': '2%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(
                        'Dashboard',
                        id='linkDashboard',
                        style={
                            'color': colors['l1'],
                            'margin-top': '20px',
                            'margin-bottom': '20px',
                            }
                    )
                ], style={'display': 'inline-block'}
                ),
                html.Div([], style={'width': '2%', 'display': 'inline-block'}),
                html.Div([
                    html.H3(
                        'Datenstory',
                        id='linkDatastory',
                        n_clicks=0,
                        style={'color': colors['l6']}
                    )
                ], style={'display': 'inline-block'}
                )
            ], style={'backgroundColor': colors['d3']}
            ),
            # first row of plots
            html.Div([
                html.Div([], style={
                    'width': '5%',
                    'display': 'inline-block'
                }),
                # scatterplot top left
                html.Div([
                    dcc.Dropdown(
                        id='yaxis',
                        options=[{'label': i, 'value': i} for i in features],
                        value='breclod0'
                    ),
                    # make plotly figure bar invisible
                    # config={'displayModeBar': False,'staticPlot': False}
                    html.Div(id='scatterplot1')
                ], style={
                    'backgroundColor': colors['l0'],
                    'width': '55%',
                    'height': 500,
                    'box-shadow': '8px 8px 8px lightgrey',
                    'display': 'inline-block',
                    'position': 'relative',
                    'border-radius': 15,
                    'padding': '10px',
                    'margin': '10px'
                }
                ),
                html.Div([], style={
                    'backgroundColor': colors['l0'],
                    'width': '27.5%',
                    'height': 500,
                    'box-shadow': '8px 8px 8px lightgrey',
                    'display': 'inline-block',
                    'position': 'relative',
                    'border-radius': 15,
                    'padding': '10px',
                    'margin': '10px'
                }
                ),
                html.Div([], style={
                    'width': '5%',
                    'display': 'inline-block'
                }),
            ], style={'backgroundColor': colors['l1']}
            ),
            # second row of plots
            html.Div([
                html.Div([], style={
                    'width': '5%',
                    'display': 'inline-block'
                }),
                html.Div([
                    html.H1(id='thisis')
                ], style={
                    'backgroundColor': colors['l0'],
                    'width': '30%',
                    'height': 285,
                    'box-shadow': '8px 8px 8px lightgrey',
                    'display': 'inline-block',
                    'position': 'relative',
                    'border-radius': 15,
                    'padding': '10px',
                    'margin': '10px'
                }
                ),
                html.Div([], style={
                    'backgroundColor': colors['l0'],
                    'width': '30%',
                    'height': 285,
                    'box-shadow': '8px 8px 8px lightgrey',
                    'display': 'inline-block',
                    'position': 'relative',
                    'border-radius': 15,
                    'padding': '10px',
                    'margin': '10px'
                }
                ),
                html.Div([], style={
                    'backgroundColor': colors['l0'],
                    'width': '20.3%',
                    'height': 285,
                    'box-shadow': '8px 8px 8px lightgrey',
                    'display': 'inline-block',
                    'position': 'relative',
                    'border-radius': 15,
                    'padding': '10px',
                    'margin': '10px'
                }
                ),
                html.Div([], style={
                    'width': '5%',
                    'display': 'inline-block'
                }),
            ])
        ], style={'backgroundColor': colors['l1']}
        )

    @dashApp.callback(
        Output('thisis', 'children'),
        [Input('linkDatastory', 'n_clicks')])
    def redirectToStory(n_clicks):
        if n_clicks is 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/", id="hello")

    @dashApp.callback(
        Output('scatterplot1', 'children'),
        [Input('yaxis', 'value')])
    def update_graph(yaxis_name):
        df = pd.read_sql(
            f"""SELECT
            AVG(meas_value),
            meas_date
            FROM core.measurements_t
            WHERE meas_name = {"'"+ yaxis_name +"'"}
            GROUP BY meas_date""",
            engine
        )

        return {
            'data': [go.Scatter(
                x=df["meas_date"],
                y=df["avg"],
                mode='lines+markers',
                marker={
                    'size': 5,
                    'color': 'blue',
                    'line': {'width': 2}
                }
            )],
            'layout': go.Layout(
                title='My Scatterplot',
                xaxis={'title': 'time in years'},
                yaxis={'title': yaxis_name},
                hovermode='closest')
        }

    createDashboard()
    return dashApp
