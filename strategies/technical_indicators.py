import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict

class TechnicalIndicators:
    """Handles all technical indicator calculations"""
    
    @staticmethod
    def calculate_ema(series: pd.Series, window: int) -> pd.Series:
        return series.ewm(span=window, adjust=False).mean()
    
    @staticmethod
    def calculate_sma(series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window=window).mean()
    
    @staticmethod
    def identify_market_structure(df: pd.DataFrame) -> Dict[str, bool]:
        """Identifies bullish/bearish market structure breaks"""
        if len(df) < 3:
            return {'bullish': False, 'bearish': False}
        
        return {
            'bullish': (df['low'].iloc[-2] > df['low'].iloc[-3]) & 
                      (df['high'].iloc[-1] > df['high'].iloc[-2]),
            'bearish': (df['high'].iloc[-2] < df['high'].iloc[-3]) & 
                      (df['low'].iloc[-1] < df['low'].iloc[-2])
        }
    
    @staticmethod
    def find_deviation_line(df: pd.DataFrame, ema_window: int = 21) -> Tuple[Optional[float], Optional[float]]:
        """Finds deviation line (entry) and stop loss level"""
        df = df.copy()
        df['ema21'] = TechnicalIndicators.calculate_ema(df['close'], ema_window)
        
        for i in range(len(df)-1, max(0, len(df)-20), -1):
            candle = df.iloc[i]
            if candle['low'] < candle['ema21']:
                for j in range(i-1, max(0, i-10), -1):
                    prev_candle = df.iloc[j]
                    if prev_candle['close'] > prev_candle['open']:
                        for k in range(j, max(0, j-10), -1):
                            red_candle = df.iloc[k]
                            if red_candle['close'] < red_candle['open']:
                                return prev_candle['high'], red_candle['low']
        return None, None