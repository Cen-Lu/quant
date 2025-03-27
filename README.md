# Quant Trading Strategy for IBKR

This project implements a range-based trading strategy for Interactive Brokers (IBKR) using Python.

## Project Structure

```
quant/
├── strategy_ui.py       # Main strategy UI
├── range_strategy.py    # Core trading strategy implementation
├── requirements.txt     # Python dependencies
└── README.md            # This documentation
```

## Key Features

- **Range Trading Strategy**: 
  - Identifies range-bound market conditions using ADX, Bollinger Bands and RSI
  - Executes trades when price is near support/resistance levels
  - Manages risk with stop losses and position sizing

- **Interactive UI**:
  - Manage IBKR connection
  - Configure strategy parameters
  - Start/stop strategy execution
  - View execution logs

## Requirements

- Python 3.8+
- Interactive Brokers TWS or Gateway
- Required packages (see requirements.txt)

## Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the strategy UI:
   ```bash
   python strategy_ui.py
   ```

2. Connect to IBKR TWS/Gateway

3. Configure strategy parameters

4. Start/stop the strategy as needed

## Configuration

Key strategy parameters:

- **Symbol**: Trading instrument (e.g. AAPL)
- **ADX Period/Threshold**: Trend strength filter
- **Bollinger Period/Std Dev**: Range boundaries
- **RSI Period/Oversold**: Entry conditions
- **Risk Management**: Stop loss, position sizing, daily limits

## License

MIT License
