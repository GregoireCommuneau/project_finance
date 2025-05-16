import argparse
import psycopg2
import connectPostGre as co
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx


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
    parser = argparse.ArgumentParser(description="Generate a graph showing correlation between all selected symbols.")
    parser.add_argument("--symbols", type=list, default=[], help="List of all symbols or names to compare")
    parser.add_argument("--start_date", type=str, default="2023-01-01", help="Start date (format YYYY-MM-DD)")
    parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date (format YYYY-MM-DD)")
    return parser.parse_args()

# Validate whether the input is a symbol or name, and resolve accordingly
def validate_symbols_or_names(conn, inputs):
    """
    Validates whether the inputs are stock symbols or names.
    If a symbol is not found, it tries to resolve it using the name field in `index_info`.
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
            # Try matching by symbol
            cursor.execute(query_symbol, (item,))
            result = cursor.fetchone()

            if result:
                symbols.append(result[0])
            else:
                # Try matching by name
                cursor.execute(query_name, (item,))
                result = cursor.fetchone()

                if result:
                    symbols.append(result[0])
                else:
                    missing_inputs.append(item)

    return symbols, missing_inputs

# If no symbols provided, fetch all available
def all_symbols(conn):
    query = """
        SELECT symbol
        FROM index_info
    """
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        symbols = [row[0] for row in result]
    return symbols

# Get readable names for each symbol
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

# Main logic
if __name__ == "__main__":
    conn = connect_to_postgres()
    try:
        args = parse_arguments()

        # Validate input (symbols or names)
        symbols, missing_inputs = validate_symbols_or_names(conn, args.symbols)

        # Handle any missing inputs
        if missing_inputs:
            raise ValueError(f"The following entries were not found in the database: {', '.join(missing_inputs)}")

        # Load data
        if symbols:
            stock_data = load_stock_data(conn, symbols)
        else:
            symbols = all_symbols(conn)
            stock_data = load_stock_data(conn, symbols)

        # Get display names
        symbol_names = get_symbol_names(conn, symbols)

        # Pivot the data so each symbol is a column
        pivoted_data = stock_data.pivot(index='date', columns='symbol', values='close')

        # Ensure all columns exist
        for symbol in symbols:
            if symbol not in pivoted_data.columns:
                raise ValueError(f"No data found for {symbol}")

        # Compute returns
        returns = pivoted_data.pct_change().dropna()

        # Compute correlation matrix
        correlation_matrix = []
        for i in range(len(symbols)):
            line = []
            for j in range(len(symbols)):
                line.append(returns[symbols[i]].corr(returns[symbols[j]]))
            correlation_matrix.append(line)

        # Create graph
        graph = nx.Graph()

        # Add nodes
        for symbol in symbols:
            graph.add_node(symbol_names[symbol])

        # Add edges based on correlation strength
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):  # Avoid duplicates
                corr = correlation_matrix[i][j] * 2
                if abs(corr) > 0.5:  # Only add significant correlations
                    graph.add_edge(
                        symbol_names[symbols[i]],
                        symbol_names[symbols[j]],
                        weight=abs(corr),
                        sign="positive" if corr > 0 else "negative"
                    )

        # Separate positive and negative edges
        positive_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['sign'] == "positive"]
        negative_edges = [(u, v) for u, v, d in graph.edges(data=True) if d['sign'] == "negative"]

        # Draw the graph
        plt.figure(figsize=(12, 12))
        pos = nx.spring_layout(graph, seed=42)
        edges = graph.edges(data=True)

        # Draw nodes
        nx.draw_networkx_nodes(graph, pos, node_size=2000, node_color="#cfcfcf")

        # Draw positive edges (green)
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=positive_edges,
            width=[graph[u][v]['weight'] * 5 for u, v in positive_edges],
            edge_color="green"
        )

        # Draw negative edges (red)
        nx.draw_networkx_edges(
            graph, pos,
            edgelist=negative_edges,
            width=[graph[u][v]['weight'] * 5 for u, v in negative_edges],
            edge_color="red"
        )

        # Draw labels
        nx.draw_networkx_labels(graph, pos, font_size=8, font_color="black")

        plt.title("Correlation Network Between Symbols", fontsize=16)
        plt.axis('off')
        plt.show()

    finally:
        conn.close()
