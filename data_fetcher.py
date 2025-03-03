import os

import yfinance as yf
import pandas as pd

class TickerNotFoundException(Exception):
    pass

def fetch_historical_data(symbol, period='60d', interval='1d'):
    if not os.path.exists('data'):
        os.makedirs('data')
    data = yf.download(symbol, period=period, interval=interval)
    if data.empty:
        raise TickerNotFoundException(f"No data found for symbol {symbol}")
    data.index.name = 'Datetime'
    data.reset_index(inplace=True)
    data.to_csv('data/historical_data.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    fetch_historical_data()