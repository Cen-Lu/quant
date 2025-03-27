# data_acquisition.py
import yfinance as yf
import pandas as pd

def get_historical_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    下载指定股票在[start, end]期间的历史数据。
    
    :param symbol: 股票代码，例如 'AAPL'
    :param start: 起始日期（格式 'YYYY-MM-DD'）
    :param end: 结束日期（格式 'YYYY-MM-DD'）
    :return: 包含历史数据的 pandas DataFrame
    """
    print(f"正在下载 {symbol} 从 {start} 到 {end} 的历史数据...")
    data = yf.download(symbol, start=start, end=end)
    if data.empty:
        raise ValueError("下载的数据为空，请检查股票代码和日期区间！")
    return data