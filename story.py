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

    text1 = '''
        Die Entscheidende Frage bleibt: Wurden die Bergwanderer 
        durch Warntafeln genügen über die Gefahr in diesem Gebiet informiert? 
        Die Antwort darauf lautet leider Nein. Die Warntafeln am Ender der 
        Alpstrasse warnten nur vor möglichen Bergstürzen im rot schraffierten 
        Vor der Gefahr eines Murgangs im Anschluss an einen Bergsturz wurden 
        nicht gewarnt
    '''

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
        'BgStory': '#FFFFFF',
        'shadow': '#C5D1D8'
    }

    shadow = f'7px 7px 7px {colors["shadow"]}'

    dashAppStory = Dash(
        __name__,
        server=flaskApp,
        url_base_pathname='/',
        external_stylesheets=external_stylesheets
    )

    rainParam = 'rre150m0'
    snowParam = 'hns000y0'

    def dfScatterWrangling(param, meas_date='2007-01-01'):
        # data wrangling scatterplot snow
        dfScatter = pd.read_sql(
            f"""
            SELECT
                m.meas_date meas_year,
                k.station_name,
                m.meas_value,
                m.station,
                k.elevation
            FROM core.measurements_t m
            JOIN core.station_t k
            ON (m.station = k.station_short_name)
            WHERE m.meas_name = {"'" + param +"'"}
            AND k.parameter = {"'" + param +"'"}
            AND k.station_name = 'Weissfluhjoch'
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            AND m.meas_date >= {"'" + meas_date +"'"}
            ORDER BY station, meas_date ASC
            """,
            engine
        )
        dfScatter = dfScatter.dropna()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfScatter.index), dfScatter['meas_value'])
        dfScatter['bestfit'] = reg.predict(np.vstack(dfScatter.index))

        return dfScatter

    def plotScatterCreation(df, colors):
        # creating the snow scatterplot with all stations
        plot = go.Figure()

        plot.add_trace(go.Scatter(
            name='Schneefall',
            x=df['meas_year'],
            y=df['meas_value'],
            mode='lines',
            line_shape='spline',
            marker={
                'size': 5,
                'color': colors['rbb'],
                'line': {
                    'width': 1,
                    'color': 'black'
                }
            }
        ))

        plot.add_trace(go.Scatter(
            name='Regression',
            x=df['meas_year'],
            y=df['bestfit'],
            mode='lines',
            marker={
                'size': 5,
                'color': colors['rbr'],
                'line': {
                    'width': 1,
                    'color': 'black'
                }
            }
        ))

        plot.update_layout(
            title='Regenfall in Weissfluhjoch',
            title_x=0,
            margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
            height=450,
            yaxis={
                # 'title': 'Schneefall (Meter)',
                'color': colors['plotAxisTitle'],
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': colors['plotGrid'],
                'rangemode': "tozero",
            },
            xaxis={
                'showgrid': False,
                'color': colors['plotAxisTitle'],
                'showline': True,
                'linecolor': colors['plotGrid']
            },
            paper_bgcolor=colors['BgPlot3'],
            plot_bgcolor='rgba(0,0,0,0)',
            # legend={
            #     'yanchor': 'top',
            #     'y': 0.99,
            #     'xanchor': 'right',
            #     'x': 0.99
            # }
        )

        return plot

    dfScatterSnow = dfScatterWrangling(snowParam, '1950-01-01')
    # change measurement unit to meters
    # dfScatterSnow['meas_value'] = round(dfScatterSnow.meas_value / 100, 2)

    dfScatterRain = dfScatterWrangling(rainParam, '1950-01-01')

    # main dashboard function
    def createStory():
        plotRain = plotScatterCreation(dfScatterRain, colors)
        plotSnow = plotScatterCreation(dfScatterSnow, colors)

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
            html.Div([
                dcc.Markdown('# Guter Titel'),
                dcc.Markdown(text1),
            ], style={
                'max-width': 665,
                'padding-left': 15,
                'padding-right': 15,
                'padding-top': 40,
                'horizontal-align': 'center',
                'margin': '0 auto',
                # 'vetical-align': 'top',
            }
            ),
            html.Div([
                dcc.Graph(
                    id='plotRain',
                    figure=plotRain,
                    config={
                        'displayModeBar': False,
                        'staticPlot': False
                    }
                )
            ], style={
                'max-width': 965,
                'padding-left': 15,
                'padding-right': 15,
                'padding-top': 0,
                'horizontal-align': 'center',
                'margin': '0 auto',
                # 'vetical-align': 'top',
            }
            ),
            html.Div([
                dcc.Graph(
                    id='plotSnow',
                    figure=plotSnow,
                    config={
                        'displayModeBar': False,                      
                        'staticPlot': False
                    }
                )
            ], style={
                'max-width': 965,
                'padding-left': 15,
                'padding-right': 15,
                'padding-top': 0,
                'horizontal-align': 'center',
                'margin': '0 auto',
                # 'vetical-align': 'top',
            }
            ),
            html.Div([
                dcc.Markdown(text1),
            ], style={
                'max-width': 665,
                'padding-left': 15,
                'padding-right': 15,
                'padding-top': 40,
                'horizontal-align': 'center',
                'margin': '0 auto',
                # 'vetical-align': 'top',
            }
            ),
        ], style={
            'backgroundColor': colors['BgStory'],
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
