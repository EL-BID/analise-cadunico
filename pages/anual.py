import os

import dash
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

dash.register_page(__name__, path='/anual', title='Análise CADÚnico')

# ====================================================
# Layout
# ====================================================

layout = html.Div([

    ## Dropdown
    dbc.Row([
        html.P('Indicador:', style={'text-align':'center'}),
        html.Div(
            dcc.Dropdown(id='seletor-var',
                options={
                    'extrema_pobreza':'Extrema pobreza',
                    'pobreza':'Pobreza',
                    'vulnerabilidade':'Vulnerabilidade',
                    'p.marc_sit_rua':'Situação de rua',
                    'sem renda':'Sem renda',
                    'gini':'Gini',
                },
                value='extrema_pobreza',
                clearable=False,
            ),
        className='col-3 dropdown')
    ]),


    ## Mapa e gráficos
    html.Div([
        html.Div(
            dcc.Graph(id='graph-anual'),
        className='col-lg-10'),
    ], className='row justify-content-center'),
    
])

# ====================================================
# Callbacks
# ====================================================

# Plotar o mapa
@dash.callback(
    Output('graph-anual', 'figure'),
    Input('seletor-var', 'value'),
)
def plotar_grafico_anual(var):
    if var != 'gini':
        df = pq.read_table(data_func.local_df, columns=['ano', var]).to_pandas()
        df = df.groupby('ano')[var].sum()
        graph = data_func.grafico(df, legenda=False)
    else:
        df = pq.read_table(data_func.local_df, columns=['ano', 'd.vlr_renda_total_fam']).to_pandas()
        df = df.groupby('ano', as_index=False)['d.vlr_renda_total_fam'].agg(data_func.gini).rename(columns={'d.vlr_renda_total_fam':'gini'}).set_index('ano')
        graph = data_func.grafico(df, legenda=False, gini=True)
    
    return graph
