import streamlit as st
import requests_cache
import pandas as pd
import numpy as np
import yfinance as yf
from stockstats import StockDataFrame as stockDF
from sklearn.neighbors import KNeighborsRegressor
from sktime.forecasting.compose import ReducedForecaster
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px 

Periods = ('1mo','3mo','6mo','1y','2y','5y','10y','ytd','max')

def get_cache_session():
  session = requests_cache.CachedSession('yfinance.cache')
  session.headers['User-agent'] = 'my-program/1.0'

  return session

def get_user_choices():
  st.sidebar.header('Escolher ação')
  ticker_choice = st.sidebar.text_input('Digite um ticker válido: ')
  period_choice = st.sidebar.radio('Escolha o período: ', Periods)

  return ticker_choice, period_choice

@st.cache(allow_output_mutation=True)
def get_data(ticker_choice, period_choice, session):
  ticker_data = yf.Ticker(ticker_choice, session=session)
  df = pd.DataFrame(ticker_data.history(period=period_choice))
  stock = stockDF.retype(df)
  df['macd'] = stock['macd']

  return df

def get_ticker_plot(df):
  ticker_plot = px.line(df, x=df.index, y=df.columns[1:4])

  return ticker_plot

def get_macd_plot(df):
  macd_plot = make_subplots(vertical_spacing=0, rows=2, cols=1, 
    row_heights=[4,3])
  macd_plot.add_trace(go.Candlestick(x=df.index, name='Candlestick', 
    open=df['open'], high=df['high'], low=df['low'], close=df['close']), 
    row=1, col=1)
  macd_plot.add_trace(go.Scatter(x=df.index, name='MACD', 
    line=dict(color='blue')), row=2, col=1)
  macd_plot.update_layout(xaxis_rangeslider_visible=False, 
    xaxis=dict(zerolinecolor='black', showticklabels=False),
    xaxis2=dict(showticklabels=False))
  macd_plot.update_xaxes(showline=True, linewidth=1, linecolor='black', 
    mirror=False)

  return macd_plot

def get_predictions_data(df):
  y = pd.Series(df['close'], index=df.index)
  r = pd.date_range(start=y.index.min(), end=y.index.max())
  y = y.reindex(r).fillna(0.0)
  y = y.replace(to_replace=0.0, method='ffill')

  regressor = KNeighborsRegressor(n_neighbors=1)
  forecaster = ReducedForecaster(
    regressor, scitype="regressor", window_length=15, strategy="recursive")
  forecaster.fit(y)

  fh = np.arange(10)
  prediction = forecaster.predict(fh)
  y_pred = pd.concat([y, prediction])

  predictions_data = pd.DataFrame({ 'Real': y, 'Prediction': prediction}, 
    index=y_pred.index)

  return predictions_data

def get_predictions_plot(predictions_data):
  predictions_plot = px.line(predictions_data.tail(60), 
    x=predictions_data.tail(60).index, y=predictions_data.tail(60).columns)

  return predictions_plot

ticker_choice, period_choice = get_user_choices()

if st.sidebar.button('Ler ticker'):

  session = get_cache_session()
  df = get_data(ticker_choice, period_choice, session)

  st.write('# TradePy')
  st.write('AÇÃO: ', ticker_choice)

  st.write('## Overview')
  st.write('Plote da visão geral do ticker.')
  ticker_plot = get_ticker_plot(df)
  st.plotly_chart(ticker_plot)

  st.write('## Indicador MACD')
  st.write('Indicador de análise técnica do mercado financeiro.')
  macd_plot = get_macd_plot(df)
  st.plotly_chart(macd_plot)

  st.markdown('## Predições')
  st.write('Predição para os próximos 10 dias.')
  predictions_data = get_predictions_data(df)
  predictions_plot = get_predictions_plot(predictions_data)
  st.plotly_chart(predictions_plot)

else:
  st.stop()