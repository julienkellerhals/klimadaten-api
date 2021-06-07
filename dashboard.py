import re
import math
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

# cd path/to/project
# pip install -r requirements.txt --user --no-deps
# ctrl + shift + P -> select interpreter -> new anaconda env


def mydashboard(flaskApp, instance):
    flaskApp = flaskApp
    instance.checkEngine()
    engine = instance.engine
    # decent stylesheets: MINTY, SANDSTONE, SIMPLEX, UNITED
    external_stylesheets = [dbc.themes.UNITED]

    textDescription = """
         In den kommenden Jahrzehnten werden Massenbewegungen wahrscheinlich
         häuffiger. Die generell zunehmende Temperatur führt zum langsamen
         Auftauen des Permafrosts und zur beschleunigten Gletscherschmelze,
         welche das Risiko für Massenbewegungen vergrössern. Das Risiko wird
         zudem durch die mögliche Zunahme von
         Starkniederschlägen und durch den Anstieg der Schneefallgrenze erhöht.
         Weniger Schneefall führt zu mehr
         Regen, welcher durch eine hohe Bodendurchnässung das Risiko für
         Massenbewegungen weiter erhöhen kann.
        """

    textSelection = """
        Station durch klicken auf Karte auswählen.
        Momentan werden die Daten für folgende Stationen angezeigt:
        """

    colors = {
        'd1': '#05090C',
        'd3': '#121F26',
        'l0': '#FFFFFF',
        'l1': '#EBEFF2',
        'l2': '#D8E0E5',
        'blue': '#285D8F',
        'red': '#DE3143',
        'BgPlots': '#FFFFFF',
        'plotGrid': '#B6C3CC',
        'plotAxisTitle': '#748B99',
        'BgDashboard': '#E2E8ED',
        'shadow': '#C5D1D8'
    }

    snowParam = 'hns000y0'
    rainParam = 'rre150y0'
    rainExtremeParam = 'rhh150mx'
    temperatureParam = 'tre200y0'
    shadow = f'7px 7px 10px {colors["shadow"]}'

    dashApp = Dash(__name__,
                   server=flaskApp,
                   url_base_pathname='/dashboard/',
                   external_stylesheets=external_stylesheets)

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
            """, engine)

        dfSelection['years'] = 2020 - dfSelection['min']
        dfSelection['ratio'] = dfSelection['count'] / dfSelection['years']
        dfSelection = dfSelection[dfSelection.ratio >= 0.90]

        return dfSelection

    def dfStationsWrangling(dfSelection):
        dfStations = dfSelection.groupby([
            'station_short_name', 'station_name'
        ]).agg(meas_name=('meas_name', 'count'),
               # min = ('min', 'min'),
               # ratio = ('ratio', 'min')
               ).reset_index()
        dfStations = dfStations[dfStations.meas_name == 7]

        return dfStations

    def dfMapWrangling(dfStations, snowParam):
        # data wrangling map data
        dfMap = pd.read_sql(
            f"""
            SELECT
            avg(m.meas_value) avg,
            k.station_name,
            k.longitude,
            k.latitude,
            k.elevation
            FROM core.measurements_t m
            LEFT JOIN core.station_t k
            ON (m.station = k.station_short_name)
            AND m.meas_name = {"'"+ snowParam +"'"}
            AND k.parameter = {"'"+ snowParam +"'"}
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY k.station_name,
            k.longitude,
            k.latitude,
            k.elevation;
            """, engine)

        dfMap = pd.merge(how='inner',
                         left=dfMap,
                         right=dfStations,
                         left_on='station_name',
                         right_on='station_name')

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
        dfMap['latitude'] = dfMap['latitude'].str.extract(r'(^\d+)') + '.' + \
            dfMap['lat'].str.extract(r'(\d+)$')
        dfMap = dfMap.drop('lat', axis=1)
        dfMap = dfMap.astype({'longitude': 'float', 'latitude': 'float'})
        dfMap = dfMap.groupby(['station_name']).agg(
            avg=('avg', 'mean'),
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
                k.station_name,
                sum(m.meas_value) meas_value,
                m.station,
                k.elevation
            FROM core.measurements_t m
            JOIN core.station_t k
            ON (m.station = k.station_short_name)
            WHERE m.meas_name = {"'"+ param +"'"}
            AND k.parameter = {"'"+ param +"'"}
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY meas_year, k.station_name, m.station, k.elevation
            ORDER BY meas_year ASC
            """, engine)
        dfScatter = dfScatter.dropna()

        dfScatter = dfScatter[dfScatter.meas_year != 2021]

        return dfScatter

    def dfHeatWrangling(param):
        # data wrangling scatterplot snow
        dfHeat = pd.read_sql(
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
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY
                meas_year,
                meas_month,
                k.station_name,
                m.station,
                k.elevation
            ORDER BY station_name, meas_year, meas_month ASC
            """, engine)
        dfHeat = dfHeat.dropna()

        return dfHeat

    def dfScatterAllWrangling(dfStations, dfScatter, yearParam):
        dfAll = pd.merge(how='inner',
                         left=dfStations,
                         right=dfScatter,
                         left_on='station_short_name',
                         right_on='station')

        dfAll.sort_values(['station_short_name', 'meas_year'], inplace=True)

        # select all Stations
        dfParamAll = dfAll.groupby('meas_year').agg(meas_value=('meas_value',
                                                                'mean'))

        dfParamAll = dfParamAll.reset_index()
        dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfParamAll.index),
                                     dfParamAll['meas_value'])
        dfParamAll['bestfit'] = reg.predict(np.vstack(dfParamAll.index))

        return dfParamAll

    def dfHeatAllWrangling(dfStations, dfHeat, yearParam):
        dfAll = pd.merge(how='inner',
                         left=dfStations,
                         right=dfHeat,
                         left_on='station_short_name',
                         right_on='station')

        dfAll.sort_values(['station_short_name', 'meas_year', 'meas_month'],
                          inplace=True)

        # select all Stations
        dfParamAll = dfAll.groupby(['meas_year', 'meas_month'
                                    ]).agg(meas_value=('meas_value', 'mean'))

        dfParamAll = dfParamAll.reset_index()
        # dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

        return dfParamAll

    def dfBarAllWrangling(dfStations, dfScatter, yearParam):
        dfAll = pd.merge(how='inner',
                         left=dfStations,
                         right=dfScatter,
                         left_on='station_short_name',
                         right_on='station')

        dfAll.sort_values(['station_short_name', 'meas_year'], inplace=True)

        # select all Stations
        dfParamAll = dfAll.groupby('meas_year').agg(meas_value=('meas_value',
                                                                'mean'))

        meanOfParam = dfParamAll['meas_value'].mean()
        dfParamAll['deviation'] = dfParamAll['meas_value'] - meanOfParam
        dfParamAll['color'] = np.where(dfParamAll['deviation'] >= 0, True,
                                       False)

        dfParamAll = dfParamAll.reset_index()
        # TODO fix param and desc
        dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfParamAll.index),
                                     dfParamAll['meas_value'])
        dfParamAll['bestfit'] = reg.predict(np.vstack(dfParamAll.index))

        return (dfParamAll, meanOfParam)

    def getParamYear(dfSelection, short_name):
        dfSelectionParam = dfSelection[dfSelection.meas_name == short_name]
        dfSelectionParam = dfSelectionParam[dfSelectionParam.station_name.isin(
            list(dfStations.station_name))]
        yearParam = dfSelectionParam['min'].median()

        if math.isnan(yearParam):
            yearParam = 0

        return yearParam

    # call start functions
    dfSelection = dfSelectionWrangling()
    dfStations = dfStationsWrangling(dfSelection)
    dfMap = dfMapWrangling(dfStations, snowParam)

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
    dfRainExtremeAll, meanRainExtreme = dfBarAllWrangling(
        dfStations, dfScatterRainExtreme, yearRainExtreme)
    dfScatterTemperature = dfScatterWrangling(temperatureParam)
    dfTemperatureAll, meanTemperature = dfBarAllWrangling(
        dfStations, dfScatterTemperature, yearTemperature)
    meanStationHeight = re.findall(r'^\d*', str(dfMap['elevation'].mean()))[0]

    # functions for plot creation
    def plotMapCreation(dfMap, colors):
        # creating the map
        plot = go.Figure()
        plot.add_trace(
            go.Scattermapbox(lat=dfMap['latitude'],
                             lon=dfMap['longitude'],
                             hovertemplate=dfMap['text'],
                             mode='markers',
                             marker={
                                 'size': 10,
                                 'color': colors['d3'],
                                 'opacity': 0.7
            }))

        plot.update_layout(
            title_text='Schneefall',
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

    def plotBarCreation(df, meanOfParam, colors, suffix):
        # creating the rain barplot
        plot = go.Figure()

        plot.add_trace(
            go.Bar(name='Regenfall',
                   x=df["meas_year"],
                   y=df["deviation"],
                   base=meanOfParam,
                   marker={
                       'color': colors['blue'],
                   }))

        plot.add_trace(
            go.Scatter(name='Regression',
                       x=df["meas_year"],
                       y=df["bestfit"],
                       mode='lines',
                       marker={
                           'size': 5,
                           'color': colors['red'],
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
                [df.meas_value.min() * 0.95,
                 df.meas_value.max() * 1.05],
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
            paper_bgcolor=colors['BgPlots'],
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            legend={
                'yanchor': 'top',
                'y': 0.99,
                'xanchor': 'left',
                'x': 0.01
            })

        return plot

    def plotScatterCreation(df, colors, suffix):
        # creating the snow scatterplot with all stations
        plot = go.Figure()

        plot.add_trace(
            go.Scatter(name='Schneefall',
                       x=df['meas_year'],
                       y=df['meas_value'],
                       mode='lines',
                       line_shape='spline',
                       marker={
                           'size': 5,
                           'color': colors['blue'],
                           'line': {
                               'width': 1,
                               'color': 'black'
                           }
                       }))

        plot.add_trace(
            go.Scatter(name='Regression',
                       x=df['meas_year'],
                       y=df['bestfit'],
                       mode='lines',
                       marker={
                           'size': 5,
                           'color': colors['red'],
                           'line': {
                               'width': 1,
                               'color': 'black'
                           }
                       }))

        plot.update_layout(title_x=0.1,
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
                           paper_bgcolor=colors['BgPlots'],
                           plot_bgcolor='rgba(0,0,0,0)',
                           showlegend=False,
                           legend={
                               'yanchor': 'top',
                               'y': 0.99,
                               'xanchor': 'right',
                               'x': 0.99
                           })

        return plot

    def plotHeatCreation(df, colors, suffix):
        # creating the snow scatterplot with all stations
        plot = go.Figure()

        plot.add_trace(
            go.Heatmap(
                # name='Schneefall',
                x=df['meas_year'],
                y=df['meas_month'],
                z=df['meas_value'],
                colorscale=[[1, colors['red']], [0.50, colors['l2']],
                            [0, colors['blue']]],
            ))

        plot.update_layout(
            # title_x=0.1,
            margin={
                'l': 25,
                'b': 25,
                't': 5,
                'r': 20
            },
            height=360,
            paper_bgcolor=colors['BgPlots'],
            plot_bgcolor='rgba(0,0,0,0)',
            # showlegend=False,
            # legend={
            #     'yanchor': 'top',
            #     'y': 0.99,
            #     'xanchor': 'right',
            #     'x': 0.99
            # }
        )

        return plot

    # main dashboard function
    def createDashboard():

        # call plot creation functions
        plotMap = plotMapCreation(dfMap, colors)
        plotRainExtreme = plotBarCreation(dfRainExtremeAll, meanRainExtreme,
                                          colors, 'mm')
        plotTemperature = plotBarCreation(dfTemperatureAll, meanTemperature,
                                          colors, '°C')
        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')
        plotSnow.update_layout(yaxis={
            'rangemode': "tozero",
        }, )
        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')
        plotRain.update_layout(
            height=420,
            yaxis={
                'rangemode': "tozero",
            },
        )

        dashApp.layout = html.Div([
            # header
            html.Div([
                html.Div([
                    html.H2(
                        'Die Ursachen von Massenbewegungen',
                        id='titleDashboard',
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-left': 45,
                            'padding-right':45
                        }
                    ),
                ], style={
                    'text-align': 'left',
                    'display': 'inline-block',
                }
                ),
                html.Div([
                    html.H3(
                        'Dashboard',
                        id='linkDashboard',
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-right': 30,
                            'font-weight': 'bold'
                        }
                    ),
                    html.H3(
                        'Datenstory',
                        id='linkDatastory',
                        n_clicks=0,
                        style={
                            'color': colors['l1'],
                            'display': 'inline-block',
                            'padding-right': 30,
                        }
                    ),
                    html.Div(id='linkDatastoryOutput')
                ], style={
                    'text-align': 'right',
                    'display': 'inline-block',
                    'padding-right': 15
                }
                ),
            ], style={
                'display': 'flex',
                'align-items': 'flex-start',
                'justify-content': 'space-between',
                'backgroundColor': colors['d3'],
                'box-shadow': shadow,
                'position': 'relative',
                'padding': '5px',
            }
            ),
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
                                    f'#### **Ø {meanStationHeight} m.ü.M.**',
                                    id='MASL'
                                ),
                            ], style={
                                'height': 158,
                                'overflowY': 'auto',
                                'text-align': 'bottom',
                            }
                            ),

                        ], style={
                            'backgroundColor': colors['BgPlots'],
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
                                        'color':colors['l1'],
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
                                'backgroundColor': colors['BgPlots'],
                                'height': 420
                            }
                            )
                        ], style={
                            'backgroundColor': colors['BgPlots'],
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
                            html.H4('Maximaler Regenfall')
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
                                'backgroundColor': colors['BgPlots'],
                                'height': 360
                            }
                            )
                        ], style={
                            'backgroundColor': colors['BgPlots'],
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
                                'backgroundColor': colors['BgPlots'],
                                'height': 360
                            }
                            )
                        ], style={
                            'backgroundColor': colors['BgPlots'],
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
        ], style={
            'height': '100vh',
            'display': 'flex',
            'flex-direction': 'column',
        }
        )

    @dashApp.callback(Output('linkDatastoryOutput', 'children'),
                      [Input('linkDatastory', 'n_clicks')])
    def redirectToStory(n_clicks):
        if n_clicks == 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/", id="hello")

    @dashApp.callback(Output('intermediateValue', 'children'),
                      Output('name', 'children'), Output('MASL', 'children'),
                      Output('selection', 'children'),
                      [Input('plotMap', 'clickData')])
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

    @dashApp.callback(Output('plotSnow', 'figure'),
                      [Input('intermediateValue', 'children')])
    def callbackSnow(station):
        dfSnowAll = dfScatterSnow[dfScatterSnow['station_name'] == station]
        dfSnowAll = dfSnowAll.reset_index()

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfSnowAll.meas_year),
                                     dfSnowAll['meas_value'])
        dfSnowAll['bestfit'] = reg.predict(np.vstack(dfSnowAll.meas_year))

        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')

        plotSnow.update_layout(yaxis={
            'rangemode': "tozero",
        }, )

        return plotSnow

    @dashApp.callback(Output('plotRain', 'figure'),
                      [Input('intermediateValue', 'children')])
    def callbackRain(station):
        dfRainAll = dfScatterRain[dfScatterRain['station_name'] == station]
        dfRainAll = dfRainAll.reset_index()

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfRainAll.meas_year),
                                     dfRainAll['meas_value'])
        dfRainAll['bestfit'] = reg.predict(np.vstack(dfRainAll.meas_year))

        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')

        plotRain.update_layout(
            height=420,
            yaxis={
                'rangemode': "tozero",
            },
        )

        return plotRain

    @dashApp.callback(Output('plotRainExtreme', 'figure'),
                      [Input('intermediateValue', 'children')])
    def callbackRainExtreme(station):
        dfRainExtremeAll = dfScatterRainExtreme[
            dfScatterRainExtreme['station_name'] == station]
        dfRainExtremeAll = dfRainExtremeAll.reset_index()

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfRainExtremeAll.meas_year),
                                     dfRainExtremeAll['meas_value'])
        dfRainExtremeAll['bestfit'] = reg.predict(
            np.vstack(dfRainExtremeAll.meas_year))

        meanOfParam = dfRainExtremeAll['meas_value'].mean()
        dfRainExtremeAll[
            'deviation'] = dfRainExtremeAll['meas_value'] - meanOfParam
        dfRainExtremeAll['color'] = np.where(
            dfRainExtremeAll['deviation'] >= 0, True, False)

        plotRainExtreme = plotBarCreation(dfRainExtremeAll, meanOfParam,
                                          colors, 'mm')

        return plotRainExtreme

    @dashApp.callback(Output('plotTemperature', 'figure'),
                      [Input('intermediateValue', 'children')])
    def callbackTemperature(station):
        dfTemperatureAll = dfScatterTemperature[
            dfScatterTemperature['station_name'] == station]
        dfTemperatureAll = dfTemperatureAll.reset_index()

        # simple regression line
        reg = LinearRegression().fit(np.vstack(dfTemperatureAll.meas_year),
                                     dfTemperatureAll['meas_value'])
        dfTemperatureAll['bestfit'] = reg.predict(
            np.vstack(dfTemperatureAll.meas_year))

        meanOfParam = dfTemperatureAll['meas_value'].mean()
        dfTemperatureAll[
            'deviation'] = dfTemperatureAll['meas_value'] - meanOfParam
        dfTemperatureAll['color'] = np.where(
            dfTemperatureAll['deviation'] >= 0, True, False)

        plotTemperature = plotBarCreation(dfTemperatureAll, meanOfParam,
                                          colors, '°C')

        return plotTemperature

    @dashApp.callback(Output('plotRainExtreme', 'figure'),
                      Output('plotTemperature', 'figure'),
                      Output('plotSnow',
                             'figure'), Output('plotRain', 'figure'),
                      Output('name', 'children'), Output('MASL', 'children'),
                      Output('selection', 'children'),
                      [Input('allStations', 'n_clicks')])
    def callbackAllStations(n_clicks):
        plotRainExtreme = plotBarCreation(dfRainExtremeAll, meanRainExtreme,
                                          colors, 'mm')
        plotTemperature = plotBarCreation(dfTemperatureAll, meanTemperature,
                                          colors, '°C')
        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')
        plotSnow.update_layout(yaxis={
            'rangemode': "tozero",
        }, )
        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')
        plotRain.update_layout(
            height=420,
            yaxis={
                'rangemode': "tozero",
            },
        )

        stationString = f'## **alle Stationen**'
        elevationString = f'#### **Ø {meanStationHeight} m.ü.M.**'
        selectionString = """
            Station durch klicken auf Karte auswählen.
            Momentan werden die Daten für folgende Stationen angezeigt:
            """

        return (plotRainExtreme, plotTemperature, plotSnow, plotRain,
                stationString, elevationString, selectionString)

    createDashboard()
    return dashApp
