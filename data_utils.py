# data_utils.py
import pandas as pd
import numpy as np

# Calculate daily percentage returns from price data

def calculate_daily_returns(pivoted_data):
    return pivoted_data.pct_change().dropna()

# Compute correlation matrix between multiple time series

def calculate_correlation_matrix(returns, symbols):
    matrix = []
    for i in range(len(symbols)):
        row = []
        for j in range(len(symbols)):
            row.append(returns[symbols[i]].corr(returns[symbols[j]]))
        matrix.append(row)
    return pd.DataFrame(matrix, columns=symbols, index=symbols)

# Calculate rolling correlation between two time series over a defined window

def calculate_rolling_correlation(returns, sym1, sym2, window):
    return returns[sym1].rolling(window=window).corr(returns[sym2])