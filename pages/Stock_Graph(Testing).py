import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time


# Load tickers and company names from CSV
def load_tickers_from_csv(file_path):
    df = pd.read_csv(file_path, encoding='utf-8')
    df['Ticker'] = df['Ticker'].str.strip()
    df['Company'] = df['Company'].str.strip()
    return df


# Function to fetch stock data
def fetch_stock_data(ticker, interval):
    try:
        data = yf.download(ticker, period="1d", interval=interval)
        return data
    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
        return pd.DataFrame()


# Function to calculate RSI
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


# Function to calculate MACD
def calculate_macd(data):
    short_window = 12
    long_window = 26
    signal_window = 9
    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()
    return macd, signal


# Plot stock data with indicators
def plot_stock_data(data, indicator=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))

    if indicator == 'RSI':
        data['RSI'] = calculate_rsi(data)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis='y2'))
        fig.update_layout(
            title='Stock Price with RSI',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            yaxis2=dict(overlaying='y', side='right', title='RSI'),
        )
    elif indicator == 'MACD':
        macd, signal = calculate_macd(data)
        fig.add_trace(go.Scatter(x=data.index, y=macd, mode='lines', name='MACD'))
        fig.add_trace(go.Scatter(x=data.index, y=signal, mode='lines', name='Signal Line'))
        fig.update_layout(title='Stock Price with MACD', xaxis_title='Time', yaxis_title='Price (USD)')

    return fig


# Real-time stock graph page
def real_time_stock_graph(tickers_df):
    st.title("Real-Time Stock Price Chart")

    # Sidebar selections
    ticker_input = st.sidebar.text_input("Enter Stock Ticker or Company Name", value="AAPL")
    query = ticker_input.lower()
    filtered_tickers = tickers_df[tickers_df['Ticker'].str.lower().str.contains(query) |
                                  tickers_df['Company'].str.lower().str.contains(query)]

    if not filtered_tickers.empty:
        selected_ticker = st.sidebar.selectbox("Select Ticker", filtered_tickers['Ticker'])
    else:
        st.sidebar.warning("No matching tickers found.")
        return

    interval = st.sidebar.selectbox("Select Interval", ["1m", "5m", "30m", "60m", "1d", "5d", "1wk", "1mo"], index=0)
    indicator = st.sidebar.selectbox("Select Indicator", ["None", "RSI", "MACD"], index=0)

    # Button for real-time chart
    start_chart = st.sidebar.button("Start Real-Time Chart")
    stop_chart = st.sidebar.button("Stop Real-Time Chart")

    # Manage chart state with session state
    if "running" not in st.session_state:
        st.session_state.running = False

    if start_chart:
        st.session_state.running = True

    if stop_chart:
        st.session_state.running = False

    chart_placeholder = st.empty()

    while st.session_state.running:
        data = fetch_stock_data(selected_ticker, interval)
        if data.empty:
            st.warning("No data found. Please check the ticker or interval.")
            break

        fig = plot_stock_data(data, indicator if indicator != 'None' else None)
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(60)


# App entry point
def app():
    tickers_df = load_tickers_from_csv('tickers.csv')  # Replace with your file path
    real_time_stock_graph(tickers_df)


if __name__ == "__main__":
    app()
