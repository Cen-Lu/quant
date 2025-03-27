"""
Main script to run the range trading strategy
"""

import json
import time
from datetime import time as dt_time
from ib_insync import *
from range_strategy import RangeStrategy

def load_config(config_path):
    """Load strategy configuration from JSON file"""
    with open(config_path) as f:
        config = json.load(f)
        
    # Convert time strings to time objects
    config['trade_start_time'] = dt_time.fromisoformat(config['trade_start_time'])
    config['trade_end_time'] = dt_time.fromisoformat(config['trade_end_time'])
    
    return config

def main():
    # Load configuration
    config = load_config('strategy_config.json')
    
    # Connect to IBKR
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=1)
    
    # Initialize strategy
    strategy = RangeStrategy(
        ib=ib,
        symbol='AAPL',  # Default symbol, can be parameterized
        config=config
    )
    
    try:
        # Start trading loop
        strategy.run()
    except KeyboardInterrupt:
        print("Shutting down strategy...")
    finally:
        ib.disconnect()

if __name__ == '__main__':
    main()
