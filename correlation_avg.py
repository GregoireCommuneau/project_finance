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

# Load stock data from PostgreSQL for given symbols
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
    # Create a DataFrame from the data
    df = pd.DataFrame(rows, columns=['symbol', 'date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    return df

# Compute daily returns
def calculate_returns(data):
    return data['close'].pct_change()

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Download stock data from the database and compute return correlation.")
    parser.add_argument("symbols", nargs="+", default="NVDA", help="List of 2 stock/index names or symbols (e.g., AAPL NVDA)")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    return parser.parse_args()

# Validate input symbols or resolve names to symbols using the index_info table
def validate_symbols_or_names(conn, inputs):
    """
    Validates if the inputs are stock symbols or names.
    If a symbol is not found, tries to resolve it using the name in the `index_info` table.
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
            # Check if it's a direct symbol
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

        # Retrieve user input (symbols or names)
        inputs = args.symbols

        # Validate input symbols or resolve names
        symbols, missing_inputs = validate_symbols_or_names(conn, inputs)

        # Handle missing entries
        if missing_inputs:
            raise ValueError(f"The following entries were not found in the database: {', '.join(missing_inputs)}")

        # Load stock data for the selected symbols
        stock_data = load_stock_data(conn, symbols)

        # Pivot data so each symbol is a column and each row is a date
        pivoted_data = stock_data.pivot(index='date', columns='symbol', values='close')
        print(pivoted_data)

        # Compute daily returns
        returns = pivoted_data.pct_change().dropna()

        # Calculate correlation between the two selected symbols
        correlation = returns[symbols[0]].corr(returns[symbols[1]])

        # Display the result
        print(f"Correlation between {args.symbols[0]} and {args.symbols[1]}: {correlation}")
    finally:
        conn.close()