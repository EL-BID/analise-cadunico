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

dash.register_page(__name__, title='Análise CADÚnico')

# ====================================================
# Layout
# ====================================================

layout = html.Div([

    ## Dropdown
    dbc.Row([
        html.P('Indicador:', style={'text-align':'center'}),
        html.Div(
            dcc.Dropdown(id='seletor-var-sankey',
                options=['Extrema pobreza', 'Pobreza', 'Vulnerabilidade', 'Situação de rua'],
                value='Extrema pobreza',
                clearable=False,
            ),
        className='col-3 dropdown')
    ]),

    ## Range Slider para os anos

    html.Div([
        html.P('Período:', style={'text-align':'center'}),
        dcc.RangeSlider(2017, 2022, 1, value=[2020, 2022], marks={i:str(i) for i in range(2017, 2023)}, allowCross=False, id='ano-range-slider', className='col-lg-10'),
    ], className='row justify-content-center'),

    html.Div(
        html.Div([
            dcc.Markdown(id='texto-sankey', className='pergunta-sankey'),
            dcc.Graph(id='graph-sankey'),
            dcc.Markdown(id='rodape-sankey'),
        ], className='div-sankey col-lg-10'),
    className='row justify-content-center'),
])

# ====================================================
# Callbacks
# ====================================================

# Plotar o sankey a partir da variável fonte
@dash.callback(
    Output('graph-sankey', 'figure'),
    Output('rodape-sankey', 'children'),
    Input('seletor-var-sankey', 'value'),
    Input('ano-range-slider', 'value'),
)
def plotar_grafico_sankey(var, anos):
    df_sankey = pq.read_table(data_func.local_df, columns=['d.dat_atual_fam', 'p.num_cpf_pessoa', 'ano', 'p.marc_sit_rua', 'situacao', 'rua'], filters=[('ano','>=', anos[0]), ('ano','<=', anos[1])]).to_pandas()
    df_sankey = df_sankey.sort_values('d.dat_atual_fam').groupby(['p.num_cpf_pessoa', 'ano'], as_index=False).last()
    cpfs_validos = list(df_sankey['p.num_cpf_pessoa'].value_counts()[(df_sankey['p.num_cpf_pessoa'].value_counts() >= 2)].index)
    df_sankey['p.num_cpf_pessoa'] = df_sankey['p.num_cpf_pessoa'].map({i:i for i in cpfs_validos})
    df_sankey.dropna(subset=['p.num_cpf_pessoa'], inplace=True)
    df_sankey.sort_values(['p.num_cpf_pessoa', 'ano'], inplace=True)
    
    if var == 'Vulnerabilidade':
        df_sankey['situacao'] = df_sankey['situacao'].map({'Extrema pobreza':'Vulnerabilidade', 'Pobreza':'Vulnerabilidade'}).fillna(df_sankey['situacao'])
        df_sankey = df_sankey.groupby('p.num_cpf_pessoa').agg({'situacao':['first', 'last'], 'ano':'first'})
        df_sankey.columns = ['first', 'last', 'ano_inicial']
        df_sankey = df_sankey.loc[df_sankey['ano_inicial']==anos[0]]
        total = len(df_sankey)
        df_sankey = df_sankey.loc[df_sankey['first'] == var]
        df_sankey = df_sankey.value_counts().reset_index().rename(columns={0:'valor'})
        df_sankey['percentual'] = np.round((df_sankey['valor']/df_sankey['valor'].sum())*100, 1)

        situacoes = dict(enumerate(df_sankey['last']))
        situacoes = {v: k for k, v in situacoes.items()}
        inicio = [2]*len(situacoes)

        ### Posição dos nodes
        x_var = [1, 1, 0]
        y_var = [0.5, 0.001, 0.001]

        labels = list(situacoes.keys())+[var]
        labels[0] = labels[0] + ' ' + format(df_sankey['valor'].iloc[0], ',').replace(',', '.')
        labels[1] = labels[1] + ' ' + format(df_sankey['valor'].iloc[1], ',').replace(',', '.')
        labels[2] = labels[2] + ' ' + format(df_sankey['valor'].sum(), ',').replace(',', '.')

    elif var == 'Extrema pobreza' or var == 'Pobreza':
        df_sankey = df_sankey.groupby('p.num_cpf_pessoa').agg({'situacao':['first', 'last'], 'ano':'first'})
        df_sankey.columns = ['first', 'last', 'ano_inicial']
        df_sankey = df_sankey.loc[df_sankey['ano_inicial']==anos[0]]
        total = len(df_sankey)
        df_sankey = df_sankey.loc[df_sankey['first'] == var]
        df_sankey = df_sankey.value_counts().reset_index().rename(columns={0:'valor'})
        df_sankey['percentual'] = np.round((df_sankey['valor']/df_sankey['valor'].sum())*100, 1)

        situacoes = dict(enumerate(df_sankey['last']))
        situacoes = {v: k for k, v in situacoes.items()}
        inicio = [3]*len(situacoes)

        ### Posição dos nodes
        x_var = [1, 1, 1, 0]
        y_var = [0.6, 0.2, 0.001, 0.001]

        labels = list(situacoes.keys())+[var]
        labels[0] = labels[0] + ' ' + format(df_sankey['valor'].iloc[0], ',').replace(',', '.')
        labels[1] = labels[1] + ' ' + format(df_sankey['valor'].iloc[1], ',').replace(',', '.')
        labels[2] = labels[2] + ' ' + format(df_sankey['valor'].iloc[2], ',').replace(',', '.')
        labels[3] = labels[3] + ' ' + format(df_sankey['valor'].sum(), ',').replace(',', '.')

    elif var == 'Situação de rua':
        df_sankey = df_sankey.groupby('p.num_cpf_pessoa').agg({'p.marc_sit_rua':['first', 'last'], 'ano':'first'})
        df_sankey.columns = ['first', 'last', 'ano_inicial']
        df_sankey = df_sankey.loc[df_sankey['ano_inicial']==anos[0]]
        total = len(df_sankey)
        df_sankey = df_sankey.loc[df_sankey['first'] == 1]
        df_sankey = df_sankey.value_counts().reset_index().rename(columns={0:'valor'})
        df_sankey['percentual'] = np.round((df_sankey['valor']/df_sankey['valor'].sum())*100, 1)

        df_sankey['first'] = df_sankey['first'].map({0:'Superou', 1:'Situação de rua'})
        df_sankey['last'] = df_sankey['last'].map({0:'Superou', 1:'Situação de rua'})

        situacoes = dict(enumerate(df_sankey['last']))
        situacoes = {v: k for k, v in situacoes.items()}
        inicio = [2]*len(situacoes)

        ### Posição dos nodes
        x_var = [1, 1, 0]
        y_var = [0.5, 0.001, 0.001]

        labels = list(situacoes.keys())+[var]
        labels[0] = labels[0] + ' ' + format(df_sankey['valor'].iloc[0], ',').replace(',', '.')
        labels[1] = labels[1] + ' ' + format(df_sankey['valor'].iloc[1], ',').replace(',', '.')
        labels[2] = labels[2] + ' ' + format(df_sankey['valor'].sum(), ',').replace(',', '.')


    df_sankey['cores'] = df_sankey['last'].map(data_func.mapa_cores)
    cores = list(df_sankey['cores'])+[data_func.mapa_cores[var]]


    sankey = go.Sankey(
        arrangement = "snap",
        node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = 'black', width = 0.5),
            label = labels,
            color = cores,
            customdata = list(df_sankey['percentual'])+[100],
            hovertemplate = '%{customdata}%<extra></extra>',
            x = x_var,
            y = y_var,
        ),

        link = dict(
            source = inicio,
            target = list(situacoes.values()),
            value = df_sankey['valor'],
            customdata = list(df_sankey['percentual'])+[100],
            hovertemplate = '%{customdata}%<extra></extra>',
        ),
    )

    sankey_chart = go.Figure(data=sankey)
    
    sankey_chart.update_layout(
        margin=dict(
            l=30,
            r=30,
            b=30,
            t=30,
        ),
    )

    total = format(total, ',').replace(',','.')

    sankey_chart.update_layout(
        # font_family="Courier New",
        font_color="black",
        font_size=16,
    )

    return sankey_chart, f'Comparamos a situação do indivíduo em {anos[0]} com o seu dado mais recente no CADÚnico, seja em {anos[1]} ou antes. Total de pessoas analisadas: **{total}**.'



# Plotar o sankey a partir da variável fonte
@dash.callback(
    Output('texto-sankey', 'children'),
    Input('seletor-var-sankey', 'value'),
    Input('ano-range-slider', 'value'),
)
def escrever_texto(var, anos):
    return f'Dos que estavam em **{var.lower()}** em {anos[0]}, como encontram-se em {anos[1]}?'