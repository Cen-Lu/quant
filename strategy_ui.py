"""
Simple Trading Strategy UI for IBKR Quant Project
Focuses on core functionality: connection, parameters, execution and logging
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from range_strategy import RangeStrategy
from ib_insync import *
import logging

class StrategyUI:
    def __init__(self, root):
        """
        Initialize the trading strategy UI
        
        The UI provides controls for:
        - Connecting to IBKR TWS/Gateway
        - Configuring strategy parameters
        - Starting/stopping the strategy
        - Viewing execution logs
        
        Args:
            root (tk.Tk): The root Tkinter window
        """
        # Basic UI setup
        self.root = root
        self.root.title("Quant Strategy Manager")
        self.root.geometry("800x600")
        
        # Strategy components
        self.ib = IB()  # IBKR connection
        self.strategy = None  # Active strategy
        
        # Setup UI components
        self.create_connection_panel()
        self.create_parameter_panel() 
        self.create_control_panel()
        self.create_log_panel()
        
    def create_connection_panel(self):
        """Create connection management UI"""
        frame = ttk.LabelFrame(self.root, text="IBKR Connection", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Connection status
        self.conn_status = ttk.Label(frame, text="Disconnected", foreground="red")
        self.conn_status.grid(row=0, column=0, padx=5, pady=5)
        
        # Control buttons
        ttk.Button(frame, text="Connect", command=self.connect_ibkr).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Disconnect", command=self.disconnect_ibkr).grid(row=0, column=2, padx=5)

    def create_parameter_panel(self):
        """Create strategy parameter UI"""
        frame = ttk.LabelFrame(self.root, text="Strategy Parameters", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Parameter fields
        self.params = {
            'symbol': self.create_param_field(frame, "Symbol", "AAPL", 0),
            'adx_period': self.create_param_field(frame, "ADX Period", "14", 1),
            'adx_threshold': self.create_param_field(frame, "ADX Threshold", "20", 2),
            'bollinger_period': self.create_param_field(frame, "Bollinger Period", "20", 3),
            'bollinger_std_dev': self.create_param_field(frame, "Bollinger Std Dev", "2", 4),
            'rsi_period': self.create_param_field(frame, "RSI Period", "14", 5),
            'rsi_oversold': self.create_param_field(frame, "RSI Oversold", "30", 6),
            'atr_period': self.create_param_field(frame, "ATR Period", "14", 7),
            'stop_loss_mult': self.create_param_field(frame, "Stop Loss Multiplier", "1.5", 8),
            'profit_target': self.create_param_field(frame, "Profit Target %", "0.015", 9),
            'risk_per_trade': self.create_param_field(frame, "Risk per Trade %", "0.01", 10),
            'max_trades': self.create_param_field(frame, "Max Trades/Day", "5", 11),
            'daily_loss_limit': self.create_param_field(frame, "Daily Loss Limit %", "0.02", 12)
        }
        
    def create_param_field(self, frame, label, default, row):
        """Helper to create a parameter field"""
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="e", padx=5, pady=2)
        var = tk.StringVar(value=default)
        ttk.Entry(frame, textvariable=var, width=10).grid(row=row, column=1, sticky="w", padx=5, pady=2)
        return var

    def create_control_panel(self):
        """Create strategy control UI"""
        frame = ttk.LabelFrame(self.root, text="Strategy Controls", padding=10)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(frame, text="Start Strategy", command=self.start_strategy).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Stop Strategy", command=self.stop_strategy).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Validate Parameters", command=self.validate_parameters).grid(row=0, column=2, padx=5)

    def create_log_panel(self):
        """Create execution log UI"""
        frame = ttk.LabelFrame(self.root, text="Execution Log", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(frame, height=15, width=80)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        
    def connect_ibkr(self):
        """Connect to IBKR TWS/Gateway"""
        try:
            self.ib.connect('127.0.0.1', 7497, clientId=1)
            self.conn_status.config(text="Connected", foreground="green")
            self.log("Successfully connected to IBKR")
        except Exception as e:
            self.conn_status.config(text="Connection failed", foreground="red")
            self.log(f"Connection failed: {str(e)}")
            messagebox.showerror("Connection Error", f"Failed to connect to IBKR: {str(e)}")

    def disconnect_ibkr(self):
        """Disconnect from IBKR"""
        if self.ib.isConnected():
            self.ib.disconnect()
            self.conn_status.config(text="Disconnected", foreground="red")
            self.log("Disconnected from IBKR")
            
    def validate_parameters(self):
        """Validate strategy parameters"""
        try:
            params = self.get_parameters()
            self.log("Parameters validated successfully")
            return True
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            self.log(f"Parameter validation failed: {str(e)}")
            return False
            
    def get_parameters(self):
        """Get and validate parameters"""
        params = {}
        for key, var in self.params.items():
            value = var.get()
            if key == 'symbol':
                if not value:
                    raise ValueError("Symbol cannot be empty")
                params[key] = value
            else:
                try:
                    params[key] = float(value)
                except ValueError:
                    raise ValueError(f"Invalid value for {key}: {value}")
        return params
        
    def start_strategy(self):
        """Start the trading strategy"""
        if not self.ib.isConnected():
            messagebox.showerror("Error", "Not connected to IBKR")
            return
            
        if not self.validate_parameters():
            return
            
        try:
            params = self.get_parameters()
            self.strategy = RangeStrategy(self.ib, params['symbol'], params)
            self.strategy.run()
            self.log("Strategy started successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start strategy: {str(e)}")
            self.log(f"Strategy start failed: {str(e)}")
            
    def stop_strategy(self):
        """Stop the trading strategy"""
        if self.strategy:
            try:
                self.strategy.disconnect()
                self.strategy = None
                self.log("Strategy stopped successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to stop strategy: {str(e)}")
                self.log(f"Strategy stop failed: {str(e)}")
        else:
            messagebox.showinfo("Info", "No active strategy to stop")

if __name__ == '__main__':
    root = tk.Tk()
    app = StrategyUI(root)
    root.mainloop()
