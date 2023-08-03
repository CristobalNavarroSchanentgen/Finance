# EXCTRACTING INDICATORS FROM YFINANCE API

import yfinance as yf

def get_last_price(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="1d")
    return history['Close'].iloc[-1]


# Don't forget to check the updated tickers

def main():
    assets = {
        "S&P 500": "^GSPC",
        "Nasdaq": "^IXIC",
        "Dow Jones Industrial Average": "^DJI",
        "US 10 Years Treasury Yields": "^TNX",
        "VIX": "^VIX",
        "S&P Bond Index": "^SP500BDT", #
        "Bitcoin": "BTC-USD",
        "Gold": "GC=F",
        "WTI": "CL=F"
    }

    for name, ticker in assets.items():
        price = get_last_price(ticker)
        print(f"{name}: {price}")

if __name__ == "__main__":
    main()
