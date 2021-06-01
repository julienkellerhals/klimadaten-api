import re
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash import Dash
from flask import Flask
from dash.exceptions import PreventUpdate
from sklearn.linear_model import LinearRegression
from dash.dependencies import Input, Output, State


def mystory(flaskApp, instance):
    flaskApp = flaskApp
    instance.checkEngine()
    engine = instance.engine
    # decent stylesheets: MINTY, SANDSTONE, SIMPLEX, UNITED
    external_stylesheets = [dbc.themes.UNITED]

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
        'l6': '#96A8B2',
        'l8': '#748B99',
        'c1': '#ED90A4',
        'c2': '#ABB150',
        'c3': '#00C1B2',
        'c4': '#ACA2EC',
        'b1': '#ADD8E5',
        'b2': '#BCDFEB',
        'rbb': '#285D8F',
        'rbr': '#DE3143',
        'lightblue': '#B4DFFF',
        'BgPlot1': '#FFFFFF',
        'BgPlot2': '#FFFFFF',
        'BgPlot3': '#FFFFFF',
        'BgPlot4': '#ADD8E5',
        'BgPlot5': '#FFFFFF',
        'plotTitle': '#121F26',
        'plotGrid': '#B6C3CC',
        'plotAxisTitle': '#748B99',
        'BgDashboard': '#D8E0E5',
        'shadow': '#C5D1D8'
    }

    shadow = f'7px 7px 7px {colors["shadow"]}'

    dashAppStory = Dash(
        __name__,
        server=flaskApp,
        url_base_pathname='/',
        external_stylesheets=external_stylesheets
    )

    # main dashboard function
    def createStory():
        dashAppStory.layout = html.Div([
            # header
            html.Div([
                html.Div([
                    html.H2(
                        'Erdrutsch in Bondo',
                        id='titleDashboard',
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-left': 45,
                        }
                    ),
                ], style={
                    'text-align': 'left',
                    'width': '50%',
                    'display': 'inline-block',
                }
                ),
                html.Div([
                    html.H3(
                        'Dashboard',
                        id='linkDashboard',
                        n_clicks=0,
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-right': 30,
                        }
                    ),
                    html.H3(
                        'Datenstory',
                        id='linkDatastory',
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-right': 45,
                            'font-weight': 'bold'
                        }
                    ),
                    html.Div(id='linkDashboardOutput')
                ], style={
                    'text-align': 'right',
                    'width': '50%',
                    'display': 'inline-block',
                }
                ),
            ], style={
                'backgroundColor': colors['d3'],
                'box-shadow': shadow,
                'position': 'relative',
                'padding': '5px',
            }
            ),
        ], style={
            'backgroundColor': colors['BgDashboard'],
            'height': '100vh'
        }
        )

    @dashAppStory.callback(
        Output('linkDashboardOutput', 'children'),
        [Input('linkDashboard', 'n_clicks')])
    def redirectToDashboard(n_clicks):
        if n_clicks == 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/dashboard/", id="hello")

    createStory()
    return dashAppStory
