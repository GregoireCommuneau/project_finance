# streamlit_app.py
import streamlit as st
import pandas as pd
from db_utils import connect_to_postgres, validate_symbols_or_names, get_symbol_names
from data_utils import calculate_daily_returns, calculate_correlation_matrix, calculate_rolling_correlation
from plot_utils import plot_heatmap, plot_rolling_correlation

st.set_page_config(page_title="Stock Correlation Analyzer", layout="wide")
st.title("📊 Stock Correlation Analyzer")

# Connect to DB
conn = connect_to_postgres()

# Inputs
symbol_input = st.text_input("Enter stock symbols (comma-separated)", value="AAPL,MSFT,GOOGL")
symbol_list = [s.strip().upper() for s in symbol_input.split(",") if s.strip()]
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("2023-12-31"))
window_size = st.slider("Rolling Window (days)", min_value=5, max_value=120, value=30)

if st.button("Run Analysis") and symbol_list:
    symbols, missing = validate_symbols_or_names(conn, symbol_list)

    if missing:
        st.warning(f"Symbols not found in DB: {', '.join(missing)}")

    if symbols:
        # Load stock data from database
        query = """
            SELECT symbol, date, close
            FROM stock_data
            WHERE symbol IN %s AND date BETWEEN %s AND %s
            ORDER BY date;
        """
        with conn.cursor() as cursor:
            cursor.execute(query, (tuple(symbols), start_date, end_date))
            rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=["symbol", "date", "close"])
        df["date"] = pd.to_datetime(df["date"])
        pivoted = df.pivot(index="date", columns="symbol", values="close")

        # Daily returns and correlation
        returns = calculate_daily_returns(pivoted)
        correlation_df = calculate_correlation_matrix(returns, symbols)

        symbol_names = get_symbol_names(conn, symbols)
        correlation_df_named = correlation_df.rename(columns=symbol_names, index=symbol_names)

        st.subheader("Correlation Heatmap")
        st.pyplot(plot_heatmap(correlation_df_named, title="Correlation Matrix"))

        if len(symbols) >= 2:
            rolling = calculate_rolling_correlation(returns, symbols[0], symbols[1], window_size)
            st.subheader(f"Rolling Correlation: {symbols[0]} vs {symbols[1]}")
            st.pyplot(plot_rolling_correlation(rolling, symbols[0], symbols[1], window_size))

conn.close()
