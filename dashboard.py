import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from flask import Flask

def create_dashapp(server):
    app = dash.Dash(
        server=server,
        url_base_pathname='/dashapp/'
    )
    app.config['suppress_callback_exceptions'] = True
    app.title='Dash App'

    # Set the layout
    app.layout = html.Div([
        html.Br(), ' This is the outermost div!', html.Br(),'-',
        html.Div([
            'This is an inner div!'],
            style={
                'color': 'red',
                'border': '2px red solid'}),
        html.Div([
            'This is an inner div!'],
            style={
                'color': 'blue',
                'border': '2px blue solid'})], 
        style={
            'textAlign': 'center', 
            'color': 'green',
            'border': '2px green solid'})

    # Register callbacks here if you want...
    
    return app.run_server(debug=True)
    #return app.server