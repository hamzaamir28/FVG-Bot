from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Optional

class TradeDirection(Enum):
    LONG = auto()
    SHORT = auto()

class TradeStatus(Enum):
    PENDING = auto()
    ACTIVE = auto()
    CLOSED = auto()

@dataclass
class TradeSignal:
    """Complete trade specification"""
    entry: float
    stop_loss: float
    take_profit: float
    direction: TradeDirection
    timestamp: datetime
    status: TradeStatus = TradeStatus.PENDING
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    fvg_id: Optional[str] = None
    dev_line: Optional[float] = None

class TradeManager:
    """Manages trade lifecycle and execution"""
    
    def __init__(self):
        self.active_trade: Optional[TradeSignal] = None
    
    def create_signal(self, **kwargs) -> Optional[TradeSignal]:
        """Creates new trade if none active"""
        if self.active_trade is None:
            return TradeSignal(**kwargs)
        return None
    
    def check_exit(self, current_candle: dict):
        """Checks if active trade should exit"""
        if self.active_trade is None:
            return
            
        if self.active_trade.direction == TradeDirection.LONG:
            if current_candle['low'] <= self.active_trade.stop_loss:
                self._close_trade(self.active_trade.stop_loss, "SL")
            elif current_candle['high'] >= self.active_trade.take_profit:
                self._close_trade(self.active_trade.take_profit, "TP")
        else:  # SHORT
            if current_candle['high'] >= self.active_trade.stop_loss:
                self._close_trade(self.active_trade.stop_loss, "SL")
            elif current_candle['low'] <= self.active_trade.take_profit:
                self._close_trade(self.active_trade.take_profit, "TP")
    
    def _close_trade(self, exit_price: float, reason: str):
        """Handles trade closure"""
        if self.active_trade:
            self.active_trade.exit_price = exit_price
            self.active_trade.exit_reason = reason
            self.active_trade.status = TradeStatus.CLOSED
            self.active_trade = None