import argparse
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_batch
import connectPostGre as co

# Connect to PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        host=co.host,
        database=co.database,
        user=co.user,
        password=co.password,
        port=co.port
    )

# Download stock data using yfinance
def fetch_stock_data(symbol, start_date, end_date):
    print(f"Downloading data for {symbol}...")
    data = yf.download(symbol, start=start_date, end=end_date)
    if 'Ticker' in data.columns.names:  # Remove multi-index if present
        data.columns = data.columns.droplevel('Ticker')
    return data

# Insert stock data into PostgreSQL
def insert_stock_data(conn, symbol, data):
    if data is None or data.empty:
        print(f"No data to insert for {symbol}.")
        return
    with conn.cursor() as cursor:
        execute_batch(cursor, """
            INSERT INTO stock_data (symbol, date, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol, date) DO NOTHING;
        """, [
            (symbol, index.date(), float(row['Open']), float(row['High']),
             float(row['Low']), float(row['Close']), int(row['Volume']))
            for index, row in data.iterrows()
        ])
    conn.commit()
    print(f"Data for {symbol} inserted into the database.")

# Insert or update symbol name into index_info table
def insert_stock_name(conn, symbol, name):
    if name == "None":
        return

    query_check = """
        SELECT symbol
        FROM index_info
        WHERE symbol = %s
    """

    query_insert = """
        INSERT INTO index_info (symbol, name)
        VALUES (%s, %s)
        ON CONFLICT (symbol) DO UPDATE
        SET name = EXCLUDED.name;
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(query_check, (symbol,))
            result = cursor.fetchone()

            if result:
                print(f"Symbol '{symbol}' already exists in the database. Updating name if needed.")
            
            cursor.execute(query_insert, (symbol, name))
            conn.commit()
            print(f"Symbol '{symbol}' with name '{name}' has been inserted/updated.")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting/updating symbol: {e}")

# Parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Download stock market data and insert it into PostgreSQL.")
    parser.add_argument("symbol", type=str, help="Stock symbol (e.g., AAPL)")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    parser.add_argument("--name", type=str, default="None", help="Stock name (uppercase, no spaces or apostrophes)")
    return parser.parse_args()

# Main
if __name__ == "__main__":
    args = parse_arguments()

    symbol = args.symbol
    name = args.name
    start_date = args.start_date
    end_date = args.end_date

    conn = connect_to_postgres()
    try:
        # Download and insert data
        data = fetch_stock_data(symbol, start_date, end_date)
        insert_stock_data(conn, symbol, data)
        insert_stock_name(conn, symbol, name)
    finally:
        conn.close()
        print("All data has been successfully inserted.")
