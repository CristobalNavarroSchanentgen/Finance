# ANALYSE RESULTS FROM MY LOCAL TRADES DB

from sqlalchemy import create_engine
import pandas as pd

#strats ---------
#strat = 'macd_crossover_1006'
#strat = 'algovibe1'
#strat = 'first_classifier_2_mins_09995'
#strat = 'first_classifier_2_mins_0999'
#strat = 'algovibeS0997'
#strat = 'first_classifier_2_mins'
#strat = 'macd_crossover'


# Create the database connection using SQLAlchemy
engine = create_engine('postgresql://username:password@localhost/binance')

# Write your SQL query
query = f"SELECT * FROM trades WHERE strategy_name='{strat}'"

# Use pandas to import the data into a DataFrame
trades = pd.read_sql(query, engine)


def apply_empirical_metrics(trades):
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


apply_empirical_metrics(trades)
