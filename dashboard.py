import re
import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash_core_components as dcc
import dash_html_components as html
from dash import Dash
from flask import Flask
from dash.exceptions import PreventUpdate
from sklearn.linear_model import LinearRegression
from dash.dependencies import Input, Output, State

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
            'c1': '#ED90A4',
            'c2': '#ABB150',
            'c3': '#00C1B2',
            'c4': '#ACA2EC',
            'b1': '#ADD8E5',
            'b2': '#BCDFEB',
            'rbb': '#285D8F',
            'rbr': '#DE3143'
        }

    dashApp = Dash(
        __name__,
        server=flaskApp,
        url_base_pathname='/dashboard/',
        external_stylesheets=external_stylesheets
    )

    # data wrangling map data
    df_map_1 = pd.read_sql(
        """
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
        AND m.meas_name = 'hns000d0'
        AND m.valid_to = '2262-04-11'
        AND k.parameter = 'hns000d0'
        AND k.valid_to = '2262-04-11'
        GROUP BY k.station_name,
        k.longitude,
        k.latitude,
        k.elevation;
        """,
        engine
    )

    df_map_2 = pd.read_sql(
        """
        SELECT
        avg(m.meas_value) avg_then,
        k.station_name
        FROM core.measurements_t m
        LEFT JOIN core.station_t k
        ON (m.station = k.station_short_name)
        WHERE m.meas_date >= '1970-01-01'
        AND m.meas_date < '1980-01-01'
        AND m.meas_name = 'hns000d0'
        AND m.valid_to = '2262-04-11'
        AND k.parameter = 'hns000d0'
        AND k.valid_to = '2262-04-11'
        GROUP BY k.station_name
        """,
        engine
    )

    df_map = pd.merge(
        left=df_map_1,
        right=df_map_2,
        left_on='station_name',
        right_on='station_name'
    )

    df_map['text'] = df_map['station_name'] + '<br>Ø Schneefall pro Tag 1970-1980: ' + (round(df_map['avg_then'],2)).astype(str) + 'cm' + '<br>Ø Schneefall pro Tag 2010-2020: ' + (round(df_map['avg_now'],2)).astype(str) + 'cm' + '<br>Veränderung: ' + (round((1 - df_map['avg_then'] / df_map['avg_now']) * 100,0)).astype(str) + '%'
    df_map['lon'] = df_map['longitude'].str.extract(r'(\d+).$')
    df_map['lon'] = pd.to_numeric(df_map['lon'])
    df_map['lon'] = round(df_map['lon']/60  * 1000)
    df_map['lon'] = df_map['lon'].apply(str)
    df_map['longitude'] = df_map['longitude'].str.extract(r'(^\d+)') + '.' + df_map['lon'].str.extract(r'(^\d+)')
    df_map = df_map.drop('lon', axis = 1)
    df_map['lat'] = df_map['latitude'].str.extract(r'(\d+).$')
    df_map['lat'] = pd.to_numeric(df_map['lat'])
    df_map['lat'] = round(df_map['lat']/60  * 1000)
    df_map['lat'] = df_map['lat'].apply(str)
    df_map['latitude'] = df_map['latitude'].str.extract(r'(^\d+)') + '.' + df_map['lat'].str.extract(r'(^\d+)')
    df_map = df_map.drop('lat', axis = 1)

    # data wrangling scatterplot
    dfScatter = pd.read_sql(
        """
        SELECT extract(year from m.meas_date) as meas_year,
        sum(m.meas_value) snow,
        k.station_name
        FROM core.measurements_t m
        JOIN core.station_t k
        ON (m.station = k.station_short_name)
        WHERE m.meas_name = 'hns000d0'
        AND k.parameter = 'hns000d0'
        GROUP BY meas_year, k.station_name
        ORDER BY meas_year ASC
        """,
        engine
    )

    def createDashboard():
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
        
        plotMap = go.Figure()

        plotMap.add_trace(go.Scattergeo(
            # locationmode='country names', # if locationmode and locations are active, one can see adelboden
            # locations=['Switzerland'], # puts point in the middle of country
            lon=df_map["longitude"],
            lat=df_map["latitude"],
            text=df_map['text'],
            mode='markers',
            marker={
                'size': df_map['avg_now'] * 15,
                'color': df_map['avg_now'] - df_map['avg_then'],
                'line': {'width': 1, 'color': 'black'},
                'sizemode': 'area'
            }
        ))

        plotMap.update_layout(
            title_text='Schneefall',
            hovermode='closest',
            margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
            height=400,
            paper_bgcolor=colors['b1'],
            geo=dict(
                scope='europe', # changes layout so one can see only europe and borders
                landcolor='rgb(217, 217, 217)',
                lonaxis_range=[5.7, 10.6],
                lataxis_range=[45.7, 47.9]
            )
        )

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
                        style={'color': colors['l1']}
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
                ),
                html.Div(id='linkDatastoryOutput')
            ], style={
                'backgroundColor': colors['d3'],
                'box-shadow': '4px 4px 4px lightgrey',
                'position': 'relative',
                'padding': '5px'
            }
            ),
            # first row of plots
            html.Div([
                html.Div([], style={
                    'width': '5%',
                    'display': 'inline-block'
                }),
                # map top left
                html.Div([
                    html.Div([
                        html.H4('Karte mit Schneetagen pro Station')
                    ]),
                    html.Div([
                        dcc.Graph(
                            id='map1',
                            figure=plotMap,
                            config={
                                'displayModeBar': False,
                                'staticPlot': False
                            }
                        )
                    ], style={
                        'backgroundColor': colors['l0'],
                        'height': 400,
                        'box-shadow': '8px 8px 8px lightgrey',
                        'position': 'relative',
                        'border-radius': 15,
                        'margin': '10px'
                    }
                    ),
                ], style={
                    'width': '37.5%',
                    'display': 'inline-block',
                    'vertical-align': 'top'
                }
                ),
                html.Div([
                    html.H4("Totaler Schneefall und Regenfall or Temp"),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='scatterplot1',
                                config={
                                    'displayModeBar': False,
                                    'staticPlot': False
                                }
                            )
                        ], style={
                            'backgroundColor': colors['l4'],
                            'width': '70%',
                            'display': 'inline-block',
                            'position': 'relative',
                            'border-radius': 15
                        }
                        ),
                        html.Div([
                            dcc.Dropdown(
                                id='yaxis',
                                options=[
                                    {'label': i, 'value': i}
                                    for i in features
                                ],
                                value='breclod0'
                            ),
                            html.H4('Some random text i guess')
                        ], style={
                            'backgroundColor': colors['l0'],
                            'width': '25%',
                            'padding': '10px',
                            'display': 'inline-block',
                            'vertical-align': 'top'
                        }
                        )
                    ], style={
                        'backgroundColor': colors['l0'],
                        'height': 400,
                        'box-shadow': '8px 8px 8px lightgrey',
                        'position': 'relative',
                        'border-radius': 15,
                        # 'padding': '10px',
                        'margin': '10px',
                        'vertical-align': 'top'
                    }
                    ),
                ], style={
                    'width': '45%',
                    'display': 'inline-block',
                    'vertical-align': 'top'
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
                # scatterplot bottom left
                html.Div([
                    html.H4('Schnee- & Regenfall bei Stationen'),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='scatterplot2',
                                config={
                                    'displayModeBar': False,
                                    'staticPlot': False
                                }
                            )
                        ], style={
                            'backgroundColor': colors['l4'],
                            'border-radius': 15,
                            'height': 335
                        }
                        )
                    ], style={
                        'backgroundColor': colors['l0'],
                        'height': 335,
                        'box-shadow': '8px 8px 8px lightgrey',
                        'position': 'relative',
                        'border-radius': 15,
                        'margin': '10px',
                        'vertical-align': 'top'
                    }
                    ),
                ], style={
                    'width': '40%',
                    'display': 'inline-block',
                    'vertical-align': 'top'
                }
                ),
                # 2nd plot 2nd row
                html.Div([
                    html.H4('Bodentemperatur'),
                    html.Div([], style={
                        'backgroundColor': colors['l0'],
                        'height': 335,
                        'box-shadow': '8px 8px 8px lightgrey',
                        'position': 'relative',
                        'border-radius': 15,
                        'margin': '10px',
                        'vertical-align': 'top'
                    }
                    ),
                ], style={
                    'width': '20.15%',
                    'display': 'inline-block',
                    'vertical-align': 'top'
                }
                ),
                # 3nd plot 2nd row
                html.Div([
                    html.H4('Extreme Regenfälle'),
                    html.Div([
                    ], style={
                        'backgroundColor': colors['l0'],
                        'height': 335,
                        'box-shadow': '8px 8px 8px lightgrey',
                        'position': 'relative',
                        'border-radius': 15,
                        'margin': '10px',
                    }
                    ),
                ], style={
                    'width': '20.15%',
                    'display': 'inline-block',
                    'vertical-align': 'top'
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
        Output('linkDatastoryOutput', 'children'),
        [Input('linkDatastory', 'n_clicks')])
    def redirectToStory(n_clicks):
        if n_clicks is 0:
            raise PreventUpdate
        else:
            return dcc.Location(pathname="/", id="hello")

    @dashApp.callback(
        Output('scatterplot1', 'figure'),
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

        # simple regression line
        reg = LinearRegression().fit(np.vstack(df.index), df['avg'])
        df['bestfit'] = reg.predict(np.vstack(df.index))

        return {
            'data': [go.Scatter(
                name=yaxis_name,
                x=df["meas_date"],
                y=df["avg"],
                mode='lines+markers',
                marker={
                    'size': 5,
                    'color': colors['rbb'],
                    'line': {'width': 1, 'color': 'black'}
                }
            ), go.Scatter(
                name='regression line',
                x=df["meas_date"],
                y=df["bestfit"],
                mode='lines',
                marker={
                    'size': 5,
                    'color': colors['rbr'],
                    'line': {'width': 1, 'color': 'black'}
                }
            )
            ],
            'layout': go.Layout(
                title='Veränderungen der Variabeln über Zeit',
                xaxis={'title': 'time in years'},
                yaxis={'title': yaxis_name},
                hovermode='closest',
                margin={'l': 60, 'b': 60, 't': 50, 'r': 10},
                height=400,
                paper_bgcolor=colors['b1'],
                plot_bgcolor='rgba(0,0,0,0)',
                legend={
                    'yanchor': 'top',
                    'y': 0.99,
                    'xanchor': 'right',
                    'x': 0.99
                }
            )
        }

    # TODO Store in callback which station is selected and then use this information as input in scatterplot function
    # use dcc.Store() for this

    # TODO maybe my callback just has the wrong indentation.

    @dashApp.callback(
        Output('scatterplot2', 'figure'),
        [Input('map1', 'hoverData')])
    def callback_graph(hoverData):
        v_index = hoverData['points'][0]['pointIndex']
        station = df_map.iloc[v_index]['station_name']
        
        # hns000d0
        # rre150m0

        dfTemp = dfScatter[dfScatter['station_name'] == station]

        fig = {
            'data': [go.Scatter(
                x = dfTemp['meas_year'],
                y = dfTemp['snow'],
                mode='lines+markers',
                margin={'l': 60, 'b': 60, 't': 50, 'r': 10},
                height=400
            )],
            'layout': go.Layout(
                title = station,
                # xaxis = {'visible':True, 'title': 'seconds'},
                # yaxis = {'visible':True, 'title': 'time','range':[0,60/df['acceleration'].min()]}
            )
        }
        return fig


    createDashboard()
    return dashApp
