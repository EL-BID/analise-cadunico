import datetime
from dateutil.relativedelta import relativedelta
import json

import pyarrow.parquet as pq
import numpy as np
import pandas as pd
import plotly.express as px

# ====================================================

bairros = ['AFLITOS', 'AFOGADOS', 'AGUA FRIA', 'ALTO DO MANDU', 'ALTO JOSE BONIFACIO', 'ALTO JOSE DO PINHO', 'ALTO SANTA TEREZINHA', 'APIPUCOS', 'AREIAS', 'ARRUDA', 'BARRO', 'BEBERIBE', 'BOA VIAGEM', 'BOA VISTA', 'BOMBA DO HEMETERIO', 'BONGI', 'BRASILIA TEIMOSA', 'BREJO DA GUABIRABA', 'BREJO DE BEBERIBE', 'CABANGA', 'CACOTE', 'CAJUEIRO', 'CAMPINA DO BARRETO', 'CAMPO GRANDE', 'CASA AMARELA', 'CASA FORTE', 'CAXANGA', 'CIDADE UNIVERSITARIA', 'COELHOS', 'COHAB', 'COQUEIRAL', 'CORDEIRO', 'CORREGO DO JENIPAPO', 'CURADO', 'DERBY', 'DOIS IRMAOS', 'DOIS UNIDOS', 'ENCRUZILHADA', 'ENGENHO DO MEIO', 'ESPINHEIRO', 'ESTANCIA', 'FUNDAO', 'GRACAS', 'GUABIRABA', 'HIPODROMO', 'IBURA', 'ILHA DO LEITE', 'ILHA DO RETIRO', 'ILHA JOANA BEZERRA', 'IMBIRIBEIRA', 'IPSEP', 'IPUTINGA', 'JAQUEIRA', 'JARDIM SAO PAULO', 'JIQUIA', 'JORDAO', 'LINHA DO TIRO', 'MACAXEIRA', 'MADALENA', 'MANGABEIRA', 'MANGUEIRA', 'MONTEIRO', 'MORRO DA CONCEICAO', 'MUSTARDINHA', 'NOVA DESCOBERTA', 'PAISSANDU', 'PARNAMIRIM', 'PASSARINHO', 'PEIXINHOS', 'PINA', 'POCO', 'PONTO DE PARADA', 'PORTO DA MADEIRA', 'PRADO', 'RECIFE', 'ROSARINHO', 'SAN MARTIN', 'SANCHO', 'SANTANA', 'SANTO AMARO', 'SANTO ANTONIO', 'SAO JOSE', 'SITIO DOS PINTOS', 'SOLEDADE', 'TAMARINEIRA', 'TEJIPIO', 'TORRE', 'TORREAO', 'TORROES', 'TOTO', 'VARZEA', 'VASCO DA GAMA', 'ZUMBI']

mapa_json = json.load(open('dados/bairros.geojson'))

mapa_cores = {'Extrema pobreza':'#E84258', 'Pobreza':'#FD8060', 'Vulnerabilidade':'#FD8060', 'Superou':'#B0D8A4', 'Situação de rua':'#E84258'}

# ====================================================
# Trazendo e tratando df
# ====================================================

local_df = 'dados/cadunico 28out2022.parquet'

anos = list(pq.read_table(local_df, columns=['ano']).to_pandas()['ano'].unique())
anos.sort()

# ====================================================
# Gini
# ====================================================

def gini(x, w=None):
    # The rest of the code requires numpy arrays.
    x = np.asarray(x)
    if w is not None:
        w = np.asarray(w)
        sorted_indices = np.argsort(x)
        sorted_x = x[sorted_indices]
        sorted_w = w[sorted_indices]
        # Force float dtype to avoid overflows
        cumw = np.cumsum(sorted_w, dtype=float)
        cumxw = np.cumsum(sorted_x * sorted_w, dtype=float)
        return (np.sum(cumxw[1:] * cumw[:-1] - cumxw[:-1] * cumw[1:]) / 
                (cumxw[-1] * cumw[-1]))
    else:
        sorted_x = np.sort(x)
        n = len(x)
        cumx = np.cumsum(sorted_x, dtype=float)
        # The above formula, with all weights equal to 1 simplifies to:
        return (n + 1 - 2 * np.sum(cumx) / cumx[-1]) / n

# ====================================================

def grafico(df, tipo='barra', legenda=True, gini=False):
    pd.DataFrame(df).rename(columns={
        'extrema_pobreza': 'Extrema pobreza', 
        'pobreza': 'Pobreza', 
        'vulnerabilidade': 'Vulnerabilidade', 
        'p.marc_sit_rua': 'Situação de rua', 
        'sem renda': 'Sem renda', 
        'gini': 'Gini'
    }, inplace=True)
    if tipo=='barra':
        fig = px.bar(df)
        fig.update_traces(width=0.5)
    elif tipo=='linha':
        fig = px.line(df)

    fig.update_layout(
        margin=dict(
            b=10,
            t=10,
            l=30,
            r=30, 
        )
    )

    fig.update_layout(
        legend=dict(
            title="",
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
        ),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(
            tickformat='%m/%Y',
            title="",
            visible=True,
            showline=False,
            showticklabels=True,
            showgrid=False,
            gridcolor='lightgrey',
            griddash='dash',
        ),
        yaxis=dict(
            title="",
            visible=True,
            showline=False,
            showgrid=True,
            gridcolor='lightgrey',
            griddash='dash',
            showticklabels=True,
        ),
    )

    if not legenda:
        fig.update_layout(showlegend=False)
        fig.update_traces(hovertemplate='<b>%{y} pessoas</b><br>%{x}<extra></extra>')


    if gini:
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>%{x}',
        )
    else:
        fig.update_traces(
            hovertemplate='<b>%{y} pessoas</b><br>%{x}',
        )

    if tipo == 'linha':
        fig.update_layout(
            xaxis=dict(
                range=['2018-01-01', df.index[-1]],
                showgrid=True,
            )
        )


    return fig


def mapa_choropleth(df, var_local, gini=False):

    mapa_fig = px.choropleth_mapbox(
        df,
        geojson=mapa_json,
        locations=var_local,
        featureidkey='properties.bairro_nome_ca',
        color='valor',
        center = {"lat": -8.04090, "lon": -34.92923},
        mapbox_style="open-street-map",
        zoom=10.2,
        opacity=.6,
        )
    mapa_fig.update_geos(fitbounds='locations', visible=False)
    mapa_fig.layout.update(
        dragmode=False, 
        showlegend=False,
        margin=dict(
            l=0,
            r=0,
            b=0,
            t=0 
        ),
        paper_bgcolor='white',
        geo=dict(
            bgcolor='white',
        ),
    )

    mapa_fig.update_traces(
        hovertemplate='<b>%{location}</b><br>%{z} pessoas',
    )
    
    if not gini:
        mapa_fig.update_layout(coloraxis_colorbar=dict(title="Pessoas"))

    return mapa_fig