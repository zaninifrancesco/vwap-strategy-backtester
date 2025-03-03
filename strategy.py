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
        self.min_balance = capital
        self.wins = []
        self.losses = []
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.max_consecutive_wins = 0
        self.max_consecutive_losses = 0
        self.trade_durations = []

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

    def update_statistics(self, profit_loss, entry_time, exit_time):
        self.total_trades += 1
        self.total_profit += profit_loss
        self.balance += profit_loss
        self.trade_durations.append((exit_time - entry_time).total_seconds())
        if profit_loss > 0:
            self.winning_trades += 1
            self.wins.append(profit_loss)
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.losing_trades += 1
            self.losses.append(profit_loss)
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        self.equity_curve.append(self.balance)
        if self.balance < self.min_balance:
            self.min_balance = self.balance
        if len(self.equity_curve) > 1:
            peak = max(self.equity_curve)
            drawdown = peak - self.total_profit
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
        if self.consecutive_wins > self.max_consecutive_wins:
            self.max_consecutive_wins = self.consecutive_wins
        if self.consecutive_losses > self.max_consecutive_losses:
            self.max_consecutive_losses = self.consecutive_losses

    def backtest(self, data):
        data = self.calculate_vwap(data)
        data = self.calculate_bands(data)

        entry_price = 0
        entry_time = None
        position_size = 0

        for i in range(1, len(data)):
            if self.current_position == 0:
                if data['Close'].iloc[i - 1] < data['LowerBand'].iloc[i - 1] and data['Close'].iloc[i] > \
                        data['LowerBand'].iloc[i]:
                    self.current_position = 1
                    entry_price = data['Close'].iloc[i]
                    position_size = self.risk_management.calculate_position_size(self.stop_loss)
                    entry_time = data.index[i]
                    self.trades.append(
                        f"Buy at {entry_price} on {entry_time}, Lots: {position_size}, Balance: {self.balance}")
                elif data['Close'].iloc[i - 1] > data['UpperBand'].iloc[i - 1] and data['Close'].iloc[i] < \
                        data['UpperBand'].iloc[i]:
                    self.current_position = -1
                    entry_price = data['Close'].iloc[i]
                    position_size = self.risk_management.calculate_position_size(self.stop_loss)
                    entry_time = data.index[i]
                    self.trades.append(
                        f"Sell at {entry_price} on {entry_time}, Lots: {position_size}, Balance: {self.balance}")
            elif self.current_position == 1:
                if data['Close'].iloc[i] <= entry_price - self.stop_loss or data['Close'].iloc[
                    i] >= entry_price + self.take_profit:
                    profit_loss = (data['Close'].iloc[i] - entry_price) * position_size
                    exit_time = data.index[i]
                    self.update_statistics(profit_loss, entry_time, exit_time)
                    self.trades.append(
                        f"Sell at {data['Close'].iloc[i]} on {exit_time} (Stop Loss or Take Profit), Profit/Loss: {profit_loss}, Balance: {self.balance}")
                    self.current_position = 0
            elif self.current_position == -1:
                if data['Close'].iloc[i] >= entry_price + self.stop_loss or data['Close'].iloc[
                    i] <= entry_price - self.take_profit:
                    profit_loss = (entry_price - data['Close'].iloc[i]) * position_size
                    exit_time = data.index[i]
                    self.update_statistics(profit_loss, entry_time, exit_time)
                    self.trades.append(
                        f"Buy at {data['Close'].iloc[i]} on {exit_time} (Stop Loss or Take Profit), Profit/Loss: {profit_loss}, Balance: {self.balance}")
                    self.current_position = 0

        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        average_win = np.mean(self.wins) if self.wins else 0
        average_loss = np.mean(self.losses) if self.losses else 0
        profit_factor = sum(self.wins) / abs(sum(self.losses)) if self.losses else float('inf')
        average_trade_duration = np.mean(self.trade_durations) if self.trade_durations else 0

        results = (f"Backtest results:\n"
                   f"Final Capital: {self.balance}\n"
                   f"Win Rate: {win_rate}%\n"
                   f"Max Drawdown: {self.max_drawdown}\n"
                   f"Total Trades: {self.total_trades}\n"
                   f"Total Profit: {self.total_profit}\n"
                   f"Minimum Balance: {self.min_balance}\n"
                   f"Profit Factor: {profit_factor}\n"
                   f"Average Win: {average_win}\n"
                   f"Average Loss: {average_loss}\n"
                   f"Max Consecutive Wins: {self.max_consecutive_wins}\n"
                   f"Max Consecutive Losses: {self.max_consecutive_losses}\n"
                   f"Average Trade Duration (seconds): {average_trade_duration}\n"
                   f"Losses: {self.losing_trades}\n"
                   f"Wins: {self.winning_trades}\n"
                   )
        return results, self.trades, self.equity_curve