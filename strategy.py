# strategy.py
import pandas as pd

class MovingAverageCrossoverStrategy:
    def __init__(self, short_window: int = 20, long_window: int = 50):
        """
        初始化策略参数。
        
        :param short_window: 短期均线窗口长度
        :param long_window: 长期均线窗口长度
        """
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根据历史数据生成交易信号。
        
        :param data: 包含 'Close' 列的价格数据 DataFrame
        :return: 包含信号和仓位变动的 DataFrame
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0.0
        
        # 计算短期和长期均线
        signals['short_mavg'] = data['Close'].rolling(window=self.short_window, min_periods=1).mean()
        signals['long_mavg'] = data['Close'].rolling(window=self.long_window, min_periods=1).mean()
        
        # 当短期均线上穿长期均线时产生买入信号，反之卖出
        signals['signal'] = (signals['short_mavg'] > signals['long_mavg']).astype(float)
        signals['positions'] = signals['signal'].diff()
        
        return signals
