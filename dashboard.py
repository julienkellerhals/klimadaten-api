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

"""
Parameters in database

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
awesome color scale

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

    textDescription = """
        Erdrutsche werden in den kommenden Jahrzehnten wahrscheinlich 
        häuffiger. Dieses Dashboard visualisiert die Ursachen von Erdrutschen. 
        Durch die sich beschleunigende Gletscherschmelze und das langsame 
        Auftauen des Permafrosts, wird das Risiko für Erdrutsche grösser. Die 
        generell zunehmende Temperatur ist Grund dafür. Das Risiko von 
        Hangrutschungen wird zudem durch die mögliche Zunahme von 
        Starkniederschlägen und durch den Anstieg der Schneefallgrenze erhöht.
        """

    textStationAll = """
        Momentan werden die Daten für folgende Stationen angezeigt:
        """

    textStationOne = """
        Momentan werden die Daten für folgende Stationen angezeigt:
        """

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
        'blue': '#285D8F',
        'red': '#DE3143',
        'lightblue': '#B4DFFF',
        'BgPlot1': '#FFFFFF',
        'BgPlot2': '#FFFFFF',
        'BgPlot3': '#FFFFFF',
        'BgPlot4': '#ADD8E5',
        'BgPlot5': '#FFFFFF',
        'plotTitle': '#121F26',
        'plotGrid': '#B6C3CC',
        'plotAxisTitle': '#748B99',
        'BgDashboard': '#E2E8ED',
        'shadow': '#C5D1D8'
    }

    snowParam = 'hns000y0'
    rainParam = 'rre150y0'
    rainExtremeParam = 'rhh150yx'
    temperatureParam = 'tre200y0'
    shadow = f'7px 7px 10px {colors["shadow"]}'

    # plot titles
    titleRainExtreme = '∅ Maximaler Niederschlag aller Stationen'
    titleTemperature = 'Durchschnittliche Temperature aller Stationen'
    titleSnow = 'Durchschnittlicher Schneefall aller Stationen'
    titleRain = 'Durchschnittlicher Regenfall aller Stationen'

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
            """,
            engine
        )

        # dfMap1 = pd.read_sql(
        #     f"""
        #     SELECT
        #     avg(m.meas_value) avg_now,
        #     k.station_name,
        #     k.longitude,
        #     k.latitude,
        #     k.elevation
        #     FROM core.measurements_t m
        #     LEFT JOIN core.station_t k
        #     ON (m.station = k.station_short_name)
        #     WHERE m.meas_date >= '2010-01-01'
        #     AND m.meas_date < '2020-01-01'
        #     AND m.meas_name = {"'"+ snowParam +"'"}
        #     AND k.parameter = {"'"+ snowParam +"'"}
        #     AND m.valid_to = '2262-04-11'
        #     AND k.valid_to = '2262-04-11'
        #     GROUP BY k.station_name,
        #     k.longitude,
        #     k.latitude,
        #     k.elevation;
        #     """,
        #     engine
        # )

        # dfMap2 = pd.read_sql(
        #     f"""
        #     SELECT
        #     avg(m.meas_value) avg_then,
        #     k.station_name
        #     FROM core.measurements_t m
        #     LEFT JOIN core.station_t k
        #     ON (m.station = k.station_short_name)
        #     WHERE m.meas_date >= '1970-01-01'
        #     AND m.meas_date < '1980-01-01'
        #     AND m.meas_name = {"'"+ snowParam +"'"}
        #     AND k.parameter = {"'"+ snowParam +"'"}
        #     AND m.valid_to = '2262-04-11'
        #     AND k.valid_to = '2262-04-11'
        #     GROUP BY k.station_name
        #     """,
        #     engine
        # )

        # dfMap = pd.merge(
        #     how='inner',
        #     left=dfMap1,
        #     right=dfMap2,
        #     left_on='station_name',
        #     right_on='station_name'
        # )

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

        # dfMap['text'] = '<b>' + dfMap['station_name'] + '</b>' +\
        #     ' (' + (dfMap['elevation']).astype(str) + ' m.ü.M.)' + \
        #     '<br>Ø Schneefall pro Tag 1970-1980: ' + \
        #     (round(dfMap['avg_then'], 2)).astype(str) + 'cm' + \
        #     '<br>Ø Schneefall pro Tag 2010-2020: ' + \
        #     (round(dfMap['avg_now'], 2)).astype(str) + 'cm' + \
        #     '<br>Veränderung: ' + \
        #     (round(((
        #         dfMap['avg_now'] - dfMap['avg_then']) / dfMap['avg_then']
        #     ) * 100, 0)).astype(str) + '%' + '<extra></extra>'

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
            """,
            engine
        )
        dfScatter = dfScatter.dropna()

        return dfScatter

    def dfScatterAllWrangling(dfStations, dfScatter, yearParam):
        dfAll = pd.merge(
            how='inner',
            left=dfStations,
            right=dfScatter,
            left_on='station_short_name',
            right_on='station'
        )

        dfAll.sort_values([
            'station_short_name',
            'meas_year'
        ], inplace=True)

        # select all Stations
        dfParamAll = dfAll.groupby(
            'meas_year'
        ).agg(
            meas_value=('meas_value', 'mean')
        )

        dfParamAll = dfParamAll.reset_index()
        dfParamAll = dfParamAll[dfParamAll.meas_year >= yearParam]

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfParamAll.index), dfParamAll['meas_value'])
        dfParamAll['bestfit'] = reg.predict(np.vstack(dfParamAll.index))

        return dfParamAll

    def dfBarAllWrangling(
        dfStations,
        dfScatter,
        yearParam
    ):
        dfAll = pd.merge(
            how='inner',
            left=dfStations,
            right=dfScatter,
            left_on='station_short_name',
            right_on='station'
        )

        dfAll.sort_values([
            'station_short_name',
            'meas_year'
        ], inplace=True)

        # select all Stations
        dfParamAll = dfAll.groupby(
            'meas_year'
        ).agg(
            meas_value=('meas_value', 'mean')
        )

        meanRain = dfParamAll['meas_value'].mean()
        dfParamAll['deviation'] = dfParamAll[
            'meas_value'] - meanRain
        dfParamAll['color'] = np.where(
            dfParamAll['deviation'] >= 0, True, False)

        dfParamAll = dfParamAll.reset_index()
        # TODO fix param and desc
        dfParamAll = dfParamAll[
            dfParamAll.meas_year >= yearParam]

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(
                dfParamAll.index), dfParamAll['meas_value'])
        dfParamAll['bestfit'] = reg.predict(
            np.vstack(dfParamAll.index))

        return (dfParamAll, meanRain)

    def getParamYear(dfSelection, short_name):
        dfSelectionParam = dfSelection[dfSelection.meas_name == short_name]
        dfSelectionParam = dfSelectionParam[
            dfSelectionParam.station_name.isin(list(dfStations.station_name))
        ]
        yearParam = dfSelectionParam['min'].median()

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
    dfSnowAll = dfScatterAllWrangling(
        dfStations, dfScatterSnow, yearSnow
    )
    dfScatterRain = dfScatterWrangling(rainParam)
    dfRainAll = dfScatterAllWrangling(
        dfStations, dfScatterRain, yearRain
    )
    dfScatterRainExtreme = dfScatterWrangling(rainExtremeParam)
    dfRainExtremeAll, meanRain = dfBarAllWrangling(
        dfStations, dfScatterRainExtreme, yearRainExtreme
    )
    dfScatterTemperature = dfScatterWrangling(temperatureParam)
    dfTemperatureAll, meanTemperature = dfBarAllWrangling(
        dfStations, dfScatterTemperature, yearTemperature
    )

    # functions for plot creation
    def plotMapCreation(dfMap, colors):
        # creating the map
        plot = go.Figure()
        plot.add_trace(go.Scattermapbox(
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
                #     [0, colors['red']],
                #     [0.50, colors['l6']],
                #     [1, colors['blue']]
                # ],
                # 'sizemode': 'area',
                'opacity': 0.7
            }
        ))

        plot.update_layout(
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

        return plot

    def plotBarCreation(df, meanRain, colors, suffix):
        # creating the rain barplot
        plot = go.Figure()

        plot.add_trace(go.Bar(
            name='Regenfall',
            x=df["meas_year"],
            y=df["deviation"],
            base=meanRain,
            marker={
                'color': colors['blue'],
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
                'color': colors['red'],
                'line': {'width': 1, 'color': 'black'}
            }
        ))

        plot.update_layout(
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
            margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
            height=360,
            paper_bgcolor=colors['BgPlot5'],
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            legend={
                'yanchor': 'top',
                'y': 0.99,
                'xanchor': 'left',
                'x': 0.01
            }
        )

        return plot

    def plotScatterCreation(df, colors, suffix):
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
                'color': colors['blue'],
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
                'color': colors['red'],
                'line': {
                    'width': 1,
                    'color': 'black'
                }
            }
        ))

        plot.update_layout(
            title_x=0.1,
            margin={'l': 20, 'b': 20, 't': 40, 'r': 20},
            height=360,
            yaxis={
                # 'title': 'Schneefall (Meter)',
                'color': colors['plotAxisTitle'],
                'showgrid': True,
                'gridwidth': 1,
                'gridcolor': colors['plotGrid'],
                # 'rangemode': "tozero",
                'ticksuffix': ' ' + suffix
            },
            xaxis={
                'showgrid': False,
                'color': colors['plotAxisTitle'],
                'showline': True,
                'linecolor': colors['plotGrid']
            },
            paper_bgcolor=colors['BgPlot3'],
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            legend={
                'yanchor': 'top',
                'y': 0.99,
                'xanchor': 'right',
                'x': 0.99
            }
        )

        return plot

    # main dashboard function
    def createDashboard():

        # call plot creation functions
        plotMap = plotMapCreation(dfMap, colors)
        plotRainExtreme = plotBarCreation(
            dfRainExtremeAll,
            meanRain,
            colors,
            'cm'
        )
        plotRainExtreme.update_layout(
            title=titleRainExtreme,
        )
        plotTemperature = plotBarCreation(
            dfTemperatureAll,
            meanTemperature,
            colors,
            '°C'
        )
        plotTemperature.update_layout(
            title=titleTemperature,
            # title_font_size='40%'
        )
        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')
        plotSnow.update_layout(
            title=titleSnow,
            yaxis={
                'rangemode': "tozero",
            },
        )
        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')
        plotRain.update_layout(
            title=titleRain,
            height=420,
        )

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
                # 1st plot 1st row
                html.Div([
                    html.Div([
                        html.H4('Beschreibung')
                    ], style={
                        'padding-left': 20,
                        'padding-top': 5,
                        'height': 30,
                    }
                    ),
                    html.Div([
                        # dbc.Container([
                        #     dbc.Row([
                        #         dbc.Col(
                        #             html.Div(
                        #                 html.H1(
                        #                     "Scrollbars",
                        #                     className="text-center"
                        #                 ),
                        #                 className="p-3 gradient",
                        #             ),
                        #             width=6,
                        #             style={
                        #                 "overflow": "scroll",
                        #                 "height": "400px"
                        #             },
                        #         ),
                        #         dbc.Col(
                        #             html.Div(
                        #                 html.H1(
                        #                     "No scrollbars",
                        #                     className="text-center"
                        #                 ),
                        #                 className="p-3 gradient",
                        #             ),
                        #             width=6,
                        #             style={
                        #                 "overflow": "scroll",
                        #                 "height": "400px"
                        #             },
                        #             className="no-scrollbars",
                        #         ),
                        #     ])
                        # ]),
                        html.Div([
                            dcc.Markdown(textDescription),
                        ], style={
                            'maxHeight': 256,
                            'overflowY': 'auto'
                        }
                        ),
                        html.Div([
                            dcc.Markdown(textStationAll),
                            dcc.Markdown('# alle Stationen', id='name'),
                            dcc.Markdown('', id='MASL'),
                        ], style={
                            'maxHeight': 160,
                            'overflowY': 'auto'
                        }
                        ),

                    ], style={
                        'backgroundColor': colors['BgPlot2'],
                        'height': 430,
                        'box-shadow': shadow,
                        'position': 'relative',
                        'border-radius': 5,
                        'margin': '10px',
                        'vertical-align': 'top',
                        'padding': '10px'
                    }
                    ),
                ], style={
                    'width': '25%',
                    'display': 'inline-block',
                    'vertical-align': 'top',
                    'horizontal-align': 'center'
                }
                ),
                # 2nd plot 1st row
                html.Div([
                    html.Div([
                        html.H4(
                            'Landkarte zum Auswählen der Stationen',
                            style={'color': colors['plotTitle']}
                        ),
                        html.Div(
                            id='intermediateValue',
                            style={'display': 'none'}
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
                            'position': 'fixed',
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
                    'vertical-align': 'top',
                    'horizontal-align': 'left'
                }
                ),
                # 3rd plot first row
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
                            'backgroundColor': colors['BgPlot3'],
                            'height': 420
                        }
                        )
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
                                id='plotRainExtreme',
                                figure=plotRainExtreme,
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
                        html.H4('Veränderung des Schneefalls')
                    ], style={
                        'height': 30,
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
        Output('intermediateValue', 'children'),
        Output('name', 'children'),
        Output('MASL', 'children'),
        [Input('plotMap', 'clickData')])
    def callbackMap(clickData):
        v_index = clickData['points'][0]['pointIndex']
        station = dfMap.iloc[v_index]['station_name']
        elevation = dfMap.iloc[v_index]['elevation']
        elevation = re.findall(r'^\d*', str(elevation))[0]
        stationString = f'# {station}'
        elevationString = f'#### {elevation} m.ü.M.'
        return (station, stationString, elevationString)

    @dashApp.callback(
        Output('plotSnow', 'figure'),
        [Input('intermediateValue', 'children')])
    def callbackSnow(station):
        dfSnowAll = dfScatterSnow[dfScatterSnow['station_name'] == station]
        dfSnowAll = dfSnowAll.reset_index()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfSnowAll.meas_year), dfSnowAll['meas_value'])
        dfSnowAll['bestfit'] = reg.predict(np.vstack(dfSnowAll.meas_year))

        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')

        plotSnow.update_layout(
            title=f'Durchschnittlicher Schneefall bei {station}',
            yaxis={
                'rangemode': "tozero",
            },
        )

        return plotSnow

    @dashApp.callback(
        Output('plotRain', 'figure'),
        [Input('intermediateValue', 'children')])
    def callbackRain(station):
        dfRainAll = dfScatterRain[dfScatterRain['station_name'] == station]
        dfRainAll = dfRainAll.reset_index()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(dfRainAll.meas_year), dfRainAll['meas_value'])
        dfRainAll['bestfit'] = reg.predict(np.vstack(dfRainAll.meas_year))

        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')

        plotRain.update_layout(
            title=f'Durchschnittlicher Regenfall bei {station}',
            height=420,
        )

        return plotRain

    @dashApp.callback(
        Output('plotRainExtreme', 'figure'),
        [Input('intermediateValue', 'children')])
    def callbackRainExtreme(station):
        dfRainExtremeAll = dfScatterRainExtreme[
            dfScatterRainExtreme['station_name'] == station]
        dfRainExtremeAll = dfRainExtremeAll.reset_index()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(
                dfRainExtremeAll.meas_year),
                dfRainExtremeAll['meas_value']
            )
        dfRainExtremeAll['bestfit'] = reg.predict(
            np.vstack(dfRainExtremeAll.meas_year)
        )

        meanRain = dfRainExtremeAll['meas_value'].mean()
        dfRainExtremeAll['deviation'] = dfRainExtremeAll[
            'meas_value'] - meanRain
        dfRainExtremeAll['color'] = np.where(
            dfRainExtremeAll['deviation'] >= 0, True, False)

        plotRainExtreme = plotBarCreation(
            dfRainExtremeAll, meanRain, colors, 'cm'
        )

        plotRainExtreme.update_layout(
            title=f'∅ Maximaler Niederschlag bei {station}'
        )

        return plotRainExtreme

    @dashApp.callback(
        Output('plotTemperature', 'figure'),
        [Input('intermediateValue', 'children')])
    def callbackTemperature(station):
        dfTemperatureAll = dfScatterTemperature[
            dfScatterTemperature['station_name'] == station]
        dfTemperatureAll = dfTemperatureAll.reset_index()

        # simple regression line
        reg = LinearRegression(
            ).fit(np.vstack(
                dfTemperatureAll.meas_year),
                dfTemperatureAll['meas_value']
            )
        dfTemperatureAll['bestfit'] = reg.predict(
            np.vstack(dfTemperatureAll.meas_year)
        )

        meanRain = dfTemperatureAll['meas_value'].mean()
        dfTemperatureAll['deviation'] = dfTemperatureAll[
            'meas_value'] - meanRain
        dfTemperatureAll['color'] = np.where(
            dfTemperatureAll['deviation'] >= 0, True, False)

        plotTemperature = plotBarCreation(
            dfTemperatureAll, meanRain, colors, '°C'
        )

        plotTemperature.update_layout(
            title=f'Durchschnittliche Temperature bei {station}'
        )

        return plotTemperature

    @dashApp.callback(
        Output('plotRainExtreme', 'figure'),
        Output('plotTemperature', 'figure'),
        Output('plotSnow', 'figure'),
        Output('plotRain', 'figure'),
        Output('name', 'children'),
        Output('MASL', 'children'),
        [Input('allStations', 'n_clicks')])
    def callbackAllStations(n_clicks):
        plotRainExtreme = plotBarCreation(
            dfRainExtremeAll,
            meanRain,
            colors,
            'cm'
        )
        plotRainExtreme.update_layout(
            title=f'∅ Maximaler Niederschlag aller Stationen',
        )
        plotTemperature = plotBarCreation(
            dfTemperatureAll,
            meanTemperature,
            colors,
            '°C'
        )
        plotTemperature.update_layout(
            title=f'Durchschnittliche Temperature aller Stationen',
        )
        plotSnow = plotScatterCreation(dfSnowAll, colors, 'm')
        plotSnow.update_layout(
            title=f'Durchschnittlicher Schneefall aller Stationen',
            yaxis={
                'rangemode': "tozero",
            },
        )
        plotRain = plotScatterCreation(dfRainAll, colors, 'mm')
        plotRain.update_layout(
            title=f'Durchschnittlicher Regenfall aller Stationen',
            height=420,
        )

        stationString = f'# alle Stationen'
        elevationString = ''

        return (
            plotRainExtreme,
            plotTemperature,
            plotSnow,
            plotRain,
            stationString,
            elevationString
        )

    createDashboard()
    return dashApp
