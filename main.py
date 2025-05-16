# main.py
import argparse
import pandas as pd
from db_utils import connect_to_postgres, insert_stock_data, insert_stock_name, validate_symbols_or_names, get_symbol_names, all_symbols, data_already_exists
from data_utils import calculate_daily_returns, calculate_correlation_matrix, calculate_rolling_correlation
from plot_utils import plot_heatmap, plot_rolling_correlation
from fetch_data import fetch_stock_data

# Parse CLI arguments for high-level project execution

def parse_arguments():
    parser = argparse.ArgumentParser(description="Full financial data pipeline: fetch, store, analyze, plot")
    parser.add_argument("symbols", nargs="+", help="List of stock symbols or index names")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--window", type=int, default=30, help="Rolling window size in days")
    parser.add_argument("--name", type=str, default="None", help="Optional human-readable name for the symbol")
    return parser.parse_args()

# Main orchestrator
if __name__ == "__main__":
    args = parse_arguments()

    # Connect to database
    conn = connect_to_postgres()

    try:
        # Validate and resolve symbol names
        symbols, missing = validate_symbols_or_names(conn, args.symbols)
        if missing:
            raise ValueError(f"The following symbols/names were not found: {', '.join(missing)}")

        # Download and store data only if not already present
        for sym in symbols:
            if not data_already_exists(conn, sym, args.start_date, args.end_date):
                data = fetch_stock_data(sym, args.start_date, args.end_date)
                insert_stock_data(conn, sym, data)
            else:
                print(f"Data for {sym} from {args.start_date} to {args.end_date} already exists in database.")
            insert_stock_name(conn, sym, args.name)

        # Load full data from DB for selected symbols
        query = """
            SELECT symbol, date, close
            FROM stock_data
            WHERE symbol IN %s
            ORDER BY date;
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (tuple(symbols),))
            rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=["symbol", "date", "close"])
        df['date'] = pd.to_datetime(df['date'])
        pivoted = df.pivot(index="date", columns="symbol", values="close")

        # Calculate returns and correlation
        returns = calculate_daily_returns(pivoted)
        correlation_df = calculate_correlation_matrix(returns, symbols)

        # Plot heatmap of correlations
        symbol_names = get_symbol_names(conn, symbols)
        correlation_df_named = correlation_df.rename(columns=symbol_names, index=symbol_names)
        plot_heatmap(correlation_df_named, title="Correlation Matrix of Daily Returns")

        # Optionally: plot rolling correlation for first 2 symbols
        if len(symbols) >= 2:
            rolling = calculate_rolling_correlation(returns, symbols[0], symbols[1], args.window)
            plot_rolling_correlation(rolling, symbols[0], symbols[1], args.window)

    finally:
        conn.close()
        print("Pipeline execution completed.")
