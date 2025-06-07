import argparse
import psycopg2
import connectPostGre as co
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# Connect to the PostgreSQL database
def connect_to_postgres():
    return psycopg2.connect(
        host=co.host,
        database=co.database,
        user=co.user,
        password=co.password,
        port=co.port
    )

# Load stock data for given symbols from the database
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
    
    # Create a DataFrame from the fetched rows
    df = pd.DataFrame(rows, columns=['symbol', 'date', 'close'])
    df['date'] = pd.to_datetime(df['date'])
    return df

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Produce a correlation matrix for given stock/index symbols")
    parser.add_argument("--symbols", type=list, default=[], help="List of symbols or names to compare")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    return parser.parse_args()

# Validate whether inputs are symbols or names; retrieve actual symbols
def validate_symbols_or_names(conn, inputs):
    """
    Validates if the inputs are stock symbols or index names.
    If a symbol is not found, it tries to find the corresponding symbol from the name in the `index_info` table.
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
            # Try to find the symbol directly
            cursor.execute(query_symbol, (item,))
            result = cursor.fetchone()

            if result:
                symbols.append(result[0])
            else:
                # Try to find it by name instead
                cursor.execute(query_name, (item,))
                result = cursor.fetchone()

                if result:
                    symbols.append(result[0])
                else:
                    missing_inputs.append(item)

    return symbols, missing_inputs

# Retrieve all available symbols from the database
def all_symbols(conn):
    """
    If no symbols are specified, fetch all symbols available in the database.
    """
    query_symbol = """
        SELECT symbol
        FROM index_info
    """

    with conn.cursor() as cursor:
        cursor.execute(query_symbol)
        result = cursor.fetchall()
        symbols = [row[0] for row in result]  # Flatten the result into a simple list

    return symbols

# Retrieve the names of the given symbols
def get_symbol_names(conn, symbols):
    """
    Get the human-readable names corresponding to each symbol from the index_info table.
    """
    query = """
        SELECT symbol, name
        FROM index_info
        WHERE symbol IN %s
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (tuple(symbols),))
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}

# Main script logic
if __name__ == "__main__":
    conn = connect_to_postgres()
    try:
        args = parse_arguments()

        # Validate user inputs, check if they are symbols or names
        symbols, missing_inputs = validate_symbols_or_names(conn, args.symbols)

        # Raise an error if any input was not found
        if missing_inputs:
            raise ValueError(f"The following inputs were not found in the database: {', '.join(missing_inputs)}")
    
        # Load stock data based on valid symbols
        if symbols:
            stock_data = load_stock_data(conn, symbols)
        else:
            symbols = all_symbols(conn)
            stock_data = load_stock_data(conn, symbols)

        # Get the display names for each symbol
        symbol_names = get_symbol_names(conn, symbols)

        # Pivot data so each symbol is a column and each row is a date
        pivoted_data = stock_data.pivot(index='date', columns='symbol', values='close')

        # Ensure all columns (symbols) exist in the data
        for symbol in symbols:
            if symbol not in pivoted_data.columns:
                raise ValueError(f"Could not find data for {symbol}")

        # Compute daily returns
        returns = pivoted_data.pct_change().dropna()

        # Calculate correlation matrix between symbol returns
        correlation_matrix = []
        for i in range(len(symbols)):
            line = []
            for j in range(len(symbols)):
                line.append(returns[symbols[i]].corr(returns[symbols[j]]))
            correlation_matrix.append(line)

        # Convert correlation matrix to DataFrame for styling
        correlation_df = pd.DataFrame(
            correlation_matrix, 
            columns=[symbol_names[s] for s in symbols], 
            index=[symbol_names[s] for s in symbols]
        )

        # Rename columns of returns for better readability
        returns.columns = [symbol_names[s] for s in returns.columns]

        # Plot a scatter matrix (pairplot) of the returns
        sns.pairplot(returns, diag_kind="kde", corner=True)
        plt.suptitle("Scatter Matrix of Returns", y=1.02, fontsize=16)
        plt.show()

    finally:
        conn.close()