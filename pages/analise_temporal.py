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

dash.register_page(__name__, path='/analise', title='Análise CADÚnico')

# ====================================================
# Layout
# ====================================================

layout = html.Div([

    ## Dropdown
    dbc.Row(
        html.Div(
            dcc.Dropdown(id='seletor-bairros',
                options=data_func.bairros,
                placeholder='Recife',
            ),
        className='col-3 dropdown')
    ),

    html.Button('X', id='reset-bairro', n_clicks=0, type='reset'),

    ## Mapa e gráficos
    dbc.Row([
        html.Div(
            dcc.Graph(id='graph-mapa-Recife'),
        className='col-lg-4'),

        html.Div([
            dbc.Row(
                dcc.Loading(dcc.Graph(id='graph-pobreza', className='graficos pull-up')),
            ),
            dbc.Row(
                dcc.Loading(dcc.Graph(id='graph-rua', className='graficos pull-up')),
            ),
        ], className='col-lg-4'),

        html.Div([
            dbc.Row(
                dcc.Loading(dcc.Graph(id='graph-semrenda', className='graficos pull-up')),
            ),
            dbc.Row(
                dcc.Loading(dcc.Graph(id='graph-gini', className='graficos pull-up')),
            ),
        ], className='col-lg-4'),
    
    ]),
    
])

# ====================================================
# Callbacks
# ====================================================

# Plotar o mapa
@dash.callback(
    Output('graph-mapa-Recife', 'figure'),
    Input('seletor-bairros', 'value'),
)
def plotar_mapa(bairro):

    df_temp = pd.DataFrame(data=[[i, '0'] for i in data_func.bairros], columns=['bairro', 'valor'])
    
    if bairro:
        df_temp.loc[df_temp['bairro']==bairro, 'valor'] = '1'

    mapa_fig = px.choropleth_mapbox(
        df_temp,
        geojson=data_func.mapa_json,
        locations='bairro',
        featureidkey='properties.bairro_nome_ca',
        color='valor',
        color_discrete_map={'0':'#EE9856', '1':'#3C88EC'},
        hover_name='bairro',
        hover_data={'valor':False, 'bairro':False},
        center = {"lat": -8.04090, "lon": -34.975},
        mapbox_style="open-street-map",
        zoom=10.5,
        opacity=.6,
        )
    mapa_fig.update_geos(fitbounds='locations', visible=False)
    mapa_fig.update_coloraxes(showscale=False)
    mapa_fig.layout.update(
        dragmode=False, 
        showlegend=False,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0,
            pad=0,
        ),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        geo=dict(
            bgcolor='rgba(0, 0, 0, 0)',
        ),
    )
    
    return mapa_fig


# Plotar os gráficos
@dash.callback(
    Output('graph-pobreza', 'figure'),
    Output('graph-semrenda', 'figure'),
    Output('graph-rua', 'figure'),
    Output('graph-gini', 'figure'),
    Input('seletor-bairros', 'value'),
)
def plotar_grafico_pobreza(bairro):

    ## Lendo e ajustando dados
    
    if not bairro:
        domic_renda = pq.read_table(data_func.local_df, columns=['data_mes', 'ano', 'Nome do bairro', 'd.vlr_renda_total_fam', 'sem renda', 'renda até 3k']).to_pandas()
        domic_renda = domic_renda.groupby('data_mes')[['sem renda', 'renda até 3k']].sum()
        domic_renda = domic_renda.rolling(window=12, min_periods=1)[['sem renda', 'renda até 3k']].sum()
        
        df = pq.read_table(data_func.local_df, columns=['data_mes', 'pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua']).to_pandas()
        df = df.groupby('data_mes')[['pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua']].sum()
        df = df.rolling(window=12, min_periods=1)[['pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua']].sum()
        
        gini = pq.read_table(data_func.local_df, columns=['data_mes', 'd.vlr_renda_total_fam']).to_pandas()
        gini = gini.groupby(['data_mes'], as_index=False)['d.vlr_renda_total_fam'].agg(data_func.gini).rename(columns={'d.vlr_renda_total_fam':'gini'}).set_index('data_mes')
        gini = gini.rolling(window=12, min_periods=1)['gini'].mean()

    else:
        domic_renda = pq.read_table(data_func.local_df, columns=['data_mes', 'sem renda', 'renda até 3k'], filters=[('Nome do bairro', '=', bairro)]).to_pandas()
        domic_renda = domic_renda.groupby('data_mes')[['sem renda', 'renda até 3k']].sum()
        domic_renda = domic_renda.rolling(window=12, min_periods=1)[['sem renda', 'renda até 3k']].sum()
        
        df = pq.read_table(data_func.local_df, columns=['data_mes', 'pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua'], filters=[('Nome do bairro', '==', bairro)]).to_pandas()
        df = df.groupby('data_mes')[['pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua']].sum()
        df = df.rolling(window=12, min_periods=1)[['pobreza', 'extrema_pobreza', 'vulnerabilidade', 'p.marc_sit_rua']].sum()
        
        gini = pq.read_table(data_func.local_df, columns=['data_mes', 'd.vlr_renda_total_fam', 'Nome do bairro'], filters=[('Nome do bairro', '=', bairro)]).to_pandas()
        gini = gini.groupby(['data_mes'], as_index=False)['d.vlr_renda_total_fam'].agg(data_func.gini).rename(columns={'d.vlr_renda_total_fam':'gini'}).set_index('data_mes')
        gini = gini.rolling(window=12, min_periods=1)['gini'].mean()

    df = df.merge(domic_renda, left_index=True, right_index=True, how='outer')
    df = df.merge(gini, left_index=True, right_index=True, how='outer')

    chart_pobreza = data_func.grafico(df[['pobreza', 'extrema_pobreza', 'vulnerabilidade']], tipo='linha')
    sem_renda = data_func.grafico(df[['sem renda']], tipo='linha')
    rua = data_func.grafico(df[['p.marc_sit_rua']], tipo='linha')
    gini = data_func.grafico(df[['gini']], tipo='linha', gini=True)

    return chart_pobreza, sem_renda, rua, gini


# Mudar bairro ao clicar no mapa
@dash.callback(
    Output('seletor-bairros', 'value'),
    Input('graph-mapa-Recife', 'clickData'),
    Input('reset-bairro', 'n_clicks'),
)
def click_mapa(click_mapa, click_reset):
    if dash.callback_context.triggered[0]['prop_id'] != '.':
        if dash.callback_context.triggered[0]['prop_id'] == 'reset-bairro.n_clicks':
            return None
        else:
            return click_mapa['points'][0]['location']


# Esconder botão de reset dos bairros quando não foi útil
@dash.callback(
    Output('reset-bairro', 'style'),
    Input('seletor-bairros', 'value'),
)
def esconder_botao(bairro):
    if bairro:
        return {'visibility':''}
    else:
        return {'visibility':'hidden'}