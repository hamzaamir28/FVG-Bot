from backtesting import Strategy
from backtesting.lib import resample_apply
from strategies.fvg_strat import FVGStrategy
from strategies.trade_signal import TradeDirection  # Added import

class BacktestFVGStrategy(Strategy):
    """Adapts FVGStrategy for backtesting.py"""
    
    def init(self):
        self.strategy = FVGStrategy()
        
        # Create multi-timeframe data
        self.df_10m = resample_apply('10min', self.data.df)
        self.df_5m = resample_apply('5min', self.data.df)
        self.df_30m = resample_apply('30min', self.data.df)
    
    def next(self):
        signal = self.strategy.process(
            df_10m=self.df_10m,
            df_5m=self.df_5m,
            df_30m=self.df_30m
        )
        
        if signal and not self.position:
            if signal.direction == TradeDirection.LONG:
                self.buy(sl=signal.stop_loss, tp=signal.take_profit)
            else:
                self.sell(sl=signal.stop_loss, tp=signal.take_profit)