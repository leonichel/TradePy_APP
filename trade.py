# bibliotecas
import streamlit as st
import requests_cache

import pandas as pd
import numpy as np

import yfinance as yf
from stockstats import StockDataFrame as stockDF

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px 

# Configurações

# sessões de cache
session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'

# nome da aplicação
st.title('TradePy')

# configurando sidebar
st.sidebar.header('Escolher ação')
choice = st.sidebar.text_input('Digite um ticker válido: ')
delta = st.sidebar.radio('Escolha o período: ', 
  ('5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max'))

# verificando se ação foi selecionada
if not choice:
  st.stop()

# ler ação selecionada
@st.cache(allow_output_mutation=True)
def get_data():
  ticker = yf.Ticker(choice, session=session)
  return ticker

ticker = get_data()
df = pd.DataFrame(ticker.history(period=delta))

# obter o macd
stock = stockDF.retype(df)
df['macd'] = stock['macd']

# Display

# ação escolhida
st.write('AÇÃO: ', choice)

# overview
st.markdown('## Overview')
over = px.line(df, x=df.index, y=df.columns[1:4])
st.plotly_chart(over)

# macd
st.markdown('## MACD')

macd = make_subplots(vertical_spacing=0, rows=2, cols=1, row_heights=[4,3])

macd.add_trace(go.Candlestick(x=df.index, name='Candlestick', open=df['open'], 
  high=df['high'], low=df['low'], close=df['close']), row=1, col=1)
macd.add_trace(go.Scatter(x=df.index, name='MACD', line=dict(color='blue')), 
  row=2, col=1)

macd.update_layout(xaxis_rangeslider_visible=False, 
  xaxis=dict(zerolinecolor='black', showticklabels=False),
  xaxis2=dict(showticklabels=False))
macd.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=False)

st.plotly_chart(macd)
