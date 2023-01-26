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

dash.register_page(__name__, path='/', title='Análise CADÚnico')

# ====================================================
# Layout
# ====================================================

layout = html.Div([

    ## Dropdown
    dbc.Row(
        html.Div(
            dcc.Dropdown(id='seletor-ano',
                options=data_func.anos,
                value=2022,
                clearable=False,
            ),
        className='col-3 dropdown')
    ),

    ## Mapas choropleth
    html.Div([
        html.Div([
            html.H2('Pobreza'),
            html.P(id='num-pobreza', className='rodape-bairros'),
            dcc.Loading(dcc.Graph(id='mapa-pobreza', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
        html.Div([
            html.H2('Extrema Pobreza'),
            html.P(id='num-ext-pobreza', className='rodape-bairros'),
            dcc.Loading(dcc.Graph(id='mapa-ext-pobreza', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
    ], className='row row-mapas'),

    html.Div([
        html.Div([
            html.H2('Vulnerabilidade'),
            html.P(id='num-vulnerabilidade', className='rodape-bairros'),
            dcc.Loading(dcc.Graph(id='mapa-vulnerabilidade', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
        html.Div([
            html.H2('Sem renda'),
            html.P(id='num-sem-renda', className='rodape-bairros'),
            dcc.Loading(dcc.Graph(id='mapa-sem-renda', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
    ], className='row row-mapas'),
    
    html.Div([
        html.Div([
            html.H2('Situação de rua'),
            html.P(id='num-rua', className='rodape-bairros'),
            dcc.Loading(dcc.Graph(id='mapa-rua', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
        html.Div([
            html.H2('Coeficiente de Gini'),
            dcc.Loading(dcc.Graph(id='mapa-gini', className='mapas-choropleth')),
        ], className='col-md-6 g-0 div-mapas-choropleth pull-up'),
    ], className='row row-mapas'),

    html.Div(id='empty-bairros')
])

# ====================================================
# Callbacks
# ====================================================

# Plotar os mapas
@dash.callback(
    Output('mapa-pobreza', 'figure'),
    Output('mapa-ext-pobreza', 'figure'),
    Output('mapa-vulnerabilidade', 'figure'),
    Output('mapa-sem-renda', 'figure'),
    Output('mapa-rua', 'figure'),
    Output('mapa-gini', 'figure'),
    Output('num-pobreza', 'children'),
    Output('num-ext-pobreza', 'children'),
    Output('num-vulnerabilidade', 'children'),
    Output('num-sem-renda', 'children'),
    Output('num-rua', 'children'),
    Input('seletor-ano', 'value'),
)
def plotar_mapas_choropleth(ano):

    ## Lendo e ajustando dados

    # gini = data_func.df.loc[data_func.df['ano']==ano]
    gini = pq.read_table(data_func.local_df, columns=['ano', 'd.vlr_renda_total_fam', 'Nome do bairro'], filters=[('ano','=',ano)] ).to_pandas()
    gini = gini[['ano', 'd.vlr_renda_total_fam', 'Nome do bairro']].groupby(['ano', 'Nome do bairro'], as_index=False)['d.vlr_renda_total_fam'].agg(data_func.gini).rename(columns={'d.vlr_renda_total_fam':'gini'}).set_index('ano')
    
    domic_renda = pq.read_table(data_func.local_df, columns=['Nome do bairro', 'data_mes', 'sem renda', 'renda até 3k'], filters=[('ano', '=', ano)]).to_pandas().groupby('Nome do bairro')[['sem renda', 'renda até 3k']].sum()

    df = pq.read_table(data_func.local_df, columns=['Nome do bairro', 'pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua', 'd.vlr_renda_total_fam', 'ano']).to_pandas()
    df = df.loc[df['ano']==ano]
    df = df.groupby('Nome do bairro', as_index=False)[['pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua', 'd.vlr_renda_total_fam']].sum()
    df = df.merge(domic_renda, on='Nome do bairro', how='outer')
    df = df.merge(gini, on='Nome do bairro', how='outer')

    mapa_pobreza = data_func.mapa_choropleth(df[['Nome do bairro', 'pobreza']].rename(columns={'pobreza':'valor'}), 'Nome do bairro')
    num_pobreza = f"Total: {df['pobreza'].sum():,} pessoas".replace(',','.')

    mapa_extrema_pobreza = data_func.mapa_choropleth(df[['Nome do bairro', 'extrema_pobreza']].rename(columns={'extrema_pobreza':'valor'}), 'Nome do bairro')
    num_ext_pobreza = f"Total: {df['extrema_pobreza'].sum():,} pessoas".replace(',','.')

    mapa_vulnerabilidade = data_func.mapa_choropleth(df[['Nome do bairro', 'vulnerabilidade']].rename(columns={'vulnerabilidade':'valor'}), 'Nome do bairro')
    num_vulnerabilidade = f"Total: {df['vulnerabilidade'].sum():,} pessoas".replace(',','.')

    mapa_sem_renda = data_func.mapa_choropleth(df[['Nome do bairro', 'sem renda']].rename(columns={'sem renda':'valor'}), 'Nome do bairro')
    num_sem_renda = f"Total: {df['sem renda'].sum():,} pessoas".replace(',','.')

    mapa_rua = data_func.mapa_choropleth(df[['Nome do bairro', 'p.marc_sit_rua']].rename(columns={'p.marc_sit_rua':'valor'}), 'Nome do bairro')
    num_rua = f"Total: {df['p.marc_sit_rua'].sum():,} pessoas".replace(',','.')

    mapa_gini = data_func.mapa_choropleth(df[['Nome do bairro', 'gini']].rename(columns={'gini':'valor'}), 'Nome do bairro', gini=True)

    return mapa_pobreza, mapa_extrema_pobreza, mapa_vulnerabilidade, mapa_sem_renda, mapa_rua, mapa_gini, num_pobreza, num_ext_pobreza, num_vulnerabilidade, num_sem_renda, num_rua