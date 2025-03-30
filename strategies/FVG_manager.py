from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import pandas as pd

@dataclass
class FVG:
    """Represents a Fair Value Gap pattern"""
    high: float
    low: float
    timestamp: datetime
    is_bullish: bool
    filled: bool = False
    invalidated: bool = False

class FVGManager:
    """Manages FVG detection and lifecycle"""
    
    def __init__(self):
        self.active_fvgs: List[FVG] = []
        self.filled_fvgs: List[FVG] = []
    
    def detect(self, ohlc_data: pd.DataFrame) -> List[FVG]:
        """Identifies new FVGs in OHLC data"""
        new_fvgs = []
        
        for i in range(1, len(ohlc_data)-1):
            current = ohlc_data.iloc[i]
            previous = ohlc_data.iloc[i-1]
            next_candle = ohlc_data.iloc[i+1]
            
            # Bullish FVG condition
            if current['close'] > previous['low'] and next_candle['high'] < previous['low']:
                new_fvgs.append(FVG(
                    high=previous['low'],
                    low=next_candle['high'],
                    timestamp=current.name,
                    is_bullish=True
                ))
            
            # Bearish FVG condition
            elif current['close'] < previous['high'] and next_candle['low'] > previous['high']:
                new_fvgs.append(FVG(
                    high=next_candle['low'],
                    low=previous['high'],
                    timestamp=current.name,
                    is_bullish=False
                ))
        
        return new_fvgs
    
    def update_status(self, current_price: float, current_high: float, current_low: float):
        """Updates FVG fill/invalidation status"""
        for fvg in self.active_fvgs[:]:
            # Check for fills
            if not fvg.filled:
                if (fvg.is_bullish and current_price <= fvg.low) or \
                   (not fvg.is_bullish and current_price >= fvg.high):
                    fvg.filled = True
                    self.filled_fvgs.append(fvg)
                    self.active_fvgs.remove(fvg)
            
            # Check for invalidations
            if not fvg.invalidated:
                if fvg.is_bullish:
                    if current_high > fvg.high or current_low < fvg.low:
                        fvg.invalidated = True
                        self.active_fvgs.remove(fvg)
                else:
                    if current_low < fvg.low or current_high > fvg.high:
                        fvg.invalidated = True
                        self.active_fvgs.remove(fvg)