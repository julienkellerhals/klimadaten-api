import re
import math
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


class Dashboard():
    DashboardBool = False
    instance = None
    dashApp = None

    def __init__(self, flaskApp, instance):
        self.instance = instance

        self.dashApp = Dash(
            __name__,
            server=flaskApp,
            url_base_pathname='/dashboard/',
            external_stylesheets=external_stylesheets
        )

        self.dashApp.layout = createLayout()
        self.dashApp.layout.children.append(
            createHeader(
                "Die Ursachen von Massenbewegungen",
                "dashboard"
            )
        )

        @self.dashApp.server.before_request
        def before_request():
            if not self.DashboardBool:
                if request.endpoint in ["/dashboard/"]:
                    try:
                        create_engine(
                            self.instance.databaseUrl
                        ).connect()
                    except sqlalchemy.exc.OperationalError as e:
                        print(e)
                        raise PreventUpdate
                    else:
                        self.mydashboard()

    def mydashboard(self):
        self.DashboardBool = True
        self.instance.checkEngine()
        engine = self.instance.engine

        textDescription = """
            In den kommenden Jahrzehnten werden Massenbewegungen wahrscheinlich
            häuffiger. Die generell zunehmende Temperatur führt zum langsamen
            Auftauen des Permafrosts und zur beschleunigten Gletscherschmelze,
            welche das Risiko für Massenbewegungen vergrössern. Das Risiko wird
            zudem durch die mögliche Zunahme von
            Starkniederschlägen und durch den Anstieg der
            Schneefallgrenze erhöht.
            Weniger Schneefall führt zu mehr
            Regen, welcher durch eine hohe Bodendurchnässung das Risiko für
            Massenbewegungen weiter erhöhen kann.
            """

        textSelection = """
            Station durch klicken auf Karte auswählen.
            Momentan werden die Daten für folgende Stationen angezeigt:
            """

        def dfMapWrangling(dfStations, dfStationInfo):
            # data wrangling map data
            dfMap = pd.merge(
                how='inner',
                left=dfStationInfo,
                right=dfStations,
                left_on='station_short_name',
                right_on='station'
            )

            dfMap = dfMap[[
                "station_name",
                "longitude",
                "latitude",
                "elevation"
            ]]

            # data wrangling for longitude and latitude
            dfMap['lon'] = dfMap['longitude'].str.extract(r'(\d+).$')
            dfMap['lon'] = pd.to_numeric(dfMap['lon'])
            dfMap['lon'] = round(dfMap['lon'] / 60, 3)
            dfMap['lon'] = dfMap['lon'].apply(str)
            dfMap['longitude'] = dfMap['longitude'].str.extract(r'(^\d+)') + \
                '.' + dfMap['lon'].str.extract(r'(\d+)$')
            dfMap = dfMap.drop('lon', axis=1)
            dfMap['lat'] = dfMap['latitude'].str.extract(r'(\d+).$')
            dfMap['lat'] = pd.to_numeric(dfMap['lat'])
            dfMap['lat'] = round(dfMap['lat'] / 60, 3)
            dfMap['lat'] = dfMap['lat'].apply(str)
            dfMap['latitude'] = \
                dfMap['latitude'].str.extract(r'(^\d+)') + '.' + \
                dfMap['lat'].str.extract(r'(\d+)$')
            dfMap = dfMap.drop('lat', axis=1)
            dfMap = dfMap.astype({'longitude': 'float', 'latitude': 'float'})
            dfMap = dfMap.groupby(['station_name']).agg(
                longitude=('longitude', 'mean'),
                latitude=('latitude', 'mean'),
                elevation=('elevation', 'mean'),
                # avg_now=('avg_now', 'mean'),
                # avg_then=('avg_then', 'mean'),
            ).reset_index()

            # add text column for map pop-up
            dfMap['text'] = '<b>' + dfMap['station_name'] + '</b>' +\
                ' (' + (dfMap['elevation']).astype(str) + ' m.ü.M.)' + \
                '<extra></extra>'

            return dfMap

        def dfScatterWrangling(param):
            # data wrangling scatterplot snow
            dfScatter = pd.read_sql(
                f"""
                SELECT
                    extract(year from m.meas_date) as meas_year,
                    extract(month from m.meas_date) as meas_month,
                    k.station_name,
                    sum(m.meas_value) meas_value,
                    m.station,
                    k.elevation
                FROM core.measurements_t m
                JOIN core.station_t k
                ON (m.station = k.station_short_name)
                WHERE m.meas_name = {"'"+ param +"'"}
                AND k.parameter = {"'"+ param +"'"}
                GROUP BY
                    meas_year,
                    meas_month,
                    k.station_name,
                    m.station,
                    k.elevation
                ORDER BY meas_year ASC
                """, engine)
            dfScatter = dfScatter.dropna()

            dfScatter = dfScatter[dfScatter.meas_year != 2021]

            return dfScatter

        def dfScatterAllWrangling(dfStations, dfScatter, yearParam):
            dfAll = pd.merge(
                how='inner',
                left=dfStations,
                right=dfScatter,
                left_on='station',
                right_on='station'
            )

            dfAll.sort_values(
                ['station', 'meas_year'],
                inplace=True
            )

            # select all Stations
            dfParamAll = dfAll.groupby('meas_year').agg(
                meas_value=('meas_value', 'mean'))

            dfParamAll = dfParamAll.reset_index()
            dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfParamAll.index),
                dfParamAll['meas_value']
            )
            dfParamAll['bestfit'] = reg.predict(np.vstack(dfParamAll.index))

            return dfParamAll

        def dfBarAllWrangling(dfStations, dfScatter, yearParam):
            dfAll = pd.merge(
                how='inner',
                left=dfStations,
                right=dfScatter,
                left_on='station',
                right_on='station'
            )

            dfAll.sort_values(
                ['station', 'meas_year'],
                inplace=True
            )

            # select all Stations
            dfParamAll = dfAll.groupby('meas_year').agg(
                meas_value=('meas_value', 'mean')
            )
            meanOfParam = dfParamAll['meas_value'].mean()
            dfParamAll['deviation'] = dfParamAll['meas_value'] - meanOfParam
            dfParamAll['color'] = np.where(
                dfParamAll['deviation'] >= 0, True, False
            )
            dfParamAll = dfParamAll.reset_index()
            dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfParamAll.index), dfParamAll['meas_value']
            )
            dfParamAll['bestfit'] = reg.predict(np.vstack(dfParamAll.index))

            return (dfParamAll, meanOfParam)

        def getParamYear(dfSelection, paramName):
            years = []

            for _, row in dfSelection.iterrows():
                idx = row["meas_name"].index(paramName)
                years.append(row["min_year"][idx])

            years = pd.Series(years)
            yearParam = years.median()

            if math.isnan(yearParam):
                yearParam = 0

            return yearParam

        # call start functions
        dfSelection = self.instance.getStationMinYear()
        dfStations = self.instance.getStationSubset()
        dfStationInfo = self.instance.getStationInfo(snowParam)

        dfMap = dfMapWrangling(
            dfStations,
            dfStationInfo
        )

        # get starting year for each parameter
        yearSnow = getParamYear(dfSelection, snowParam)
        yearRain = getParamYear(dfSelection, rainParam)
        yearRainExtreme = getParamYear(dfSelection, rainExtremeParam)
        yearTemperature = getParamYear(dfSelection, temperatureParam)

        # call plot functions
        dfScatterSnow = dfScatterWrangling(snowParam)
        # change measurement unit to meters
        dfScatterSnow['meas_value'] = round(dfScatterSnow.meas_value / 100, 2)
        dfSnowAll = dfScatterAllWrangling(dfStations, dfScatterSnow, yearSnow)
        dfScatterRain = dfScatterWrangling(rainParam)
        dfRainAll = dfScatterAllWrangling(dfStations, dfScatterRain, yearRain)
        dfScatterRainExtreme = dfScatterWrangling(rainExtremeParam)
        dfScatterRainExtreme = dfScatterRainExtreme[
            dfScatterRainExtreme.meas_year != min(
                dfScatterRainExtreme.meas_year
            )
        ]
        dfRainExtremeAll, meanRainExtreme = dfBarAllWrangling(
            dfStations, dfScatterRainExtreme, yearRainExtreme)
        dfScatterTemperature = dfScatterWrangling(temperatureParam)
        dfTemperatureAll, meanTemperature = dfBarAllWrangling(
            dfStations, dfScatterTemperature, yearTemperature)
        meanStationHeight = re.findall(
            r'^\d*',
            str(dfMap['elevation'].mean())
        )[0]

        # functions for plot creation
        def plotMapCreation(dfMap, colors):
            # creating the map
            plot = go.Figure()
            plot.add_trace(
                go.Scattermapbox(
                    lat=dfMap['latitude'],
                    lon=dfMap['longitude'],
                    hovertemplate=dfMap['text'],
                    mode='markers',
                    marker={
                        'size': 10,
                        'color': colors['d3'],
                        'opacity': 0.7
                    }))

            plot.update_layout(
                title_text='Parameter',
                hovermode='closest',
                showlegend=False,
                margin={
                    'l': 0,
                    'b': 0,
                    't': 0,
                    'r': 0
                },
                height=430,
                paper_bgcolor=colors['l0'],
                mapbox_style="open-street-map",
                mapbox=dict(
                    accesstoken='pk.eyJ1Ijoiam9lbGdyb3NqZWFuIiwiYSI6ImNrb' +
                    '24yNHpsMDA5OXQycXAxaHUzcDBzZHMifQ.TEpFKAlfpsYXKdAvgHYbLQ',
                    center=dict(lat=46.9, lon=8.2),
                    zoom=6.5,
                    style='mapbox://styles/joelgrosjean/' +
                    'ckon48gdw1yob17ozstokzg9c'))

            return plot

        def plotBarCreation(df, meanOfParam, colors, suffix, paramName):
            # creating the rain barplot
            plot = go.Figure()

            plot.add_trace(
                go.Bar(
                    name=paramName,
                    x=df["meas_year"],
                    y=df["deviation"],
                    base=meanOfParam,
                    marker={
                        'color': colors['rbb'],
                    }))

            plot.add_trace(
                go.Scatter(
                    name='Regression',
                    x=df["meas_year"],
                    y=df["bestfit"],
                    mode='lines',
                    marker={
                        'size': 5,
                        'color': colors['rbr'],
                        'line': {
                            'width': 1,
                            'color': 'black'
                        }
                    }))

            plot.update_layout(
                title_x=0.05,
                yaxis={
                    'color': colors['plotAxisTitle'],
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': colors['plotGrid'],
                    'range':
                    [
                        df.meas_value.min() * 0.95,
                        df.meas_value.max() * 1.05
                    ],
                    'ticksuffix': ' ' + suffix
                },
                xaxis={
                    'showgrid': False,
                    'color': colors['plotAxisTitle'],
                    'showline': True,
                    'linecolor': colors['plotGrid']
                },
                hovermode='closest',
                margin={
                    'l': 25,
                    'b': 25,
                    't': 5,
                    'r': 20
                },
                height=360,
                paper_bgcolor=colors['BgPlot1'],
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                legend={
                    'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'left',
                    'x': 0.01
                })

            return plot

        def plotScatterCreation(df, colors, suffix, paramName):
            # creating the snow scatterplot with all stations
            plot = go.Figure()

            plot.add_trace(
                go.Scatter(
                    name=paramName,
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
                    }))

            plot.add_trace(
                go.Scatter(
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
                    }))

            plot.update_layout(
                title_x=0.1,
                margin={
                    'l': 25,
                    'b': 25,
                    't': 5,
                    'r': 20
                },
                height=360,
                yaxis={
                    'color': colors['plotAxisTitle'],
                    'showgrid': True,
                    'gridwidth': 1,
                    'gridcolor': colors['plotGrid'],
                    'ticksuffix': ' ' + suffix
                },
                xaxis={
                    'showgrid': False,
                    'color': colors['plotAxisTitle'],
                    'showline': True,
                    'linecolor': colors['plotGrid']
                },
                paper_bgcolor=colors['BgPlot1'],
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                legend={
                    'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'right',
                    'x': 0.99
                })

            return plot

        # main dashboard function
        def createDashboard():

            # call plot creation functions
            plotMap = plotMapCreation(dfMap, colors)
            plotRainExtreme = plotBarCreation(
                dfRainExtremeAll,
                meanRainExtreme,
                colors,
                'mm',
                'extremer Regenfall'
            )
            plotTemperature = plotBarCreation(
                dfTemperatureAll,
                meanTemperature,
                colors,
                '°C',
                'Temperatur'
            )
            plotSnow = plotScatterCreation(
                dfSnowAll,
                colors,
                'm',
                'Schneefall'
            )
            plotSnow.update_layout(yaxis={
                'rangemode': "tozero",
            }, )
            plotRain = plotScatterCreation(
                dfRainAll,
                colors,
                'mm',
                'Regenfall'
            )
            plotRain.update_layout(
                height=420,
                yaxis={
                    'rangemode': "tozero",
                },
            )

            self.dashApp.layout.children.append(
                html.Div([
                    # first row of plots
                    html.Div([
                        # 1st plot 1st row
                        html.Div([
                            html.Div([
                                html.H4('Beschreibung')
                            ], style={
                                'padding-left': 20,
                            }
                            ),
                            html.Div([
                                html.Div([
                                    dcc.Markdown(
                                        textDescription,
                                        style={
                                            'font-size': '0.90rem'
                                        }
                                    ),
                                ], style={
                                    'maxHeight': 300,
                                    'overflowY': 'auto',
                                    'margin-bottom': 5
                                }
                                ),
                                html.Div([
                                    dcc.Markdown(
                                        textSelection,
                                        id='selection',
                                        style={
                                            'font-size': '0.90rem',
                                            'border-top': f"""1px
                                                {colors['shadow']} solid""",
                                        }
                                    ),
                                    dcc.Markdown(
                                        '## **alle Stationen**',
                                        id='name',
                                    ),
                                    dcc.Markdown(
                                        f"""#### **Ø
                                            {meanStationHeight} m.ü.M.**""",
                                        id='MASL'
                                    ),
                                ], style={
                                    'height': 158,
                                    'overflowY': 'auto',
                                    'text-align': 'bottom',
                                }
                                ),

                            ], style={
                                'backgroundColor': colors['BgPlot1'],
                                'height': 430,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                'padding': '10px',
                                'display': 'flex',
                                'flex-direction': 'column',
                                'justify-content': 'space-between',
                            }
                            ),
                        ], style={
                            'width': '25%',
                            'display': 'inline-block',
                            'horizontal-align': 'center'
                        }
                        ),
                        # 2nd plot 1st row
                        html.Div([
                            html.Div([
                                html.H4('Landkarte'),
                                html.Div(
                                    id='intermediateValue',
                                    style={'display': 'none'}
                                )
                            ], style={
                                'padding-left': 20,
                            }
                            ),
                            html.Div([
                                dcc.Graph(
                                    className='map-plot',
                                    id='plotMap',
                                    figure=plotMap,
                                    config={
                                        'displayModeBar': False,
                                        'staticPlot': False
                                    }
                                ),
                                html.Div([
                                    html.Button(
                                        id='allStations',
                                        n_clicks=0,
                                        children='alle Stationen',
                                        style={
                                            'backgroundColor': colors['d3'],
                                            'color': colors['l1'],
                                            'border-radius': 5,
                                        }
                                    )
                                ], style={
                                    'position': 'absolute',
                                    'vertical-align': 'top',
                                    'horizontal-align': 'left',
                                    'zIndex': 999,
                                    'margin-top': -40,
                                    'margin-left': 10
                                })
                            ], style={
                                'backgroundColor': colors['l0'],
                                'height': 430,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                # 'padding': '5px'
                            }
                            ),
                        ], style={
                            'width': '35%',
                            'display': 'inline-block',
                            'horizontal-align': 'left'
                        }
                        ),
                        # 3rd plot first row
                        html.Div([
                            html.Div([
                                html.H4("Durchschnittlicher Regenfall")
                            ], style={
                                'padding-left': 20,
                            }
                            ),
                            html.Div([
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
                                    'backgroundColor': colors['BgPlot1'],
                                    'height': 420
                                }
                                )
                            ], style={
                                'backgroundColor': colors['BgPlot1'],
                                'height': 430,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                'padding': '5px'
                            }
                            ),
                        ], style={
                            'width': '40%',
                            'display': 'inline-block',
                            'horizontal-align': 'right'
                        }
                        )
                    ], style={
                        'display': 'flex',
                        'align-items': 'flex-end',
                        'padding-left': 30,
                        'padding-right': 30
                    }
                    ),
                    # second row of plots
                    html.Div([
                        # 1st plot 2nd row
                        html.Div([
                            html.Div([
                                html.H4('Maximaler Regenfall in einer Stunde')
                            ], style={
                                'padding-left': 20
                            }
                            ),
                            html.Div([
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
                                    'backgroundColor': colors['BgPlot1'],
                                    'height': 360
                                }
                                )
                            ], style={
                                'backgroundColor': colors['BgPlot1'],
                                'height': 370,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                'padding': 5
                            }
                            ),
                        ], style={
                            'width': '30%',
                            'display': 'inline-block',
                            'horizontal-align': 'right'
                        }
                        ),
                        # 2nd plot 2nd row
                        html.Div([
                            html.Div([
                                html.H4('Durchschnittlicher Schneefall')
                            ], style={
                                'padding-left': 20
                            }
                            ),
                            html.Div([
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
                                    'backgroundColor': colors['BgPlot1'],
                                    'height': 360
                                }
                                )
                            ], style={
                                'backgroundColor': colors['BgPlot1'],
                                'height': 370,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                'padding': 5
                            }
                            ),
                        ], style={
                            'width': '40%',
                            'display': 'inline-block',
                            'horizontal-align': 'left'
                        }
                        ),
                        # 3rd plot 2nd row
                        html.Div([
                            html.Div([
                                html.H4('Durchschnittliche Temperatur')
                            ], style={
                                'padding-left': 20
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
                                'backgroundColor': colors['l0'],
                                'height': 370,
                                'box-shadow': shadow,
                                'position': 'relative',
                                'border-radius': 5,
                                'margin': '10px',
                                'padding': 5
                            }
                            ),
                        ], style={
                            'width': '30%',
                            'display': 'inline-block',
                            'horizontal-align': 'center'
                        }
                        ),
                    ], style={
                        'display': 'flex',
                        'align-items': 'flex-end',
                        'padding-left': 30,
                        'padding-right': 30,
                        'padding-bottom': 8,
                    }
                    ),
                ], style={
                    'display': 'flex',
                    'flex-direction': 'column',
                    'justify-content': 'center',
                    'flex-grow': '1',
                    'backgroundColor': colors['BgDashboard'],
                }
                )
            )

        @self.dashApp.callback(
            Output('linkOutput', 'children'),
            [Input('linkDatastory', 'n_clicks')]
        )
        def redirectToStory(n_clicks):
            if n_clicks == 0:
                raise PreventUpdate
            else:
                return dcc.Location(pathname="/", id="hello")

        @self.dashApp.callback(
            Output('intermediateValue', 'children'),
            Output('name', 'children'),
            Output('MASL', 'children'),
            Output('selection', 'children'),
            [Input('plotMap', 'clickData')]
        )
        def callbackMap(clickData):
            v_index = clickData['points'][0]['pointIndex']
            station = dfMap.iloc[v_index]['station_name']
            elevation = dfMap.iloc[v_index]['elevation']
            elevation = re.findall(r'^\d*', str(elevation))[0]
            stationString = f'## **{station}**'
            elevationString = f'#### **{elevation} m.ü.M.**'
            selectionString = """
                Station durch klicken auf Karte auswählen.
                Momentan werden die Daten für folgende Station angezeigt:
                """
            return (station, stationString, elevationString, selectionString)

        @self.dashApp.callback(
            Output('plotSnow', 'figure'),
            [Input('intermediateValue', 'children')]
        )
        def callbackSnow(station):
            dfSnowAll = dfScatterSnow[dfScatterSnow['station_name'] == station]
            dfSnowAll = dfSnowAll.reset_index()

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfSnowAll.meas_year),
                dfSnowAll['meas_value']
            )
            dfSnowAll['bestfit'] = reg.predict(np.vstack(dfSnowAll.meas_year))

            plotSnow = plotScatterCreation(
                dfSnowAll,
                colors,
                'm',
                'Schneefall'
            )

            plotSnow.update_layout(yaxis={
                'rangemode': "tozero",
            }, )

            return plotSnow

        @self.dashApp.callback(
            Output('plotRain', 'figure'),
            [Input('intermediateValue', 'children')]
        )
        def callbackRain(station):
            dfRainAll = dfScatterRain[dfScatterRain['station_name'] == station]
            dfRainAll = dfRainAll.reset_index()

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfRainAll.meas_year),
                dfRainAll['meas_value']
            )
            dfRainAll['bestfit'] = reg.predict(np.vstack(dfRainAll.meas_year))

            plotRain = plotScatterCreation(
                dfRainAll,
                colors,
                'mm',
                'Regenfall'
            )

            plotRain.update_layout(
                height=420,
                yaxis={
                    'rangemode': "tozero",
                },
            )

            return plotRain

        @self.dashApp.callback(
            Output('plotRainExtreme', 'figure'),
            [Input('intermediateValue', 'children')]
        )
        def callbackRainExtreme(station):
            dfRainExtremeAll = dfScatterRainExtreme[
                dfScatterRainExtreme['station_name'] == station]
            dfRainExtremeAll = dfRainExtremeAll.reset_index()
            dfRainExtremeAll = dfRainExtremeAll.groupby('meas_year').agg(
                meas_value=('meas_value', 'mean'))
            dfRainExtremeAll = dfRainExtremeAll.reset_index()
            dfRainExtremeAll = dfRainExtremeAll[
                dfRainExtremeAll.meas_year != min(dfRainExtremeAll.meas_year)]

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfRainExtremeAll.meas_year),
                dfRainExtremeAll['meas_value']
            )
            dfRainExtremeAll['bestfit'] = reg.predict(
                np.vstack(dfRainExtremeAll.meas_year))

            meanOfParam = dfRainExtremeAll['meas_value'].mean()
            dfRainExtremeAll[
                'deviation'] = dfRainExtremeAll['meas_value'] - meanOfParam
            dfRainExtremeAll['color'] = np.where(
                dfRainExtremeAll['deviation'] >= 0, True, False)

            plotRainExtreme = plotBarCreation(
                dfRainExtremeAll,
                meanOfParam,
                colors,
                'mm',
                'extremer Regenfall'
            )

            return plotRainExtreme

        @self.dashApp.callback(
            Output('plotTemperature', 'figure'),
            [Input('intermediateValue', 'children')]
        )
        def callbackTemperature(station):
            dfTemperatureAll = dfScatterTemperature[
                dfScatterTemperature['station_name'] == station]
            dfTemperatureAll = dfTemperatureAll.reset_index()

            # simple regression line
            reg = LinearRegression().fit(
                np.vstack(dfTemperatureAll.meas_year),
                dfTemperatureAll['meas_value']
            )
            dfTemperatureAll['bestfit'] = reg.predict(
                np.vstack(dfTemperatureAll.meas_year))

            meanOfParam = dfTemperatureAll['meas_value'].mean()
            dfTemperatureAll[
                'deviation'] = dfTemperatureAll['meas_value'] - meanOfParam
            dfTemperatureAll['color'] = np.where(
                dfTemperatureAll['deviation'] >= 0, True, False)

            plotTemperature = plotBarCreation(
                dfTemperatureAll,
                meanOfParam,
                colors,
                '°C',
                'Temperatur'
            )

            return plotTemperature

        @self.dashApp.callback(
            Output('plotRainExtreme', 'figure'),
            Output('plotTemperature', 'figure'),
            Output('plotSnow', 'figure'),
            Output('plotRain', 'figure'),
            Output('name', 'children'),
            Output('MASL', 'children'),
            Output('selection', 'children'),
            [Input('allStations', 'n_clicks')]
        )
        def callbackAllStations(n_clicks):
            plotRainExtreme = plotBarCreation(
                dfRainExtremeAll,
                meanRainExtreme,
                colors,
                'mm',
                'extremer Regenfall'
            )
            plotTemperature = plotBarCreation(
                dfTemperatureAll,
                meanTemperature,
                colors,
                '°C',
                'Temperatur'
            )
            plotSnow = plotScatterCreation(
                dfSnowAll,
                colors,
                'm',
                'Schneefall'
            )
            plotSnow.update_layout(yaxis={
                'rangemode': "tozero",
            }, )
            plotRain = plotScatterCreation(
                dfRainAll, colors, 'mm', 'Regenfall')
            plotRain.update_layout(
                height=420,
                yaxis={
                    'rangemode': "tozero",
                },
            )

            stationString = '## **alle Stationen**'
            elevationString = f'#### **Ø {meanStationHeight} m.ü.M.**'
            selectionString = """
                Station durch klicken auf Karte auswählen.
                Momentan werden die Daten für folgende Stationen angezeigt:
                """

            return (plotRainExtreme, plotTemperature, plotSnow, plotRain,
                    stationString, elevationString, selectionString)

        createDashboard()
