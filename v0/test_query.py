import yfinance as yf

# Example usage
symbol = "AAPL"  # Apple Inc.
start_date = "2023-01-01"
end_date = "2023-12-31"

# Download historical stock data
data = yf.download(symbol, start=start_date, end=end_date)

# Display the data
print(data)