import pandas as pd
import numpy as np
from risk_management import RiskManagement

class TradingStrategy:
    def __init__(self, capital, risk, stop_loss, take_profit):
        self.capital = capital
        self.risk = risk
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.trades = []
        self.risk_management = RiskManagement(capital, risk)
        self.current_position = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.max_drawdown = 0
        self.equity_curve = []
        self.balance = capital

    def calculate_vwap(self, data):
        q = data['Volume']
        p = data['Close']
        data['VWAP'] = (p * q).cumsum() / q.cumsum()
        return data

    def calculate_bands(self, data):
        data['STD'] = data['Close'].rolling(window=20).std()
        data['UpperBand'] = data['VWAP'] + (1.5 * data['STD'])
        data['LowerBand'] = data['VWAP'] - (1.5 * data['STD'])
        return data

    def update_statistics(self, profit_loss):
        self.total_trades += 1
        self.total_profit += profit_loss
        self.balance += profit_loss
        if profit_loss > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        self.equity_curve.append(self.balance)
        if len(self.equity_curve) > 1:
            peak = max(self.equity_curve)
            drawdown = peak - self.total_profit
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

    def backtest(self, data):
        data = self.calculate_vwap(data)
        data = self.calculate_bands(data)
        
        entry_price = 0
        entry_time = None
        position_size = 0

        for i in range(1, len(data)):
            if self.current_position == 0:
                if data['Close'].iloc[i-1] < data['LowerBand'].iloc[i-1] and data['Close'].iloc[i] > data['LowerBand'].iloc[i]:
                    self.current_position = 1
                    entry_price = data['Close'].iloc[i]
                    position_size = self.risk_management.calculate_position_size(self.stop_loss)
                    entry_time = data.index[i]
                    self.trades.append(f"Buy at {entry_price} on {entry_time}, Lots: {position_size}, Balance: {self.balance}")
                elif data['Close'].iloc[i-1] > data['UpperBand'].iloc[i-1] and data['Close'].iloc[i] < data['UpperBand'].iloc[i]:
                    self.current_position = -1
                    entry_price = data['Close'].iloc[i]
                    position_size = self.risk_management.calculate_position_size(self.stop_loss)
                    entry_time = data.index[i]
                    self.trades.append(f"Sell at {entry_price} on {entry_time}, Lots: {position_size}, Balance: {self.balance}")
            elif self.current_position == 1:
                if data['Close'].iloc[i] <= entry_price - self.stop_loss or data['Close'].iloc[i] >= entry_price + self.take_profit:
                    profit_loss = (data['Close'].iloc[i] - entry_price) * position_size
                    self.update_statistics(profit_loss)
                    self.trades.append(f"Sell at {data['Close'].iloc[i]} on {data.index[i]} (Stop Loss or Take Profit), Profit/Loss: {profit_loss}, Balance: {self.balance}")
                    self.current_position = 0
            elif self.current_position == -1:
                if data['Close'].iloc[i] >= entry_price + self.stop_loss or data['Close'].iloc[i] <= entry_price - self.take_profit:
                    profit_loss = (entry_price - data['Close'].iloc[i]) * position_size
                    self.update_statistics(profit_loss)
                    self.trades.append(f"Buy at {data['Close'].iloc[i]} on {data.index[i]} (Stop Loss or Take Profit), Profit/Loss: {profit_loss}, Balance: {self.balance}")
                    self.current_position = 0

        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        results = f"Backtest results:\nFinal Capital: {self.balance}\nWin Rate: {win_rate}%\nMax Drawdown: {self.max_drawdown}\nTotal Trades: {self.total_trades}\nTotal Profit: {self.total_profit}"
        return results, self.trades, self.equity_curve