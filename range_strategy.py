"""
Range Trading Strategy Implementation
"""

import math
import logging
from datetime import datetime, time
import pandas as pd
import talib
from ib_insync import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RangeStrategy')

class RangeStrategy:
    def __init__(self, ib=None, symbol=None, config=None):
        """
        Initialize range trading strategy
        
        The strategy identifies range-bound market conditions using technical indicators
        and executes trades when price is near support/resistance levels.
        
        Args:
            ib (IB): Interactive Brokers connection instance
            symbol (str): Trading symbol (e.g. 'AAPL')
            config (dict): Strategy configuration parameters including:
                - adx_period: ADX calculation period
                - adx_threshold: ADX threshold for range-bound markets
                - bollinger_ma_period: Bollinger Bands moving average period
                - bollinger_std_dev: Bollinger Bands standard deviation
                - rsi_period: RSI calculation period
                - rsi_oversold: RSI oversold threshold
                - atr_period: ATR calculation period
                - stop_loss_atr_multiplier: ATR multiplier for stop loss
                - profit_target_pct: Profit target percentage
                - risk_per_trade_pct: Risk percentage per trade
                - max_trades_per_day: Maximum trades per day
                - daily_loss_limit_pct: Daily loss limit percentage
        """
        self.ib = ib
        self.symbol = symbol
        self.config = self._validate_config(config)
        self.position = None  # Current position (None, 'long', or 'short')
        
        # Initialize data structures
        self.historical_data = pd.DataFrame()
        self.current_price = None
        self.latest_empty = False
        
        # Indicators
        self.adx = None
        self.bollinger = None
        self.rsi = None
        self.atr = None
        
        # Tracking
        self.trades_today = 0
        self.daily_pnl = 0
        self.last_trade = None
    
    def _validate_config(self, config):
        """Validate and set default config values"""
        defaults = {
            'adx_period': 14,
            'adx_threshold': 20,
            'bollinger_ma_period': 20,
            'bollinger_std_dev': 2,
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'atr_period': 14,
            'stop_loss_atr_multiplier': 1.5,
            'profit_target_pct': 0.015,
            'risk_per_trade_pct': 0.01,
            'max_trades_per_day': 5,
            'daily_loss_limit_pct': 0.02,
            'trade_start_time': time(9, 35),
            'trade_end_time': time(15, 55)
        }
        return {**defaults, **(config or {})}
    
    def calculate_indicators(self):
        """Calculate all technical indicators using TA-Lib"""
        if len(self.historical_data) < max(self.config['adx_period'], 
                                         self.config['bollinger_ma_period'],
                                         self.config['rsi_period']):
            return
        
        # Calculate ADX
        self.adx = talib.ADX(
            self.historical_data['high'],
            self.historical_data['low'],
            self.historical_data['close'],
            timeperiod=self.config['adx_period']
        )
        
        # Calculate Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            self.historical_data['close'],
            timeperiod=self.config['bollinger_ma_period'],
            nbdevup=self.config['bollinger_std_dev'],
            nbdevdn=self.config['bollinger_std_dev'],
            matype=0
        )
        self.bollinger = {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }
        
        # Calculate RSI
        self.rsi = talib.RSI(
            self.historical_data['close'],
            timeperiod=self.config['rsi_period']
        )
        
        # Calculate ATR
        self.atr = talib.ATR(
            self.historical_data['high'],
            self.historical_data['low'],
            self.historical_data['close'],
            timeperiod=self.config['atr_period']
        )
    
    def update_market_data(self, bar):
        """Update market data with latest bar"""
        new_row = {
            'timestamp': bar.time,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }
        self.historical_data = pd.concat([
            self.historical_data,
            pd.DataFrame([new_row])
        ]).tail(max(self.config['adx_period'],
                   self.config['bollinger_ma_period'],
                   self.config['rsi_period']) + 20)
        
        self.current_price = bar.close
        self.calculate_indicators()
    
    def evaluate_entry(self):
        """Evaluate if conditions are met for entry"""
        if self.position:
            return False
            
        # Check if market is in range
        if self.adx[-1] > self.config['adx_threshold']:
            return False
            
        # Check price near lower Bollinger Band
        if not (self.current_price <= self.bollinger['lower'][-1]):
            return False
            
        # Check RSI oversold
        if self.rsi[-1] > self.config['rsi_oversold']:
            return False
            
        # Check if within trading hours
        now = datetime.now().time()
        if not (self.config['trade_start_time'] <= now <= self.config['trade_end_time']):
            return False
            
        # Check daily trade limit
        if self.trades_today >= self.config['max_trades_per_day']:
            return False
            
        # Check daily loss limit
        if self.daily_pnl <= -self.config['daily_loss_limit_pct']:
            return False
            
        return True

    def calculate_position_size(self, price):
        """Calculate position size based on risk management rules"""
        account_value = self.ib.accountSummary('TotalCashValue')[0].value
        risk_amount = float(account_value) * self.config['risk_per_trade_pct']
        stop_distance = self.atr[-1] * self.config['stop_loss_atr_multiplier']
        return math.floor(risk_amount / stop_distance)

    def execute_trade(self):
        """Execute a trade with bracket orders"""
        if not self.evaluate_entry():
            return
            
        quantity = self.calculate_position_size(self.current_price)
        if quantity <= 0:
            return
            
        # Calculate order prices
        entry_price = self.current_price
        stop_price = entry_price - (self.atr[-1] * self.config['stop_loss_atr_multiplier'])
        target_price = entry_price * (1 + self.config['profit_target_pct'])
        
        # Create bracket order
        contract = Stock(self.symbol, 'SMART', 'USD')
        parent = MarketOrder('BUY', quantity)
        take_profit = LimitOrder('SELL', quantity, target_price)
        stop_loss = StopOrder('SELL', quantity, stop_price)
        
        # Submit orders
        trade = self.ib.placeOrder(contract, parent)
        self.ib.placeOrder(contract, take_profit)
        self.ib.placeOrder(contract, stop_loss)
        
        # Update position tracking
        self.position = {
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_price': stop_price,
            'target_price': target_price,
            'entry_time': datetime.now()
        }
        self.trades_today += 1
        
    def manage_position(self):
        """Monitor and manage open position"""
        if not self.position:
            return
            
        # Check if stop or target hit
        if self.current_price <= self.position['stop_price']:
            self.close_position('stop')
        elif self.current_price >= self.position['target_price']:
            self.close_position('target')
            
    def close_position(self, reason):
        """Close current position"""
        if not self.position:
            return
            
        # Calculate PnL
        exit_price = self.current_price
        pnl = (exit_price - self.position['entry_price']) * self.position['quantity']
        self.daily_pnl += pnl
        
        # Log trade
        trade_details = {
            'symbol': self.symbol,
            'entry_price': self.position['entry_price'],
            'exit_price': exit_price,
            'quantity': self.position['quantity'],
            'pnl': pnl,
            'duration': (datetime.now() - self.position['entry_time']).total_seconds(),
            'reason': reason
        }
        logger.info(f"Trade closed: {trade_details}")
        
        # Reset position
        self.position = None
        self.last_trade = trade_details
        
    def run(self):
        """Main trading loop"""
        while True:
            # Get latest market data
            bars = self.ib.reqHistoricalData(
                Stock(self.symbol, 'SMART', 'USD'),
                endDateTime='',
                durationStr='1 D',
                barSizeSetting='1 min',
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            self.update_market_data(bar[-1])
            
            # Manage existing position
            self.manage_position()
            
            # Evaluate new trade
            if not self.position:
                self.execute_trade()
                
            # Sleep until next iteration
            time.sleep(60)
