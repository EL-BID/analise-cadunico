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

dash.register_page(__name__, path='/info', title='Análise CADÚnico')

# ====================================================
# Layout
# ====================================================

layout = html.Div([
    dcc.Markdown('''
        # Informações

        Este dashboard apresenta uma análise exploratória dos dados do sistema de Cadastro Único do governo federal. Elegemos 6 indicadores-chave:

        - Extrema pobreza,
        - Pobreza,
        - Vulnerabilidade,
        - Ausência de renda,
        - Situação de rua e
        - Índice de Gini.

        Na seção **Comparativo**, apresentamos uma série de mapas que permitem o usuário comparar os indicadores entre os bairros do Recife para diferentes anos.

        A seção **Análise mensal** permite uma comparação temporal entre os indicadores de um mesmo bairro. Os gráficos apresentam as informações por mês, e a medida mostrada é sempre o acumulado dos 12 meses anteriores a data.
        
        A seção **Análise anual** mostra valores dos indicadores agregados por ano para toda a cidade do Recife.

        Na seção **Superação**, é possível comparar a situação mais recente de famílias cadastradas no sistema com a sua situação anterior, permitindo um diagnóstico da evolução de cada indicador.

        Com referência ao Índice de Gini, é importante notar que a medida é sempre calculada a partir dos dados do CADÚnico. O índice aqui exibido não representa toda a população da cidade.
        ''', className='texto-info col-lg-9'),
], className='row justify-content-center')