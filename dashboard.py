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

# TODO height of dash elements as percentage of the whole
# TODO remove duplicates from map (avg. everything else)
# TODO Add Rain for all Stations with button

"""
wind
"fklnd3m0" Days of the month with gust peak exceeding 27.8 m/s (100 km/h)
"fu3010m1" Gust peak (one second); monthly maximum

lightning
"breclod0" Close range lightning (distance below 3 km); daily total
"brefard0" Distant lightning (distance 3 - 30 km); daily total

precipitation
"precipitation" meteoschweiz
"rhs150m0" Precipitation; homogeneous monthly total
"rzz150mx" Precipitation; maximum ten minute total of the month
"rhh150mx" Precipitation; maximum total per hour of the month
"rre150m0" Precipitation; monthly total
"rsd700m0" Days of the month with precipitation total exceeding 69.9 mm
"rs1000m0" Days of the month with precipitation total exceeding 99.9 mm
"rsd700y0" Days of the year with precipitation total exceeding 69.9 mm
"rs1000y0" Days in a year with precipitation total exceeding 99.9 mm
"rre150y0" Precipitation; annual total
"rti150yx" Precipitation; date of the maximum daily total of the year
"rzz150yx" Precipitation; maximum ten minute total of the year
"rhh150yx" Precipitation; maximum total per hour of the year

snow
"hns000d0" Fresh snow; daily total 6 UTC - 6 UTC following day (cm)
"hns000mx" Fresh snow; maximum daily total of the month
"hto000y0" Snow depth; annual mean
"hns000y0" Fresh snow; annual total of the daily merasurements

temperature
"temperature" meteoschweiz
"tre200dn" Air temperature 2 m above ground; daily minimum
"tre200d0" Air temperature 2 m above ground; daily mean
"tre200dx" Air temperature 2 m above ground; daily maximum
"tre200y0" Air temperature 2 m above ground; annual mean
"tnd00xy0" Ice days (maximum lower than 0 degrees C); annual total

soil temperature
"tso100m0" Soil temperature at 100 cm depth; monthly mean
"tso100mx" Soil temperature at 100 cm depth; absolute monthly maximum
"""

"""
$white #FFFFFF
$gray1 #EBEFF2
$gray2 #E2E8ED
$gray3 #D8E0E5
$gray4 #C5D1D8
$gray5 #B6C3CC
$gray6 #A3B5BF
$gray7 #96A8B2
$gray8 #889AA5
$gray9 #748B99
$gray10 #677E8C
$gray11 #59717F
$gray12 #4C6472
Sgray 13 #425866
Sgray14 #364C59
$gray 15 #2C404C
Sgray16 #23343F
Sgray17 #1B2A33
Sgray 18 #121F26
Sgray 19 #0C1419
Sgray20 #05090C
$black #000000
"""


def mydashboard(flaskApp, instance):
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

    snowParam = 'hns000y0'
    rainParam = 'rre150y0'
    shadow = f'7px 7px 7px {colors["shadow"]}'

    dashApp = Dash(
        __name__,
        server=flaskApp,
        url_base_pathname='/dashboard/',
        external_stylesheets=external_stylesheets
    )

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

    def dfMapWrangling(dfStations, snowParam):
        # data wrangling map data
        dfMap1 = pd.read_sql(
            f"""
            SELECT
            avg(m.meas_value) avg_now,
            k.station_name,
            k.longitude,
            k.latitude,
            k.elevation
            FROM core.measurements_t m
            LEFT JOIN core.station_t k
            ON (m.station = k.station_short_name)
            WHERE m.meas_date >= '2010-01-01'
            AND m.meas_date < '2020-01-01'
            AND m.meas_name = {"'"+ snowParam +"'"}
            AND k.parameter = {"'"+ snowParam +"'"}
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY k.station_name,
            k.longitude,
            k.latitude,
            k.elevation;
            """,
            engine
        )

        dfMap2 = pd.read_sql(
            f"""
            SELECT
            avg(m.meas_value) avg_then,
            k.station_name
            FROM core.measurements_t m
            LEFT JOIN core.station_t k
            ON (m.station = k.station_short_name)
            WHERE m.meas_date >= '1970-01-01'
            AND m.meas_date < '1980-01-01'
            AND m.meas_name = {"'"+ snowParam +"'"}
            AND k.parameter = {"'"+ snowParam +"'"}
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY k.station_name
            """,
            engine
        )

        dfMap = pd.merge(
            how='inner',
            left=dfMap1,
            right=dfMap2,
            left_on='station_name',
            right_on='station_name'
        )

        dfMap = pd.merge(
            how='inner',
            left=dfMap,
            right=dfStations,
            left_on='station_name',
            right_on='station_name'
        )

        # data wrangling for longitude and latitude
        dfMap['lon'] = dfMap['longitude'].str.extract(r'(\d+).$')
        dfMap['lon'] = pd.to_numeric(dfMap['lon'])
        dfMap['lon'] = round(dfMap['lon']/60, 3)
        dfMap['lon'] = dfMap['lon'].apply(str)
        dfMap['longitude'] = dfMap['longitude'].str.extract(r'(^\d+)') + \
            '.' + dfMap['lon'].str.extract(r'(\d+)$')
        dfMap = dfMap.drop('lon', axis=1)
        dfMap['lat'] = dfMap['latitude'].str.extract(r'(\d+).$')
        dfMap['lat'] = pd.to_numeric(dfMap['lat'])
        dfMap['lat'] = round(dfMap['lat']/60, 3)
        dfMap['lat'] = dfMap['lat'].apply(str)
        dfMap['latitude'] = dfMap['latitude'].str.extract(r'(^\d+)') + '.' + \
            dfMap['lat'].str.extract(r'(\d+)$')
        dfMap = dfMap.drop('lat', axis=1)
        dfMap = dfMap.astype({'longitude': 'float', 'latitude': 'float'})
        dfMap = dfMap.groupby(['station_name']).agg(
            avg_now=('avg_now', 'mean'),
            longitude=('longitude', 'mean'),
            latitude=('latitude', 'mean'),
            elevation=('elevation', 'mean'),
            avg_then=('avg_then', 'mean'),
        ).reset_index()

        # add text column for map pop-up
        dfMap['text'] = '<b>' + dfMap['station_name'] + '</b>' +\
            ' (' + (dfMap['elevation']).astype(str) + ' m.ü.M.)' + \
            '<br>Ø Schneefall pro Tag 1970-1980: ' + \
            (round(dfMap['avg_then'], 2)).astype(str) + 'cm' + \
            '<br>Ø Schneefall pro Tag 2010-2020: ' + \
            (round(dfMap['avg_now'], 2)).astype(str) + 'cm' + \
            '<br>Veränderung: ' + \
            (round(((
                dfMap['avg_now'] - dfMap['avg_then']) / dfMap['avg_then']
            ) * 100, 0)).astype(str) + '%' + '<extra></extra>'

        return dfMap

    def dfScatterSnowWrangling():
        # data wrangling scatterplot snow
        dfScatterSnow = pd.read_sql(
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
            WHERE m.meas_name = {"'"+ snowParam +"'"}
            AND k.parameter = {"'"+ snowParam +"'"}
            AND m.valid_to = '2262-04-11'
            AND k.valid_to = '2262-04-11'
            GROUP BY meas_year, k.station_name, m.station, k.elevation
            ORDER BY meas_year ASC
            """,
            engine
        )

        # change measurement unit to meters
        dfScatterSnow['meas_value'] = round(dfScatterSnow.meas_value / 100, 2)
        dfScatterSnow = dfScatterSnow.dropna()

        return dfScatterSnow

    def dfSnowAllWrangling(dfStations, dfScatterSnow, medianValueTotalSnow):
        dfAll = pd.merge(
            how='inner',
            left=dfStations,
            right=dfScatterSnow,
            left_on='station_short_name',
            right_on='station'
        )

        dfAll.sort_values([
            'station_short_name',
            'meas_year'
        ], inplace=True)

        # select all Stations
        dfSnowAll = dfAll.groupby(
            'meas_year'
        ).agg(
            meas_value=('meas_value', 'mean')
        )

        dfSnowAll = dfSnowAll.reset_index()
        dfSnowAll = dfSnowAll[dfSnowAll.meas_year >= medianValueTotalSnow]

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfSnowAll.index), dfSnowAll['meas_value'])
        dfSnowAll['bestfit'] = reg.predict(np.vstack(dfSnowAll.index))

        return dfSnowAll

    def dfScatterRainWrangling():
        # avg of highest 10 minute total of rain of
        # a month per year of all stations available
        dfScatterRain = pd.read_sql(
            """
            SELECT
            extract(year from m.meas_date) as meas_year,
            avg(meas_value) avg_rain
            FROM core.measurements_t m
            WHERE m.meas_name = 'rzz150mx'
            AND extract(year from m.meas_date) >= 1981
            AND extract(year from m.meas_date) <= 2020
            AND m.valid_to = '2262-04-11'
            GROUP BY meas_year
            """,
            engine
        )

        # simple regression line
        dfScatterRain = dfScatterRain.reset_index()
        reg = LinearRegression().fit(np.vstack(
            dfScatterRain.index),
            dfScatterRain['avg_rain']
        )
        dfScatterRain['rain_bestfit'] = reg.predict(np.vstack(
            dfScatterRain.index)
        )

        meanRain = dfScatterRain['avg_rain'].mean()

        dfScatterRain['dev_rain'] = dfScatterRain['avg_rain'] - meanRain
        dfScatterRain['color'] = np.where(
            dfScatterRain['dev_rain'] >= 0, True, False)

        return (dfScatterRain, meanRain)

    # call start functions
    dfSelection = dfSelectionWrangling()
    dfStations = dfStationsWrangling(dfSelection)
    dfMap = dfMapWrangling(dfStations, snowParam)

    # station selection for all stations
    dfSelectionSnow = dfSelection[dfSelection.meas_name == 'hns000y0']
    dfSelectionSnow = dfSelectionSnow[
        dfSelectionSnow.station_name.isin(list(dfStations.station_name))
    ]
    medianValueTotalSnow = dfSelectionSnow['min'].median()

    # call plot functions
    dfScatterSnow = dfScatterSnowWrangling()
    dfSnowAll = dfSnowAllWrangling(
        dfStations, dfScatterSnow, medianValueTotalSnow
    )
    dfScatterRain, meanRain = dfScatterRainWrangling()

    def plotMapCreation(dfMap, colors):
        # creating the map
        plotMap = go.Figure()
        plotMap.add_trace(go.Scattermapbox(
            lat=dfMap['latitude'],
            lon=dfMap['longitude'],
            hovertemplate=dfMap['text'],
            mode='markers',
            marker={
                'size': 10,
                'color': colors['d3'],
                # 'size': dfMap['avg_now'] * 45,
                # 'sizemin': 3,
                # 'color': (
                #     dfMap['avg_now'] - dfMap['avg_then']
                #     ) / dfMap['avg_then'],
                # 'colorscale': px.colors.diverging.BrBG,
                # 'colorscale': [
                #     [0, colors['rbr']],
                #     [0.50, colors['l6']],
                #     [1, colors['rbb']]
                # ],
                # 'sizemode': 'area',
                'opacity': 0.7
            }
        ))

        plotMap.update_layout(
            title_text='Schneefall',
            hovermode='closest',
            showlegend=False,
            margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
            height=430,
            paper_bgcolor=colors['l0'],
            mapbox_style="open-street-map",
            mapbox=dict(
                accesstoken='pk.eyJ1Ijoiam9lbGdyb3NqZWFuIiwiYSI6ImNrb' +
                '24yNHpsMDA5OXQycXAxaHUzcDBzZHMifQ.TEpFKAlfpsYXKdAvgHYbLQ',
                # bearing=0,
                center=dict(
                    lat=46.9,
                    lon=8.2
                ),
                zoom=6.5,
                style='mapbox://styles/joelgrosjean/' +
                'ckon48gdw1yob17ozstokzg9c'
            )
        )

        return plotMap

    def plotRainCreation(dfScatterRain, meanRain, colors):
        # creating the rain barplot
        plotRain = go.Figure()

        plotRain.add_trace(go.Bar(
            name='Regenfall',
            x=dfScatterRain["meas_year"],
            y=dfScatterRain["dev_rain"],
            base=meanRain,
            marker={
                'color': colors['rbb'],
                # 'line': {'width': 1, 'color': 'black'}
            }
        ))

        plotRain.add_trace(go.Scatter(
            name='Regression',
            x=dfScatterRain["meas_year"],
            y=dfScatterRain["rain_bestfit"],
            mode='lines',
            marker={
                'size': 5,
                'color': colors['rbr'],
                'line': {'width': 1, 'color': 'black'}
            }
        ))

        plotRain.update_layout(
            title='∅ Maximaler Niederschlag aller Stationen in cm',
            title_x=0.05,
            yaxis={
                # 'title': 'maximaler Niederschlag in cm',
                'color': colors['plotAxisTitle'],
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': colors['plotGrid'],
                'range': [
                    dfScatterRain.avg_rain.min() * 0.95,
                    dfScatterRain.avg_rain.max() * 1.05
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

        return plotRain

    def plotSnowCreation(dfSnowAll, colors):
        # creating the snow scatterplot with all stations
        plotSnow = go.Figure()

        plotSnow.add_trace(go.Scatter(
            name='Schneefall',
            x=dfSnowAll['meas_year'],
            y=dfSnowAll['meas_value'],
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

        plotSnow.add_trace(go.Scatter(
            name='Regression',
            x=dfSnowAll['meas_year'],
            y=dfSnowAll['bestfit'],
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

        plotSnow.update_layout(
            title='Durchschnittlicher Schneefall aller Stationen in Meter',
            title_x=0.1,
            margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
            height=360,
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
            legend={
                'yanchor': 'top',
                'y': 0.99,
                'xanchor': 'right',
                'x': 0.99
            }
        )

        return plotSnow

    def createDashboard():

        # call plot creation functions
        plotMap = plotMapCreation(dfMap, colors)
        plotRain = plotRainCreation(dfScatterRain, meanRain, colors)
        plotSnow = plotSnowCreation(dfSnowAll, colors)

        dashApp.layout = html.Div([
            # header
            html.Div([
                html.Div([
                    html.H2(
                        'Erdrutsche und ihre Ursachen',
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
                            'padding-right': 45,
                        }
                    ),
                    html.Div(id='linkDatastoryOutput')
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
            # first row of plots
            html.Div([
                # map top left
                html.Div([
                    html.Div([
                        html.H4(
                            'Landkarte zum Auswählen der Stationen',
                            style={'color': colors['plotTitle']}
                        )
                    ], style={
                        'padding-left': 20,
                        'padding-top': 5,
                        'height': 30,
                    }
                    ),
                    html.Div([
                        dcc.Graph(
                            className='map-plot',
                            id='map1',
                            figure=plotMap,
                            config={
                                'displayModeBar': False,
                                'staticPlot': False
                            }
                        )
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
                    'width': '60%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'left'
                }
                ),
                # second plot first row
                html.Div([
                    html.Div([
                        html.H4("Veränderung des Regenfalls")
                    ], style={
                        'padding-left': 20,
                        'padding-top': 5,
                        'height': 30,
                    }
                    ),
                    html.Div([
                        # html.Div([
                        #     dcc.Graph(
                        #         id='scatterplot1',
                        #         config={
                        #             'displayModeBar': False,
                        #             'staticPlot': False
                        #         }
                        #     )
                        # ], style={
                        #     'backgroundColor': colors['BgPlot2'],
                        #     'width': '70%',
                        #     'display': 'inline-block',
                        #     'position': 'relative',
                        #     'horizontal-align': 'left'
                        # }
                        # ),
                        # html.Div([
                        #     dcc.Dropdown(
                        #         id='yaxis',
                        #         options=[
                        #             {'label': i, 'value': i}
                        #             for i in features
                        #         ],
                        #         value='breclod0'
                        #     ),
                        #     html.H4('Some random text i guess')
                        # ], style={
                        #     'backgroundColor': colors['BgPlot2'],
                        #     'width': '28%',
                        #     'display': 'inline-block',
                        #     'vertical-align': 'top',
                        #     'horizontal-align': 'right',
                        #     'padding': 5
                        # }
                        # )
                    ], style={
                        'backgroundColor': colors['BgPlot2'],
                        'height': 430,
                        'box-shadow': shadow,
                        'position': 'relative',
                        'border-radius': 5,
                        'margin': '10px',
                        'vertical-align': 'top',
                        'padding': '5px'
                    }
                    ),
                ], style={
                    'width': '40%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'right'
                }
                )
            ], style={
                'padding-left': 30,
                'padding-right': 30
            }
            ),
            # second row of plots
            html.Div([
                # 1st plot 2nd row
                html.Div([
                    html.Div([
                        html.H4('Extreme Regenfälle')
                    ], style={
                        'height': 30,
                        'padding-left': 20
                    }
                    ),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='scatterRain',
                                figure=plotRain,
                                config={
                                    'displayModeBar': False,
                                    'staticPlot': False
                                }
                            )
                        ], style={
                            'backgroundColor': colors['BgPlot5'],
                            'height': 360
                        }
                        )
                    ], style={
                        'backgroundColor': colors['BgPlot5'],
                        'height': 370,
                        'box-shadow': shadow,
                        'position': 'relative',
                        'border-radius': 5,
                        'margin': '10px',
                        'vertical-align': 'top',
                        'padding': 5
                    }
                    ),
                ], style={
                    'width': '30%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'right'
                }
                ),
                # 2nd plot 2nd row
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4('Veränderung des Schneefalls')
                        ], style={
                            'padding-left': 20,
                            'width': '70%',
                            'display': 'inline-block',
                            'vertical-align': 'top',
                            # 'horizontal-align': 'left',
                        }
                        ),
                        html.Div([
                            dbc.Button(
                                id='stationsOver1500',
                                n_clicks=0,
                                children='> 1500 m.ü.M.',
                                # style={'fontSize': 12},
                                color='secondary',
                                size="sm",
                            ),
                        ], style={
                            'width': '30%',
                            'display': 'inline-block',
                            'vertical-align': 'top',
                            'text-align': 'right',
                            'padding-right': 10,
                            'padding-bottom': 5,
                            # 'horizontal-align': 'right',
                            # 'justify': 'right'
                            # 'padding-left': 40,
                        }
                        ),
                    ], style={
                            'height': 30,
                        }
                    ),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='scatterplot2',
                                figure=plotSnow,
                                config={
                                    'displayModeBar': False,
                                    'staticPlot': False
                                }
                            )
                        ], style={
                            'backgroundColor': colors['BgPlot3'],
                            'height': 360
                        }
                        )
                    ], style={
                        'backgroundColor': colors['BgPlot3'],
                        'height': 370,
                        'box-shadow': shadow,
                        'position': 'relative',
                        'border-radius': 5,
                        'margin': '10px',
                        'vertical-align': 'top',
                        'padding': 5
                    }
                    ),
                ], style={
                    'width': '40%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'left'
                }
                ),
                # 3rd plot 2nd row
                html.Div([
                    html.Div([
                        html.H4('Durchschnittliche Temperatur')
                    ], style={
                        'height': 30,
                        'padding-left': 20
                    }
                    ),
                    html.Div([], style={
                        'backgroundColor': colors['l0'],
                        'height': 370,
                        'box-shadow': shadow,
                        'position': 'relative',
                        'border-radius': 5,
                        'margin': '10px',
                        'vertical-align': 'top'
                    }
                    ),
                ], style={
                    'width': '30%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'center'
                }
                ),
            ], style={
                'padding-left': 30,
                'padding-right': 30,
                'padding-bottom': 12,
            }
            ),
        ], style={
            'backgroundColor': colors['BgDashboard'],
            'height': '100vh'
        }
        )

    @dashApp.callback(
        Output('linkDatastoryOutput', 'children'),
        [Input('linkDatastory', 'n_clicks')])
    def redirectToStory(n_clicks):
        if n_clicks == 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/", id="hello")

    @dashApp.callback(
        Output('scatterplot2', 'figure'),
        [Input('map1', 'clickData')])
    def callbackSnow(clickData):
        v_index = clickData['points'][0]['pointIndex']
        station = dfMap.iloc[v_index]['station_name']

        dfSnowAll = dfScatterSnow[dfScatterSnow['station_name'] == station]
        dfSnowAll = dfSnowAll.reset_index()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfSnowAll.meas_year), dfSnowAll['meas_value'])
        dfSnowAll['bestfit'] = reg.predict(np.vstack(dfSnowAll.meas_year))

        plotSnow = plotSnowCreation(dfSnowAll, colors)

        plotSnow.update_layout(
            title=f'Durchschnittlicher Schneefall bei {station} in Meter'
        )

        return plotSnow

    # @dashApp.callback(
    #     Output('scatterplot1', 'figure'),
    #     [Input('yaxis', 'value')])
    # def update_graph(yaxis_name):
    #     df = pd.read_sql(
    #         f"""SELECT
    #         AVG(meas_value),
    #         meas_date
    #         FROM core.measurements_t
    #         WHERE meas_name = {"'"+ yaxis_name +"'"}
    #         GROUP BY meas_date""",
    #         engine
    #     )

    #     df = df.reset_index()

    #     # simple regression line
    #     reg = LinearRegression().fit(np.vstack(df.index), df['avg'])
    #     df['bestfit'] = reg.predict(np.vstack(df.index))

    #     fig = {
    #         'data': [go.Scatter(
    #             name=yaxis_name,
    #             x=df["meas_date"],
    #             y=df["avg"],
    #             mode='lines',
    #             marker={
    #                 'size': 5,
    #                 'color': colors['rbb'],
    #                 'line': {'width': 1, 'color': 'black'}
    #             }
    #         ), go.Scatter(
    #             name='regression line',
    #             x=df["meas_date"],
    #             y=df["bestfit"],
    #             mode='lines',
    #             marker={
    #                 'size': 5,
    #                 'color': colors['rbr'],
    #                 'line': {'width': 1, 'color': 'black'}
    #             }
    #         )
    #         ],
    #         'layout': go.Layout(
    #             title='Veränderungen der Variabeln über Zeit',
    #             xaxis={'title': 'time in years'},
    #             yaxis={'title': yaxis_name},
    #             hovermode='closest',
    #             margin={'l': 60, 'b': 60, 't': 50, 'r': 10},
    #             height=420,
    #             paper_bgcolor=colors['BgPlot2'],
    #             plot_bgcolor='rgba(0,0,0,0)',
    #             legend={
    #                 'yanchor': 'top',
    #                 'y': 0.99,
    #                 'xanchor': 'right',
    #                 'x': 0.99
    #             }
    #         )
    #     }

    #     return fig

    # @dashApp.callback(
    #     Output('scatterplot2', 'figure'),
    #     [Input('stationsOver1500', 'n_clicks')])
    # def callback_button(n_clicks):
    #     # creating the snow scatterplot with all stations
    #     plotSnow = go.Figure()

    #     plotSnow.add_trace(go.Scatter(
    #         name='Schneefall',
    #         x=dfSnowO1500['meas_year'],
    #         y=dfSnowO1500['snow'],
    #         mode='lines',
    #         line_shape='spline',
    #         marker={
    #             'size': 5,
    #             'color': colors['rbb'],
    #             'line': {
    #                 'width': 1,
    #                 'color': 'black'
    #             }
    #         }
    #     ))

    #     plotSnow.add_trace(go.Scatter(
    #         name='Regression',
    #         x=dfSnowO1500['meas_year'],
    #         y=dfSnowO1500['bestfit'],
    #         mode='lines',
    #         marker={
    #             'size': 5,
    #             'color': colors['rbr'],
    #             'line': {
    #                 'width': 1,
    #                 'color': 'black'
    #             }
    #         }
    #     ))

    #     plotSnow.update_layout(
    #         title='Durchschnitt aller Stationen oberhalb 1500 m.ü.M.',
    #         margin={'l': 50, 'b': 20, 't': 40, 'r': 10},
    #         height=360,
    #         yaxis={
    #             'title': 'Schneefall (Meter)',
    #             'color': colors['plotAxisTitle'],
    #             'showgrid': True,
    #             'gridwidth': 1,
    #             'gridcolor': colors['plotGrid'],
    #             'rangemode': "tozero"
    #         },
    #         xaxis={
    #             'showgrid': False,
    #             'color': colors['plotAxisTitle']
    #         },
    #         paper_bgcolor=colors['BgPlot3'],
    #         plot_bgcolor='rgba(0,0,0,0)',
    #         legend={
    #             'yanchor': 'bottom',
    #             'y': 0.99,
    #             'xanchor': 'right',
    #             'x': 0.99
    #         }
    #     )

    #     return plotSnow

    createDashboard()
    return dashApp
