import pandas as pd
from strategy import TradingStrategy


def run_backtest(capital, risk, stop_loss, take_profit):
    try:
        data = pd.read_csv('data/historical_data.csv', parse_dates=['Datetime'], encoding='utf-8')
        data.set_index('Datetime', inplace=True)
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        data['Volume'] = pd.to_numeric(data['Volume'], errors='coerce')
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    strategy = TradingStrategy(capital, risk, stop_loss, take_profit)
    results, trades, equity_curve = strategy.backtest(data)
    return results, trades, equity_curve