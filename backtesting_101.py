import time
import datetime
from binance import Client
import pandas as pd
import numpy as np
import ta


client = Client(api_key, api_secret)


def getminutedata(symbol, interval, lookback):
    frame = pd.DataFrame(client.get_historical_klines(symbol,
                                                     interval,
                                                     lookback + ' min ago UTC'))
    frame = frame.iloc[:,:6]
    frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit='ms')
    frame = frame.astype(float)
    return frame


def get_backtest_database(symbol, interval, lookback):
    df = getminutedata(symbol, interval, lookback)
    df['Price'] = df['Open'].shift(-1)
    df = df.drop(df.index[-1])
    return df


## STRATS ##

#%run ./signal_algovibeS0997.ipynb
#%run ./signal_vwap_breakout.ipynb
%run ./signal_macd_crossover.ipynb
#%run ./signal_rsi_ma_crossover.ipynb


## BACKTESTING FUNCTION ##

def backtest_strategy(pair, qty, strategy_name, lookback, open_position=False): 
    df = get_backtest_database(pair, '1m', lookback) # Retrieve historical data

    #df = df.resample('45S').interpolate(method='linear') # DANGER WITH GRANULARITY
    #df = df.resample('45S').ffill()

    applytechnicals(df) # apply technical analysis
    inst = Signals(df, 5) # instantiate signals
    inst.decide() # make decision based on signals

    # Initialize an empty DataFrame to store trades
    trades = pd.DataFrame(columns=['buy_date', 'sell_date', 'buy_price', 'sell_price', 'qty', 'profit_loss'])
    
    #for i in range(len(df)-1):
    i = 0
    while i < len(df)-1:
        # Simulate a buy order
        i += 1
        if not open_position and df.Buy.iloc[i]:
            buyprice = df.Open.iloc[i+1]
            open_position = True
            opening_date = df.index[i+1] 

            # Look for a selling opportunity
            while open_position and i < len(df) - 1:
                i += 1
                # Simulate a sell order
                if df.Close[i] <= buyprice * 0.997:
                    sellprice = buyprice * 0.997
                    closing_date = df.index[i+1]
                    profit_loss = qty * (sellprice - buyprice)

                    # Add the trade to the trades DataFrame
                    new_trade = pd.DataFrame([{
                        'buy_date': opening_date,
                        'sell_date': closing_date,
                        'buy_price': buyprice,
                        'sell_price': sellprice,
                        'qty': qty,
                        'profit_loss': profit_loss
                    }], index=[i])
                    trades = pd.concat([trades, new_trade])

                    open_position = False
                
                elif df.Close[i] >= buyprice * 1.006:
                    sellprice = buyprice * 1.006
                    closing_date = df.index[i+1]
                    profit_loss = qty * (sellprice - buyprice)

                    # Add the trade to the trades DataFrame
                    new_trade = pd.DataFrame([{
                        'buy_date': opening_date,
                        'sell_date': closing_date,
                        'buy_price': buyprice,
                        'sell_price': sellprice,
                        'qty': qty,
                        'profit_loss': profit_loss
                    }], index=[i])
                    trades = pd.concat([trades, new_trade])

                    open_position = False
                    

    return trades



## ANALYSIS FUNCTION ##

def backtesting_results(pair, qty, strategy_name, lookback):
    # backtest the strategy
    trades = backtest_strategy(pair, qty, strategy_name, lookback)
    
    # add sumarizing columns
    trades['absolute_tracker'] = trades['profit_loss'].cumsum()
    trades['profit_loss_relative'] = trades['profit_loss'] / (trades['buy_price'] * 0.001)
    trades['relative_tracker'] = (1 + trades['profit_loss_relative']).cumprod()
   
    # calculate the metrics
    absolute_profit = trades['profit_loss'].sum().round(4)
    return_on_the_dollar = trades['relative_tracker'].iloc[-1].round(4)
    relative_profit = (100 * (return_on_the_dollar - 1)).round(4)
    lowest_point = trades['absolute_tracker'].min().round(4)
    highest_point = trades['absolute_tracker'].max().round(4)
    positive_count = (trades['profit_loss'] > 0).sum()
    negative_count = (trades['profit_loss'] < 0).sum()
    profitable_trades = (100 * positive_count / (positive_count + negative_count)).round(2)
    num_trades = len(trades)

    
    # print the report
    print('------- FULL REPORT -------\n\n')
    print('1. STRATEGY TYPE\n')
    print(f'number of trades : {num_trades}')
    print(f'profitable trades : {profitable_trades} %\n')
    print('2. METRICS\n')
    print(f'relative profit : {relative_profit} %')
    print(f'absolute profit : {absolute_profit} $')
    print(f'return on the dollar : {return_on_the_dollar} $\n')
    print('3. AMPLITUDE\n')
    print(f'lowest point : {lowest_point} $')
    print(f'highest point : {highest_point} $')



backtest_strategy('BTCTUSD', 0.001, 'algovibeS0997', '601')  # If you want to go through the individual trades, need to add a print statement if not using jupyter.
backtesting_results('BTCTUSD', 0.001, 'algovibeS0997', '4321')
