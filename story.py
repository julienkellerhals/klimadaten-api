import re
import datetime
import math
from dash_core_components.Markdown import Markdown
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

    title1 = '''
       # Werden Vorfälle wie in Bondo zukünftig noch mehr Opfer fordern?
    '''
    title2 = '''
       #### Wenn einem der Boden unter den Füssen wegrutscht
    '''
    subtitle1 = '''
        **Der Klimawandel kann für uns viele Folgen haben. Eine selten 
        betrachtete ist die zunehmende Gefahr von Massenbewegungen. Wir werden 
        nachfolgend die Ursachen und wie sie sich in den vergangenen Jahren 
        verändert haben aufzuzeigen und am Beispiel von der Messstation auf 
        dem Weissfluhjoch visualisieren.**
    '''
    text1 = '''
        Bondo ist ein idyllisches Dorf im Kanton Graubünden am Fusse 
        des Piz Cengalo. Das kleine Dorf nahe der Grenze zu Italien liegt auf 
        gerade Mal 823m ü. M. Umgeben ist es von über 3000 Meter hohen 
        Berggipfeln, was dafür sorgt, dass einzelne Dorfteile im Winter 
        Tagelang keinen Sonnenstrahlen erreichen. 
        So ist die Region auch Ziel für viele Touristen, die versuchen dem 
        Stadtalltag zu entfliehen und sich in der Ruhe der Berge zu entspannen. 
        Auch unter Wanderern ist die Region mit ihren zahlreichen Wanderwegen 
        und SAC-Hütten ein beliebtes Ziel. Für viele ist es ein Traum in einer 
        solch wundervollen Berglandschaft zu leben. Dieser Traum wurde für die 
        Einwohner von Bondo am Mittwoch, dem 23. August 2017 um 09:30 Uhr zu 
        einem Albtraum. An diesem Tag löste sich eine ein Teil des Piz 
        Cengalo, was zu einem Murgang führte, der alles in seinem Weg 
        niederriss. So wurden auch viele Häuser in Bondo zerstört oder 
        beschädigt. 99 unterschiedliche Gebäude wurden bei dem Vorfall 
        beschädigt, wovon ein Drittel nicht mehr zu retten war. Noch schlimmer 
        kam es für acht Wanderer, welche zu diesem Zeitpunkt oberhalb von 
        Bondo unterwegs waren. Keiner der Wanderer kam bei diesem Unglück mit 
        dem Leben davon. Die Leichen der Wanderer wurden nie gefunden.
    '''
    text2 = '''
        Annemieke Buob Müller unterrichtete zum Zeitpunkt des Murgangs in 
        Stampa, einem Nachbardorf von Bondo. Erst am Mittag erfuhr sie vom 
        Murgang in ihrem Wohnort von ihren Schülern. Gemeinsam mit ihrem Mann 
        und allen anderen Bewohnern musste sie sich eine neue Unterkunft zu 
        suchen. Für ihren Mann Reto Müller war es schon immer nur eine Frage 
        der Zeit, bis sich ein solcher Murgang löst. Für ihn ist klar, dass das 
        Unglück noch schlimmer hätte kommen können. Wäre ein solches Ereignis 
        in der Nacht passiert, wären noch viel mehr Leute in den Häusern 
        gewesen und es hätte mit vielen Toten in Bodo selbst gerechnet werden 
        müssen. Das Ehepaar, welches seit langer Zeit in Bondo zuhause ist, 
        kam nach dem Unglück in einer Ferienwohnung in einem Nachbardorf unter. 
        Sie wurden aus ihrer Zuhause gerissen, ohne zu wissen, wann und ob sie 
        wieder zurückkönnen. Annemieke sprach nach dem Unglück mit einigen 
        früheren Nachbaren. Bei allen sass der Schock und der Schmerz über 
        das verlorene Zuhause sehr tief. 
    '''
    InterviewF1 = '''
        **-	Waren sei überrascht, dass es in Bondo zu solch einem Unglück 
        kam?**
    '''
    InterviewA1 = '''
        Ich war nicht überrascht von solch einem Unglück. Da es schon 2011 
        einen kleineren Murgang gab, war es angekündigt. Aus diesem Grund 
        wollte ich bei meinem Haus, welches in der roten Gefahrenzone lag, 
        eine Schutzmauer bauen. 2014 kamen Leute von der Gemeinde und vom 
        Kanton, um zu prüfen, ob die Schutzmauer nötig sei. Obwohl ich die 
        Mauer selbst gezahlt hätte, wurde das Baugesuch abgelehnt. Von da 
        an war mir bewusst, dass es nur noch eine Frage der Zeit ist.
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
    rainExtremeParam = 'rhh150yx'
    temperatureParam = 'tre200y0'

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

    def dfSelectionWrangling():
        # Select the stations with the highest quality data
        dfSelection = pd.read_sql(
            """
            SELECT
                station_name,
                station_short_name,
                meas_name,
                min(meas_year),
                COUNT(*)
            FROM(
                SELECT
                    extract(year from m.meas_date) as meas_year,
                    k.station_short_name,
                    k.station_name,
                    m.meas_name
                FROM core.measurements_t m
                JOIN core.station_t k
                ON (m.station = k.station_short_name)
                WHERE m.meas_name IN (
                    'hns000y0',
                    'hto000y0',
                    'rre150y0',
                    'rzz150yx',
                    'rhh150yx',
                    'tnd00xy0',
                    'tre200y0'
                )
                AND k.parameter IN (
                    'hns000y0',
                    'hto000y0',
                    'rre150y0',
                    'rzz150yx',
                    'rhh150yx',
                    'tnd00xy0',
                    'tre200y0'
                )
                AND m.valid_to = '2262-04-11'
                AND k.valid_to = '2262-04-11'
                AND k.station_name = 'Weissfluhjoch'
                GROUP BY
                meas_year,
                k.station_name,
                k.station_short_name,
                m.meas_name
            ) AS filtered
            GROUP BY
                station_name,
                station_short_name,
                station_name,
                meas_name
            HAVING COUNT(*) >= 30
            ORDER BY COUNT(*) DESC
            """,
            engine
        )

        dfSelection['years'] = 2020 - dfSelection['min']
        dfSelection['ratio'] = dfSelection['count'] / dfSelection['years']
        dfSelection = dfSelection[dfSelection.ratio >= 0.90]

        return dfSelection

    def dfStationsWrangling(dfSelection):
        dfStations = dfSelection.groupby([
            'station_short_name',
            'station_name'
        ]).agg(
            meas_name=('meas_name', 'count'),
            # min = ('min', 'min'),
            # ratio = ('ratio', 'min')
        ).reset_index()
        dfStations = dfStations[dfStations.meas_name == 7]

        return dfStations

    def plotScatterCreation(df, colors, param_name):
        # creating the snow scatterplot with all stations
        plot = go.Figure()

        plot.add_trace(go.Scatter(
            name=param_name,
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

    def plotBarCreation(df, colors):

        meanOfParam = df['meas_value'].mean()
        df['deviation'] = df[
            'meas_value'] - meanOfParam
        df['color'] = np.where(
            df['deviation'] >= 0, True, False)

        # creating the rain barplot
        plot = go.Figure()

        plot.add_trace(go.Bar(
            name='Regenfall',
            x=df["meas_year"],
            y=df["deviation"],
            base=meanOfParam,
            marker={
                'color': colors['rbb'],
                # 'line': {'width': 1, 'color': 'black'}
            }
        ))

        plot.add_trace(go.Scatter(
            name='Regression',
            x=df["meas_year"],
            y=df["bestfit"],
            mode='lines',
            marker={
                'size': 5,
                'color': colors['rbr'],
                'line': {'width': 1, 'color': 'black'}
            }
        ))

        plot.update_layout(
            title='∅ Maximaler Niederschlag aller Stationen in cm',
            title_x=0.05,
            yaxis={
                # 'title': 'maximaler Niederschlag in cm',
                'color': colors['plotAxisTitle'],
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': colors['plotGrid'],
                'range': [
                    df.meas_value.min() * 0.95,
                    df.meas_value.max() * 1.05
                ]
            },
            xaxis={
                'showgrid': False,
                'color': colors['plotAxisTitle'],
                'showline': True,
                'linecolor': colors['plotGrid']
            },
            hovermode='closest',
            margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
            height=360,
            paper_bgcolor=colors['BgPlot5'],
            plot_bgcolor='rgba(0,0,0,0)',
            legend={
                'yanchor': 'top',
                'y': 0.99,
                'xanchor': 'left',
                'x': 0.01
            }
        )

        return plot

    # dfSelection = dfSelectionWrangling()
    # dfStations = dfStationsWrangling(dfSelection)

    dfScatterSnow = dfScatterWrangling(snowParam, '1950-01-01')
    # change measurement unit to meters
    # dfScatterSnow['meas_value'] = round(dfScatterSnow.meas_value / 100, 2)

    dfScatterRain = dfScatterWrangling(rainParam, '1950-01-01')

    dfScatterRainExtreme = dfScatterWrangling(rainExtremeParam, '1950-01-01')

    dfScatterTemperature = dfScatterWrangling(temperatureParam, '1950-01-01')

    # main dashboard function
    def createStory():
        plotRain = plotScatterCreation(dfScatterRain, colors, 'Regenfälle')
        plotSnow = plotScatterCreation(dfScatterSnow, colors, 'Schneefälle')
        plotRainExtreme = plotBarCreation(dfScatterRainExtreme, colors)
        plotTemperature = plotBarCreation(dfScatterTemperature, colors)

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
                dcc.Markdown(title1),
                dcc.Markdown(subtitle1),
                dcc.Markdown(title2),
                dcc.Markdown(text2),
                dcc.Markdown(InterviewF1),
                dcc.Markdown(InterviewA1),
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
                dcc.Graph(
                    id='plotRainExtreme',
                    figure=plotRainExtreme,
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
                    id='plotTemperature',
                    figure=plotTemperature,
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
