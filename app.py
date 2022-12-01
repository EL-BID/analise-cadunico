'''
Arquivo principal do dashboard do CADÚnico

author: Rubens Lopes
date: 2022-08-09
'''

import os

import dash
import dash_auth
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

import pyarrow.parquet as pq
import pandas as pd
import numpy as np

import plotly.graph_objects as go
import plotly.express as px

from aux import data_func

# ====================================================
# App
# ====================================================

app = Dash(__name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="Análise CADÚnico",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.config.suppress_callback_exceptions=True

server = app.server

# ====================================================
# Layout
# ====================================================

app.layout = html.Div([
    html.Header([
        html.Div([
            html.Div(
                html.Img(src = app.get_asset_url('bid branco.svg'), className='app-logo'),
            className='col-6 col-lg-4 coluna-logo-bid'),
            html.A(html.H1("Análise CADÚnico"), href='/', className='col-12 col-lg-4 app-title'),
            html.Div(
                html.Img(src = app.get_asset_url('logo_napcd.png'), className='app-logo'),
            className='col-6 col-lg-4 coluna-logo-napcd'),
        ], className='row'),
    ]),

    dbc.Nav([
        dbc.NavItem(dbc.NavLink("Comparativo", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("Análise mensal", href="/analise", active="exact")),
        dbc.NavItem(dbc.NavLink("Análise anual", href="/anual", active="exact")),
        dbc.NavItem(dbc.NavLink("Superação", href="/superacao", active="exact")),
        dbc.NavItem(dbc.NavLink("Informações", href="/info", active="exact")),
    ], fill=True, justified=True, className="sub-header"),

    html.Div(dash.page_container, className='page-container'),

    html.Footer(
        html.P("Todos os direitos reservados - 2022"),
    ),

])

# ====================================================
# Iniciando app
# ====================================================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8000', debug=True if os.uname().sysname == 'Darwin' else False)