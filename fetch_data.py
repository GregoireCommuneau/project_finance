# fetch_data.py
import yfinance as yf

# Download historical stock data for a given symbol from Yahoo Finance

def fetch_stock_data(symbol, start_date, end_date):
    print(f"Downloading data for {symbol}...")
    data = yf.download(symbol, start=start_date, end=end_date)
    if 'Ticker' in data.columns.names:
        data.columns = data.columns.droplevel('Ticker')
    return data