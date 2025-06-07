import argparse
import psycopg2
import connectPostGre as co
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np


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

# Parse CLI arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate a correlation heatmap between financial instruments.")
    parser.add_argument("--symbols", nargs="+", help="List of all stock/index symbols or names to compare")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    return parser.parse_args()

# Validate whether the inputs are symbols or names and resolve them
def validate_symbols_or_names(conn, inputs):
    """
    Validate whether the inputs are stock symbols or readable names.
    If not found as a symbol, attempt to resolve by name in the `index_info` table.
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
            # Check if input is a direct symbol
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

# Get all available symbols if none are passed
def all_symbols(conn):
    query_symbol = """
        SELECT symbol
        FROM index_info
    """
    with conn.cursor() as cursor:
        cursor.execute(query_symbol)
        result = cursor.fetchall()
        symbols = [row[0] for row in result]
    return symbols

# Retrieve human-readable names for each symbol
def get_symbol_names(conn, symbols):
    query = """
        SELECT symbol, name
        FROM index_info
        WHERE symbol IN %s
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (tuple(symbols),))
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}

# Main execution
if __name__ == "__main__":
    conn = connect_to_postgres()
    try:
        args = parse_arguments()

        # Validate inputs and resolve symbols if needed
        symbols, missing_inputs = validate_symbols_or_names(conn, args.symbols)

        if missing_inputs:
            raise ValueError(f"The following inputs were not found in the database: {', '.join(missing_inputs)}")
    
        # Load stock data from the database
        if symbols:
            stock_data = load_stock_data(conn, symbols)
        else:
            symbols = all_symbols(conn)
            stock_data = load_stock_data(conn, symbols)

        # Get display names for each symbol
        symbol_names = get_symbol_names(conn, symbols)

        # Pivot data so each symbol is a column
        pivoted_data = stock_data.pivot(index='date', columns='symbol', values='close')

        # Ensure all required columns exist
        for symbol in symbols:
            if symbol not in pivoted_data.columns:
                raise ValueError(f"Could not find data for symbol {symbol}")

        # Calculate daily returns
        returns = pivoted_data.pct_change().dropna()

        # Calculate correlation matrix
        correlation_matrix = []
        for i in range(len(symbols)):
            line = []
            for j in range(len(symbols)):
                line.append(returns[symbols[i]].corr(returns[symbols[j]]))
            correlation_matrix.append(line)

        # Convert to DataFrame for easier styling
        correlation_df = pd.DataFrame(
            correlation_matrix,
            columns=[symbol_names[s] for s in symbols],
            index=[symbol_names[s] for s in symbols]
        )

        # Mask the upper triangle of the heatmap
        mask = np.triu(np.ones(correlation_df.shape), k=1)

        # Create heatmap with seaborn
        plt.figure(figsize=(12, 10))
        sns.heatmap(
            correlation_df,
            mask=mask,  # Hide upper triangle
            annot=True,  # Show values in cells
            fmt=".2f",  # Number formatting
            cmap="coolwarm",  # Color palette
            cbar_kws={'label': 'Correlation coefficient'},  # Color bar label
        )

        plt.title("Return Correlation Matrix", fontsize=16)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()  # Adjust spacing to prevent overlap
        plt.show()

    finally:
        conn.close()
