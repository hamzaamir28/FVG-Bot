import pandas as pd
from strategies.data_feed import BybitDataFeed
from strategies.fvg_strat import FVGStrategy
from strategies.backtest import BacktestFVGStrategy
from backtesting import Backtest
from config import BYBIT_API_KEY, BYBIT_API_SECRET, TESTNET
import time
import os

def run_backtest():
    """Backtesting mode"""
    print("Running backtest...")
    
    # Load your historical data here
    # Example:
    data = pd.read_csv('BTCUSDT_2024.csv').rename(columns={'open':'Open','high':'High','low':'Low','close':'Close','volume':'Volume'}).assign(time=lambda x: pd.to_datetime(x['time'], unit='ms')).set_index('time')[['Open','High','Low','Close','Volume']]
    bt = Backtest(data, BacktestFVGStrategy,
                 cash = 1000000,
                 commission=.00075,
                 margin=1.0,
                 exclusive_orders=True)
    
    results = bt.run()
    print("\nBacktest Results:")
    print(results)
    bt.plot()

def run_live():
    """Live trading mode"""
    if not BYBIT_API_KEY or not BYBIT_API_SECRET:
        print("Error: Bybit API credentials missing in config.py")
        return
    
    print("Starting live trading...")
    data_feed = BybitDataFeed(BYBIT_API_KEY, BYBIT_API_SECRET, TESTNET)
    strategy = FVGStrategy()
    
    while True:
        try:
            # Get data
            df_10m = data_feed.get_ohlc("BTCUSDT", "10", 200)
            df_5m = data_feed.get_ohlc("BTCUSDT", "5", 200)
            df_30m = data_feed.get_ohlc("BTCUSDT", "30", 100)
            
            if df_10m.empty or df_5m.empty:
                time.sleep(10)
                continue
                
            # Process strategy
            signal = strategy.process(df_10m, df_5m, df_30m)
            print(signal)
            
            if signal:
                print(f"\nSignal generated at {pd.Timestamp.now()}:")
                print(f"Direction: {signal.direction.name}")
                print(f"Entry: {signal.entry:.2f}")
                print(f"Stop Loss: {signal.stop_loss:.2f}")
                print(f"Take Profit: {signal.take_profit:.2f}")
                # Add Bybit order execution here
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\nStopped by user")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    print("FVG Trading System")
    print("1. Backtest")
    print("2. Live Trading")
    
    choice = input("Select mode (1/2): ").strip()
    
    if choice == "1":
        run_backtest()
    elif choice == "2":
        run_live()
    else:
        print("Invalid choice")