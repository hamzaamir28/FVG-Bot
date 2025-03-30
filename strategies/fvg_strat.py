from typing import Optional
import pandas as pd
from .technical_indicators import TechnicalIndicators
from .FVG_manager import FVGManager, FVG
from .trade_signal import TradeSignal, TradeDirection, TradeManager

class FVGStrategy:
    """Core FVG trading strategy implementation"""
    
    def __init__(self):
        self.indicators = TechnicalIndicators()
        self.fvg_manager = FVGManager()
        self.trade_manager = TradeManager()
    
    def process(self, df_10m: pd.DataFrame, df_5m: pd.DataFrame, df_30m: Optional[pd.DataFrame] = None) -> Optional[TradeSignal]:
        """Main strategy processing method"""
        # Add indicators
        df_10m = self._add_indicators(df_10m)
        df_5m = self._add_indicators(df_5m)
        
        # Update FVGs
        self.fvg_manager.active_fvgs.extend(self.fvg_manager.detect(df_10m))
        current_price = df_5m['close'].iloc[-1]
        current_candle = df_5m.iloc[-1]
        self.fvg_manager.update_status(
            current_price=current_price,
            current_high=current_candle['high'],
            current_low=current_candle['low']
        )
        
        print(self.fvg_manager.active_fvgs)
        # Check entry if no active trade
        print(self.trade_manager.active_trade)
        if self.trade_manager.active_trade is None:
            return self._check_entry(df_10m, df_5m, df_30m)
        return None
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds required indicators to DataFrame"""
        df = df.copy()
        df['ema12'] = self.indicators.calculate_ema(df['close'], 12)
        df['ema21'] = self.indicators.calculate_ema(df['close'], 21)
        return df
    
    def _check_entry(self, df_10m: pd.DataFrame, df_5m: pd.DataFrame, df_30m: Optional[pd.DataFrame]) -> Optional[TradeSignal]:
        """Checks all entry conditions for long trades"""
        prev_10m = df_10m.iloc[-2]
        if not ((prev_10m['open'] > prev_10m['ema12'] or 
                prev_10m['open'] > prev_10m['ema21']) and
               (prev_10m['close'] < prev_10m['ema12'] or 
                prev_10m['close'] < prev_10m['ema21'])):
            return None
            
        dev_line, sl = self.indicators.find_deviation_line(df_5m)
        if dev_line is None or df_5m['close'].iloc[-1] <= dev_line:
            return None
            
        # Determine trade type and TP
        is_reversal = self._is_reversal_trade(df_10m, df_30m)
        tp = self._calculate_take_profit(is_reversal, df_10m, df_5m)
        
        return self.trade_manager.create_signal(
            entry=df_5m['close'].iloc[-1],
            stop_loss=sl,
            take_profit=tp,
            direction=TradeDirection.LONG,
            timestamp=df_5m.index[-1],
            dev_line=dev_line
        )
    
    def _is_reversal_trade(self, df_10m: pd.DataFrame, df_30m: Optional[pd.DataFrame]) -> bool:
        """Determines if trade is reversal or continuation"""
        if df_30m is None or len(df_30m) < 50:
            return False
            
        df_30m['sma50'] = self.indicators.calculate_sma(df_30m['close'], 50)
        last_30m = df_30m.iloc[-1]
        
        return (last_30m['sma50'] > df_10m['ema12'].iloc[-1] and 
                last_30m['sma50'] > df_10m['ema21'].iloc[-1])
    
    def _calculate_take_profit(self, is_reversal: bool, df_10m: pd.DataFrame, df_5m: pd.DataFrame) -> float:
        """Calculates dynamic take profit"""
        if is_reversal:
            # Reversal TP logic
            return df_10m['close'].iloc[-1] * 1.02  # 2% target
        else:
            # Continuation TP logic
            return df_10m['close'].iloc[-1] * 1.01  # 1% target