import argparse
import pandas as pd
import psycopg2
import connectPostGre as co
import matplotlib.pyplot as plt

# Connect to PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        host=co.host,
        database=co.database,
        user=co.user,
        password=co.password,
        port=co.port
    )

# Load data from PostgreSQL
def load_stock_data(conn, symbols):
    query = """
        SELECT symbol, date, close
        FROM stock_data
        WHERE symbol IN %s
        ORDER BY date;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (tuple(symbols),))
        rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['symbol', 'date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    return df

# Compute daily returns
def calculate_returns(data):
    return data['close'].pct_change()

# Compute rolling correlation between two symbols
def calculate_rolling_correlation(data, symbols, window_size=30):
    # Pivot the data so each symbol has its own column
    pivoted_data = data.pivot(index='date', columns='symbol', values='close')
    returns = pivoted_data.pct_change().dropna()
    rolling_corr = returns[symbols[0]].rolling(window=window_size).corr(returns[symbols[1]])
    return rolling_corr

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Download data from the database and compute rolling correlation.")
    parser.add_argument("symbols", nargs="+", help="Symbols to observe (e.g., AAPL MSFT)")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    parser.add_argument("--avg_day", type=int, default=30, help="Number of days to use for the rolling average")
    return parser.parse_args()

# Validate input symbols or resolve names to symbols
def validate_symbols_or_names(conn, inputs):
    """
    Validates whether inputs are symbols or names.
    If a symbol is not found, searches in `index_info` using the name field.
    """
    symbols = []
    missing_inputs = []

    query_symbol = """
        SELECT symbol
        FROM index_info
        WHERE symbol = %s
    """
    query_name = """
        SELECT symbol
        FROM index_info
        WHERE name = %s
    """

    with conn.cursor() as cursor:
        for item in inputs:
            # Try matching as symbol
            cursor.execute(query_symbol, (item,))
            result = cursor.fetchone()

            if result:
                symbols.append(result[0])
            else:
                # Try resolving by name
                cursor.execute(query_name, (item,))
                result = cursor.fetchone()

                if result:
                    symbols.append(result[0])
                else:
                    missing_inputs.append(item)

    return symbols, missing_inputs


if __name__ == "__main__":
    conn = connect_to_postgres()
    try:
        args = parse_arguments()

        # Validate and resolve symbols or names
        symbols, missing_inputs = validate_symbols_or_names(conn, args.symbols)

        # Check for missing inputs
        if missing_inputs:
            raise ValueError(f"The following inputs were not found in the database: {', '.join(missing_inputs)}")

        # Rolling window size
        window_size = args.avg_day

        # Load data from the database
        stock_data = load_stock_data(conn, symbols)

        # Compute rolling correlation
        rolling_corr = calculate_rolling_correlation(stock_data, symbols, window_size)

        # Display the rolling correlation
        print("Rolling correlation calculated.")
        rolling_corr.plot(title=f"Rolling Correlation between {symbols[0]} and {symbols[1]} ({window_size}-day window)")
        plt.xlabel("Date")
        plt.ylabel("Correlation")
        plt.ylim(-1, 1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    finally:
        conn.close()
