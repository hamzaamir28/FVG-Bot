from pybit.unified_trading import HTTP
import pandas as pd
from typing import Dict, Optional

class BybitDataFeed:
    """Handles all Bybit data connections"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        self.client = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
    
    def get_ohlc(self, symbol: str, interval: str, limit: int = 200) -> pd.DataFrame:
        """Fetches OHLC data from Bybit"""
        try:
            resp = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            df = pd.DataFrame(resp['result']['list'], columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'
            ])
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='ms')
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].astype(float)
            return df.set_index('timestamp').sort_index()
        except Exception as e:
            print(f"Data fetch error: {e}")
            return pd.DataFrame()