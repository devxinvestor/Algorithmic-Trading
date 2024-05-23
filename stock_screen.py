import pandas as pd
import numpy as np
import yfinance as yf
from pyfinviz.screener import Screener
import warnings
import pandas_ta as ta
import talib
import datetime
from statsmodels.tsa.stattools import adfuller
from sklearn.svm import SVC
import cufflinks as cf
import plotly.offline as pyo
import plotly.graph_objs as go
warnings.filterwarnings('ignore')

class Stock:
    def __init__(self, time):
        time_to_days = {
            "One month": 30,
            "Six months": 182,
            "One year": 365,
            "Five years": 365*5
        }
        days = time_to_days.get(time, 0)
        self.time = time
        self.start = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        self.end = (datetime.datetime.now()).strftime('%Y-%m-%d')
    
    def get_tickers(self, pages_on_finviz):
        filter_options = [(Screener.ExchangeOption.NYSE or Screener.ExchangeOption.NASDAQ), 
                      (Screener.SectorOption.TECHNOLOGY or Screener.SectorOption.HEALTHCARE)]
        pages = [i for i in range(1,pages_on_finviz)]
        screener = Screener(filter_options=filter_options, pages=pages)
        all_stocks = np.array([])
        for i in range(1, pages_on_finviz):
            all_stocks = np.append(all_stocks, screener.data_frames[i]['Ticker'].values)
        return all_stocks
    
    def get_stock_data(self, stocks):
        stock_data = {}
        for stock in stocks:
            try:
                data = yf.download(stock, start=self.start, end=self.end)
                stock_data[stock] = data
                print(f"{stock} downloaded")
            except:
                print("This stock does not belong on yfinance")
        return stock_data
    
    def get_PSAR_Indicator(self, stock_data):
        buy = []
        for stock, data in stock_data.items():
            data['SAR'] = talib.SAR(data['High'], data['Low'], acceleration=0.02, maximum=0.2)
            data['Signal'] = 0  # 0 means no signal
            data['Signal'][data['Close'] > data['SAR']] = 1  # Buy signal
            data['Signal'][data['Close'] < data['SAR']] = -1  # Sell signal
            data['Position'] = data['Signal'].diff()
            if (data['Signal'][-1] == 1):
                buy.append(stock)
        print(buy)
        return buy
    
    def get_ADX(self, stock_data):
        buy = []
        for stock, data in stock_data.items():
            data['ADX'] = talib.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
            data['+DI'] = talib.PLUS_DI(data['High'], data['Low'], data['Close'], timeperiod=14)
            data['-DI'] = talib.MINUS_DI(data['High'], data['Low'], data['Close'], timeperiod=14)
            data['Signal'] = 0  # 0 means no signal
            data['Signal'][data['+DI'] > data['-DI']] = 1  # Buy signal
            data['Signal'][data['+DI'] < data['-DI']] = -1  # Sell signal
            data['Position'] = data['Signal'].diff()
            if (data['Signal'][-1] == 1):
                buy.append(stock)
        print(buy)
        return buy
    
    def get_RSI(self, stock_data):
        buy = []
        for stock, data in stock_data.items():
            data['RSI'] = talib.RSI(data['Close'], timeperiod=14)
            data['Signal'] = 0  # 0 means no signal
            data['Signal'][data['RSI'] > 70] = -1  # Overbought signal
            data['Signal'][data['RSI'] < 30] = 1  # Oversold signal
            data['Position'] = data['Signal'].diff()
            if (data['Signal'][-1] == 1):
                buy.append(stock)
        print(buy)
        return buy
    
    def get_Short_SMA_Crossover(self, stock_data):
        buy = []
        for stock, data in stock_data.items():
            data['SMA10'] = talib.SMA(data['Close'], timeperiod=10)
            data['SMA20'] = talib.SMA(data['Close'], timeperiod=20)
            data['Signal'] = 0  # 0 means no signal
            data['Signal'][data['SMA10'] > data['SMA20']] = 1  # Buy signal
            data['Signal'][data['SMA10'] < data['SMA20']] = -1  # Sell signal
            data['Position'] = data['Signal'].diff()
            if (data['Signal'][-1] == 1):
                buy.append(stock)
        print(buy)
        return buy
    
    def get_Long_SMA_Crossover(self, stock_data):
        buy = []
        for stock, data in stock_data.items():
            data['SMA20'] = talib.SMA(data['Close'], timeperiod=10)
            data['SMA50'] = talib.SMA(data['Close'], timeperiod=20)
            data['Signal'] = 0  # 0 means no signal
            data['Signal'][data['SMA20'] > data['SMA50']] = 1  # Buy signal
            data['Signal'][data['SMA20'] < data['SMA50']] = -1  # Sell signal
            data['Position'] = data['Signal'].diff()
            if (data['Signal'][-1] == 1):
                buy.append(stock)
        print(buy)
        return buy
    
    def graph_indicator(self, stock_data, indicator1, indicator2 = None):
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], name='Close'))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[indicator1], name=indicator1))
        if indicator2:
            fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data[indicator2], name=indicator2))
        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Signal'], name='Signal', yaxis='y2'))

        fig.update_layout(
            yaxis2=dict(
                title='Signal',
                overlaying='y',
                side='right'
            )
        )
        fig.show()
    
    def calculate_log_returns(self, stock_data):
        log_returns = {}
        for stock, data in stock_data.items():
            rets = np.log(data['Close'] / data['Close'].shift(1))
            log_returns[stock] = rets
        return log_returns
    
    def test_stationarity(self, log_returns):
        results = {}
        for stock, rets in log_returns.items():
            adf = adfuller(rets.dropna())
            results[stock] = adf
        return results
        
    

stock = Stock("One year")
# stocks = stock.get_tickers(12)
stock_data = stock.get_stock_data('A')
stock.get_Short_SMA_Crossover(stock_data)
stock.graph_indicator(stock_data['A'], 'SMA10', 'SMA20')
stock.get_Long_SMA_Crossover(stock_data)
stock.graph_indicator(stock_data['A'], 'SMA20', 'SMA50')
stock.get_PSAR_Indicator(stock_data)
stock.graph_indicator(stock_data['A'], 'SAR')

