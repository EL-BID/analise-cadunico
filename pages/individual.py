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

layout = html.Div([])

# ====================================================
# Callbacks
# ====================================================

