import numpy as np
import pandas as pd
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc


def init_dashboard(server):
    """Create a Plotly Dash dashboard."""
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
            'https://fonts.googleapis.com/css?family=Lato'
        ]
    )


    # Create Layout
    dash_app.layout = html.Div([
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

    return dash_app.server