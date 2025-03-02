import yfinance as yf
import pandas as pd

def fetch_historical_data(symbol, period='30d', interval='5m'):
    data = yf.download(symbol, period=period, interval=interval)
    if data.empty:
        raise ValueError(f"No data found for symbol {symbol}")
    data.index.name = 'Datetime'
    data.reset_index(inplace=True)
    data.to_csv('data/historical_data.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    fetch_historical_data()