# db_utils.py
import psycopg2
from psycopg2.extras import execute_batch
import connectPostGre as co

# Establish a connection to the PostgreSQL database using credentials from a config file

def connect_to_postgres():
    return psycopg2.connect(
        host=co.host,
        database=co.database,
        user=co.user,
        password=co.password,
        port=co.port
    )

# Insert stock data into the stock_data table, avoiding duplicates via ON CONFLICT clause

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

# Insert or update the symbol-name pair in the index_info table

def insert_stock_name(conn, symbol, name):
    if name == "None":
        return

    query = """
        INSERT INTO index_info (symbol, name)
        VALUES (%s, %s)
        ON CONFLICT (symbol) DO UPDATE
        SET name = EXCLUDED.name;
    """

    with conn.cursor() as cursor:
        cursor.execute(query, (symbol, name))
        conn.commit()

# Validate input strings as either symbol or name, and map them to valid symbols from DB

def validate_symbols_or_names(conn, inputs):
    symbols = []
    missing_inputs = []
    query_symbol = "SELECT symbol FROM index_info WHERE symbol = %s"
    query_name = "SELECT symbol FROM index_info WHERE name = %s"

    with conn.cursor() as cursor:
        for item in inputs:
            cursor.execute(query_symbol, (item,))
            result = cursor.fetchone()
            if result:
                symbols.append(result[0])
                continue
            cursor.execute(query_name, (item,))
            result = cursor.fetchone()
            if result:
                symbols.append(result[0])
            else:
                missing_inputs.append(item)

    return symbols, missing_inputs

# Retrieve name-to-symbol mapping for UI display or reporting

def get_symbol_names(conn, symbols):
    query = "SELECT symbol, name FROM index_info WHERE symbol IN %s"
    with conn.cursor() as cursor:
        cursor.execute(query, (tuple(symbols),))
        rows = cursor.fetchall()
    return {row[0]: row[1] for row in rows}

# Get a list of all known symbols in the database

def all_symbols(conn):
    query = "SELECT symbol FROM index_info"
    with conn.cursor() as cursor:
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall()]
    
# Check if data for the symbol and date range already exists in the database

def data_already_exists(conn, symbol, start_date, end_date):
    query = """
        SELECT COUNT(*) FROM stock_data
        WHERE symbol = %s AND date BETWEEN %s AND %s;
    """
    with conn.cursor() as cursor:
        cursor.execute(query, (symbol, start_date, end_date))
        result = cursor.fetchone()
        return result[0] > 0