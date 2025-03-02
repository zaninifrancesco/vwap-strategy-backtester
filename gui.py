import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from backtesting import run_backtest
from data_fetcher import fetch_historical_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.offline import plot

class TradingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trading Strategy GUI")

        # Parameters
        self.capital = tk.DoubleVar(value=10000)
        self.risk = tk.DoubleVar(value=1)
        self.stop_loss = tk.DoubleVar(value=50)
        self.take_profit = tk.DoubleVar(value=100)
        self.symb = tk.StringVar(value='^NDX')

        # GUI Layout
        self.create_widgets()
        self.fetch_data()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        ttk.Label(frame, text="Initial Capital").grid(column=0, row=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.capital).grid(column=1, row=0, sticky=(tk.W, tk.E))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Risk (%)").grid(column=0, row=1, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.risk).grid(column=1, row=1, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Stop Loss (pips)").grid(column=0, row=2, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.stop_loss).grid(column=1, row=2, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Take Profit (pips)").grid(column=0, row=3, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.take_profit).grid(column=1, row=3, sticky=(tk.W, tk.E))

        ttk.Label(frame, text="Symbol").grid(column=0, row=4, sticky=tk.W)
        ttk.Entry(frame, textvariable=self.symb).grid(column=1, row=4, sticky=(tk.W, tk.E))

        ttk.Button(frame, text="Start Backtest", command=self.start_backtest).grid(column=0, row=5, columnspan=2)

        self.result_text = tk.Text(frame, height=20, width=80)
        self.result_text.grid(column=0, row=6, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.rowconfigure(5, weight=1)

        self.graph_frame = ttk.Frame(self.root)
        self.graph_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(1, weight=1)

    def fetch_data(self):
        try:
            symb = self.symb.get()
            fetch_historical_data(symb)
            self.result_text.insert(tk.END, "Historical data fetched successfully.\n")
        except ValueError as e:
            self.result_text.insert(tk.END, f"Error fetching data: {e}\n")

    def start_backtest(self):
        try:
            results, trades, equity_curve = run_backtest(
                capital=self.capital.get(),
                risk=self.risk.get(),
                stop_loss=self.stop_loss.get(),
                take_profit=self.take_profit.get()
            )
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, results)
            self.result_text.insert(tk.END, "\n\nList of Trades:\n")
            for index, trade in enumerate(trades):
                self.result_text.insert(tk.END, trade + "\n")
                if (index + 1) % 2 == 0:
                    self.result_text.insert(tk.END, "\n")
            self.plot_equity_curve(equity_curve)
        except Exception as e:
            self.result_text.insert(tk.END, f"Error during backtest: {e}\n")

    def plot_equity_curve(self, equity_curve):
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(go.Scatter(x=list(range(len(equity_curve))), y=equity_curve, mode='lines', name='Equity Curve'))
        fig.update_layout(title='Equity Curve', xaxis_title='Trades', yaxis_title='Equity')

        plot_div = plot(fig, output_type='div')
        with open("temp.html", "w", encoding='utf-8') as f:
            f.write(plot_div)

        fig.write_image("temp.png")

        image = Image.open("temp.png")
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(self.graph_frame, image=photo)
        label.image = photo
        label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

if __name__ == "__main__":
    root = tk.Tk()
    app = TradingApp(root)
    root.mainloop()