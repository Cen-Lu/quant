"""
Strategy UI Implementation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from range_strategy import RangeStrategy
from ib_insync import *

class StrategyUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Range Trading Strategy")
        self.root.geometry("1200x800")
        
        # Initialize IBKR connection
        self.ib = IB()
        self.strategy = None
        
        # Create UI components
        self.create_connection_frame()
        self.create_parameters_frame()
        self.create_controls_frame()
        self.create_log_frame()
        self.create_chart_frame()
        
    def create_connection_frame(self):
        """Create connection controls"""
        frame = ttk.LabelFrame(self.root, text="IBKR Connection", padding=10)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        self.connection_status = ttk.Label(frame, text="Disconnected", foreground="red")
        self.connection_status.grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(frame, text="Connect", command=self.connect_ibkr).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Disconnect", command=self.disconnect_ibkr).grid(row=0, column=2, padx=5)
        
    def create_parameters_frame(self):
        """Create strategy parameters controls"""
        frame = ttk.LabelFrame(self.root, text="Strategy Parameters", padding=10)
        frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Create parameter controls
        self.param_vars = {}
        params = [
            ('Symbol', 'symbol', 'AAPL'),
            ('ADX Period', 'adx_period', 14),
            ('ADX Threshold', 'adx_threshold', 20),
            ('Bollinger Period', 'bollinger_ma_period', 20),
            ('Bollinger Std Dev', 'bollinger_std_dev', 2),
            ('RSI Period', 'rsi_period', 14),
            ('RSI Oversold', 'rsi_oversold', 30),
            ('ATR Period', 'atr_period', 14),
            ('Stop Loss ATR Multiplier', 'stop_loss_atr_multiplier', 1.5),
            ('Profit Target %', 'profit_target_pct', 0.015),
            ('Risk per Trade %', 'risk_per_trade_pct', 0.01),
            ('Max Trades per Day', 'max_trades_per_day', 5),
            ('Daily Loss Limit %', 'daily_loss_limit_pct', 0.02)
        ]
        
        for i, (label, key, default) in enumerate(params):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=2)
            var = tk.StringVar(value=str(default))
            self.param_vars[key] = var
            ttk.Entry(frame, textvariable=var, width=10).grid(row=i, column=1, sticky="w", padx=5, pady=2)
            
    def create_controls_frame(self):
        """Create strategy controls"""
        frame = ttk.LabelFrame(self.root, text="Strategy Controls", padding=10)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        
        ttk.Button(frame, text="Start Strategy", command=self.start_strategy).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Stop Strategy", command=self.stop_strategy).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Analyze History", command=self.analyze_history).grid(row=0, column=2, padx=5)
        
    def create_log_frame(self):
        """Create trade log display"""
        frame = ttk.LabelFrame(self.root, text="Trade Log", padding=10)
        frame.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=5)
        
        self.log_text = tk.Text(frame, height=20, width=60)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def create_chart_frame(self):
        """Create chart display"""
        frame = ttk.LabelFrame(self.root, text="Price Chart", padding=10)
        frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)
        
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def connect_ibkr(self):
        """Connect to IBKR"""
        try:
            self.ib.connect('127.0.0.1', 7497, clientId=1)
            self.connection_status.config(text="Connected", foreground="green")
            messagebox.showinfo("Success", "Connected to IBKR")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            
    def disconnect_ibkr(self):
        """Disconnect from IBKR"""
        try:
            self.ib.disconnect()
            self.connection_status.config(text="Disconnected", foreground="red")
            messagebox.showinfo("Disconnected", "Disconnected from IBKR")
        except Exception as e:
            messagebox.showerror("Disconnection Error", str(e))
            
    def get_config(self):
        """Get current configuration from UI"""
        config = {}
        for key, var in self.param_vars.items():
            try:
                # Convert to appropriate type
                if '.' in var.get():
                    config[key] = float(var.get())
                else:
                    config[key] = int(var.get())
            except ValueError:
                messagebox.showerror("Invalid Value", f"Invalid value for {key}")
                return None
        return config
    
    def start_strategy(self):
        """Start the trading strategy"""
        if not self.ib.isConnected():
            messagebox.showerror("Error", "Not connected to IBKR")
            return
            
        config = self.get_config()
        if config is None:
            return
            
        self.strategy = RangeStrategy(
            ib=self.ib,
            symbol=config['symbol'],
            config=config
        )
        
        # Start strategy in a separate thread
        import threading
        self.strategy_thread = threading.Thread(target=self.strategy.run, daemon=True)
        self.strategy_thread.start()
        messagebox.showinfo("Strategy Started", "Range trading strategy is running")
        
    def stop_strategy(self):
        """Stop the trading strategy"""
        if self.strategy:
            self.strategy.stop()
            messagebox.showinfo("Strategy Stopped", "Range trading strategy has been stopped")
            
    def analyze_history(self):
        """Analyze historical data"""
        if not self.ib.isConnected():
            messagebox.showerror("Error", "Not connected to IBKR")
            return
            
        symbol = self.param_vars['symbol'].get()
        if not symbol:
            messagebox.showerror("Error", "Please enter a valid stock symbol")
            return
            
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            contract = self.ib.qualifyContracts(contract)[0]
            
            # Get historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='1 hour',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            
            if not bars:
                messagebox.showinfo("No Data", "No historical data available for this symbol")
                return
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get historical data: {str(e)}")
            return
        
        # Plot data
        self.ax.clear()
        prices = [bar.close for bar in bars]
        self.ax.plot(prices)
        self.ax.set_title(f"{symbol} Price History")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.canvas.draw()
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
if __name__ == '__main__':
    root = tk.Tk()
    app = StrategyUI(root)
    root.mainloop()
