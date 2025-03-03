import unittest
import pandas as pd
from datetime import datetime
from strategy import TradingStrategy

class TestTradingStrategy(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        data = {
            'Date': pd.date_range(start='1/1/2022', periods=10, freq='D'),
            'Close': [10, 11, 12, 11, 10, 9, 8, 9, 10, 11],
            'Volume': [1000, 1100, 1000, 900, 1200, 1300, 1250, 1350, 1400, 1500]
        }
        self.data = pd.DataFrame(data)
        self.data.set_index('Date', inplace=True)

        self.strategy = TradingStrategy(
            capital=10000,
            risk=0.01,
            stop_loss=1,
            take_profit=2
        )

    def test_calculate_vwap(self):
        result = self.strategy.calculate_vwap(self.data.copy())
        self.assertIn('VWAP', result.columns)
        self.assertAlmostEqual(result['VWAP'].iloc[-1], (self.data['Close'] * self.data['Volume']).sum() / self.data['Volume'].sum(), places=2)


    def test_backtest(self):
        result, trades, equity_curve = self.strategy.backtest(self.data.copy())
        self.assertIsInstance(result, str)
        self.assertIsInstance(trades, list)
        self.assertIsInstance(equity_curve, list)
        self.assertGreaterEqual(self.strategy.total_trades, 0)
        self.assertGreaterEqual(self.strategy.total_profit, 0)

    def test_update_statistics(self):
        initial_balance = self.strategy.balance
        self.strategy.update_statistics(100, datetime(2022, 1, 1), datetime(2022, 1, 2))
        self.assertEqual(self.strategy.total_trades, 1)
        self.assertEqual(self.strategy.winning_trades, 1)
        self.assertEqual(self.strategy.total_profit, 100)
        self.assertEqual(self.strategy.balance, initial_balance + 100)

if __name__ == '__main__':
    unittest.main()
