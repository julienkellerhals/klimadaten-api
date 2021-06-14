import dash_html_components as html
import dash_bootstrap_components as dbc

rainParam = 'rre150y0'
snowParam = 'hns000y0'
rainExtremeParam = 'rhh150mx'
temperatureParam = 'tre200y0'

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
    'BgStory': '#FFFFFF',
    'shadow': '#C5D1D8'
}

shadow = f'7px 7px 7px {colors["shadow"]}'


def createLayout():
    layout = html.Div(
        [],
        style={
            'height': '100vh',
            'display': 'flex',
            'flex-direction': 'column',
        }
    )
    return layout


def createHeader(title, active):
    header = html.Div([
        html.Div([
            html.H2(
                title,
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
                    'padding-right': 30,
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
    )

    if active == "story":
        header.children[1].children[1].style["font-weight"] = "bold"
    elif active == "dashboard":
        header.children[1].children[0].style["font-weight"] = "bold"
    else:
        raise NotImplementedError

    return header
