import sqlalchemy
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from flask import request
from sqlalchemy import create_engine
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from sklearn.linear_model import LinearRegression
from storyText import (
    title, desc, author, subtitle1, text1, text2,  # Bild
    text3, text4, text5,  # Bild
    text6, text7, text8, subtitle2, text9, text10,  # Plot Temp
    text11, text12, text13, text14,  # Plot Snow
    text15,  # Plot Rain
    text16, text17,  # Plot Rain Extreme
    text18, subtitle3, text19, text20, text21,  # Sep
    sep, subtitle4, text22, text23, text24
)
from dashHelper import (
    rainParam,
    snowParam,
    rainExtremeParam,
    temperatureParam,
    external_stylesheets,
    colors,
    shadow,
    createLayout,
    createHeader
)


class Story():
    storyBool = False
    instance = None
    dashApp = None

    def __init__(self, flaskApp, instance):
        self.instance = instance

        self.dashApp = Dash(
            __name__,
            server=flaskApp,
            url_base_pathname='/',
            external_stylesheets=external_stylesheets
        )

        self.dashApp.layout = createLayout()
        self.dashApp.layout.children.append(
            createHeader(
                "Massenbewegung in Bondo",
                "story"
            )
        )

        @self.dashApp.server.before_request
        def before_request():
            if not self.storyBool:
                if request.endpoint in ["/"]:
                    try:
                        create_engine(
                            self.instance.databaseUrl
                        ).connect()
                    except sqlalchemy.exc.OperationalError as e:
                        print(e)
                        raise PreventUpdate
                    else:
                        self.mystory()

    def mystory(self):
        self.storyBool = True
        self.instance.checkEngine()
        engine = self.instance.engine

        imgStyling = {
            'min-height': '100%',
            'min-width': '100%',
            'max-height': '100%',
            'max-width': '100%'
        }

        anchorStyling = {
            'color': '#FFFFFF'
        }

        imgWatermarkStyling = {
            'position': 'absolute',
            'vertical-align': 'top',
            'horizontal-align': 'left',
            'zIndex': 999,
            'margin-top': 0,
            'margin-left': 10
        }

        imgDivStyling = {
            'max-width': 965,
            'padding-left': 15,
            'padding-right': 15,
            'padding-top': 0,
            'horizontal-align': 'center',
            'margin': '0 auto',
            # 'vetical-align': 'top',
        }

        plotDivStyling = imgDivStyling

        textDivStyling = {
            'max-width': 665,
            'padding-left': 15,
            'padding-right': 15,
            'padding-top': 40,
            'horizontal-align': 'center',
            'margin': '0 auto',
            'font-size': '1.15rem',
            # 'vetical-align': 'top',
        }

        def dfScatterWrangling(param):
            # data wrangling scatterplot snow
            dfScatter = pd.read_sql(
                f"""
                SELECT
                    extract(year from m.meas_date) as meas_year,
                    extract(month from m.meas_date) as meas_month,
                    m.meas_value
                FROM core.measurements_t m
                JOIN core.station_t k
                ON (m.station = k.station_short_name)
                WHERE m.meas_name = {"'" + param +"'"}
                AND k.parameter = {"'" + param +"'"}
                AND k.station_name = 'Weissfluhjoch'
                AND m.valid_to = '2262-04-11'
                AND k.valid_to = '2262-04-11'
                ORDER BY meas_date ASC
                """,
                engine
            )
            dfScatter = dfScatter.dropna()

            # select all Stations
            dfScatter = dfScatter.groupby('meas_year').agg(
                meas_value=('meas_value', 'mean'))

            dfScatter = dfScatter.reset_index()

            # simple regression line
            reg = LinearRegression(
                ).fit(np.vstack(dfScatter.index), dfScatter['meas_value'])
            dfScatter['bestfit'] = reg.predict(np.vstack(dfScatter.index))

            return dfScatter

        def plotScatterCreation(df, colors, param_name, suffix):
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
                title_x=0.01,
                margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
                height=450,
                yaxis={
                    # 'title': 'Schneefall (Meter)',
                    'color': colors['plotAxisTitle'],
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': colors['plotGrid'],
                    'rangemode': "tozero",
                    'ticksuffix': ' ' + suffix
                },
                xaxis={
                    'showgrid': False,
                    'color': colors['plotAxisTitle'],
                    'showline': True,
                    'linecolor': colors['plotGrid']
                },
                font=dict(
                    size=18,
                ),
                paper_bgcolor=colors['BgPlot3'],
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
            )

            return plot

        def plotBarCreation(df, colors, param_name, suffix):

            meanOfParam = df['meas_value'].mean()
            df['deviation'] = df[
                'meas_value'] - meanOfParam
            df['color'] = np.where(
                df['deviation'] >= 0, True, False)

            # creating the rain barplot
            plot = go.Figure()

            plot.add_trace(go.Bar(
                name=param_name,
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
                title_x=0.01,
                yaxis={
                    'color': colors['plotAxisTitle'],
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': colors['plotGrid'],
                    'range': [
                        df.meas_value.min() * 0.95,
                        df.meas_value.max() * 1.05],
                    'ticksuffix': ' ' + suffix
                },
                xaxis={
                    'showgrid': False,
                    'color': colors['plotAxisTitle'],
                    'showline': True,
                    'linecolor': colors['plotGrid']
                },
                font=dict(
                    size=18,
                ),
                hovermode='closest',
                margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
                height=450,
                paper_bgcolor=colors['BgPlot5'],
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
            )

            return plot

        dfScatterSnow = dfScatterWrangling(snowParam)
        dfScatterSnow['meas_value'] = round(dfScatterSnow.meas_value / 100, 3)
        dfScatterSnow['bestfit'] = round(dfScatterSnow.bestfit / 100, 3)
        dfScatterRain = dfScatterWrangling(rainParam)
        dfScatterRainExtreme = dfScatterWrangling(rainExtremeParam)
        # remove the first and last year because they aren't complete
        dfScatterRainExtreme = dfScatterRainExtreme[
            dfScatterRainExtreme.meas_year != 2021]
        dfScatterRainExtreme = dfScatterRainExtreme[
            dfScatterRainExtreme.meas_year != min(
                dfScatterRainExtreme.meas_year
                )
            ]
        # simple regression line
        reg = LinearRegression().fit(
            np.vstack(dfScatterRainExtreme.index),
            dfScatterRainExtreme['meas_value']
        )
        dfScatterRainExtreme['bestfit'] = reg.predict(np.vstack(
            dfScatterRainExtreme.index))
        dfScatterTemperature = dfScatterWrangling(temperatureParam)

        # main dashboard function
        def createStory():
            # plot rain
            plotRain = plotScatterCreation(
                dfScatterRain, colors, 'Regenfälle', 'mm'
            )
            plotRain.update_layout(
                title='Regenfall auf dem Weissfluhjoch'
            )
            # plot snow
            plotSnow = plotScatterCreation(
                dfScatterSnow, colors, 'Schneefälle', 'm'
            )
            plotSnow.update_layout(
                title='Schneefall auf dem Weissfluhjoch'
            )
            # plot rain extreme
            plotRainExtreme = plotBarCreation(
                dfScatterRainExtreme, colors, 'Extreme Regenfälle', 'mm')
            plotRainExtreme.update_layout(
                title='Extremer Regenfall auf dem Weissfluhjoch'
            )
            # plot temperature
            plotTemperature = plotBarCreation(
                dfScatterTemperature, colors, 'Temperatur', '°C')
            plotTemperature.update_layout(
                title='Temperatur auf dem Weissfluhjoch',
                yaxis={
                    'range': [
                        dfScatterTemperature.meas_value.min() * 1.05,
                        dfScatterTemperature.meas_value.max() * 1.05],
                },
            )

            self.dashApp.layout.children.append(
                html.Div([
                    html.Div([
                        dcc.Markdown(title),
                        dcc.Markdown(desc),
                        dcc.Markdown(author),
                        dcc.Markdown(subtitle1),
                        dcc.Markdown(text1),
                        dcc.Markdown(text2),
                    ], style=textDivStyling
                    ),
                    html.Div([
                        html.Div([
                            html.A(
                                "Reto und Annemieke vor ihrem Haus",
                                style=anchorStyling
                            )
                        ], style=imgWatermarkStyling
                        ),
                        html.Img(
                            src='/assets/Picture1.jpg',
                            style=imgStyling
                        ),
                    ], style=imgDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text3),
                        dcc.Markdown(text4),
                        dcc.Markdown(text5),
                    ], style=textDivStyling
                    ),
                    html.Div([
                        html.Div([
                            html.A(
                                "© NZZ",
                                href=(
                                    "https://img.nzz.ch/S=W1720/O=75/http://" +
                                    "nzz-img.s3.amazonaws.com/2017/8/24/" +
                                    "ccdd8fa5-dbfe-485e-95df-2e6984c840fb.jpeg"
                                ),
                                style=anchorStyling
                            )
                        ], style=imgWatermarkStyling
                        ),
                        html.Img(
                            src='/assets/bondoMurgang.jpeg',
                            style=imgStyling
                        ),
                    ], style=imgDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text6),
                        dcc.Markdown(text7),
                        dcc.Markdown(text8),
                        dcc.Markdown(subtitle2),
                        dcc.Markdown(text9),
                        dcc.Markdown(text10),
                    ], style=textDivStyling
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
                    ], style=plotDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text11),
                        dcc.Markdown(text12),
                        dcc.Markdown(text13),
                        dcc.Markdown(text14),
                    ], style=textDivStyling
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
                    ], style=plotDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text15),
                    ], style=textDivStyling
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
                    ], style=plotDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text16),
                        dcc.Markdown(text17),
                    ], style=textDivStyling
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
                    ], style=plotDivStyling
                    ),
                    html.Div([
                        dcc.Markdown(text18),
                        dcc.Markdown(subtitle3),
                        dcc.Markdown(text19),
                        dcc.Markdown(text20),
                        dcc.Markdown(text21),
                        dcc.Markdown(sep),
                        dcc.Markdown(subtitle4),
                        dcc.Markdown(text22),
                        dcc.Markdown(text23),
                        dcc.Markdown(text24),
                    ], style=textDivStyling
                    ),
                    # footer
                    html.Div([
                        html.Div([
                            html.H4(
                                'Made with ♥ ' +
                                'by Bsc Data Science Students @ FHNW',
                                style={
                                    'color': colors['l1'],
                                    'display': 'inline-block',
                                    'padding-left': 45,
                                    'padding-right': 45,
                                }
                            ),
                        ], style={
                            'text-align': 'left',
                            'display': 'inline-block',
                            'margin-top': 20,
                            'margin-bottom': 20,
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
                    'backgroundColor': colors['BgStory'],
                    'height': '100vh'
                })
            )

        @self.dashApp.callback(
            Output('linkDashboardOutput', 'children'),
            [Input('linkDashboard', 'n_clicks')]
        )
        def redirectToDashboard(n_clicks):
            if n_clicks == 0:
                raise PreventUpdate
            else:
                return dcc.Location(pathname="/dashboard/", id="hello")

        createStory()
