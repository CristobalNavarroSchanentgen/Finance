# A SIMPLE STRATEGY THAT WORKED WELL FOR ME
# You can notice that in order to optimize cloud cost (the bot was hosted on gcp) I use a print statement for sql inserts instead of managing an expansive cloud sql service. 

import numpy as np
import pandas as pd
import ta
from binance import Client
from datetime import timedelta
import datetime
import time

# client

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


def applytechnicals(df):
    df['MACD_diff'] = ta.trend.macd_diff(df.Close, fillna=True)
    df['Buy_MACD_Crossover'] = np.where((df['MACD_diff'] > 0) 
                                                 & (df['MACD_diff'].shift() < 0), 1, 0)
    
    
    df.dropna(inplace=True)

class Signals:
    
    def __init__(self, df, lookback):
        self.df = df
        self.lookback = lookback
    
    def decide(self):
        self.df['Buy'] = self.df['Buy_MACD_Crossover']



def strategy(pair, qty, strategy_name, open_position=False, retry_delay=1): 
    while True:
        try:                                                                 # important to handle timeout errors with binance api
            df = getminutedata(pair, '1m', '100')
            applytechnicals(df) 
            inst = Signals(df, 5)
            inst.decide()
    
            if df.Buy.iloc[-1]:
                order = client.create_order(symbol=pair,
                                        side='BUY',
                                        type='MARKET',
                                        quantity=qty)
                buyprice = float(order['fills'][0]['price'])
                open_position = True
                opening_date = datetime.datetime.now()
    
            while open_position:
                time.sleep(0.5)
                df = getminutedata(pair, '1m', '2')
        
                if df.Close[-1] <= buyprice * 0.997 or df.Close[-1] >= buyprice * 1.005:
                    order = client.create_order(symbol=pair,
                                            side='SELL',
                                            type='MARKET',
                                            quantity=qty)
                    sellprice = float(order['fills'][0]['price'])
                    closing_date = datetime.datetime.now()
                    duration = closing_date - opening_date
                    profit_loss = qty * (sellprice - buyprice)
            
                    print(f"INSERT INTO trades (buy_price, sell_price, strategy_name, volume, opening_date, closing_date, duration, profit_loss) VALUES ({buyprice}, {sellprice}, '{strategy_name}', {qty}, '{opening_date}', '{closing_date}', INTERVAL '{str(duration)}', {profit_loss});", flush=True)
                    break

            # If the code reached this point, it means there were no exceptions. 
            # Reset the retry_delay to its initial value
            retry_delay = 1
            break

        except Exception as e:
            print(f"Exception encountered: {str(e)}", flush=True)
            print(f"Retrying in {retry_delay} seconds...", flush=True)
            time.sleep(retry_delay)

            # Exponential backoff
            retry_delay *= 2



while True:
    strategy('BTCTUSD', 0.001, 'macd_crossover')
    time.sleep(0.5)
