import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

# Load tickers and company names from CSV
def load_tickers_from_csv(file_path):
    df = pd.read_csv(file_path,encoding='utf-8')
    # Ensure the ticker column is properly formatted and remove any leading/trailing spaces
    df['Ticker'] = df['Ticker'].str.strip()
    df['Company'] = df['Company'].str.strip()
    return df

# Function to fetch stock data
def fetch_stock_data(ticker, interval):
    # Fetch stock data using yfinance
    data = yf.download(ticker, period="1d", interval=interval)  # 1-minute interval for real-time data
    return data

# Function to calculate the Relative Strength Index (RSI)
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Function to calculate the Moving Average Convergence Divergence (MACD)
def calculate_macd(data):
    short_window = 12
    long_window = 26
    signal_window = 9

    short_ema = data['Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Close'].ewm(span=long_window, adjust=False).mean()

    macd = short_ema - long_ema
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    return macd, signal

# Function to plot stock data with selected indicators
def plot_stock_data(data, indicator=None):
    # Create a plotly figure with a line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))

    # Add selected indicator
    if indicator == 'RSI':
        data['RSI'] = calculate_rsi(data)
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis='y2'))
        fig.update_layout(
            title='Stock Price with RSI',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
            yaxis2=dict(
                overlaying='y',
                side='right',
                title='RSI'
            )
        )
    elif indicator == 'MACD':
        macd, signal = calculate_macd(data)
        fig.add_trace(go.Scatter(x=data.index, y=macd, mode='lines', name='MACD'))
        fig.add_trace(go.Scatter(x=data.index, y=signal, mode='lines', name='Signal Line'))
        fig.update_layout(
            title='Stock Price with MACD',
            xaxis_title='Time',
            yaxis_title='Price (USD)',
        )

    st.plotly_chart(fig)

# Function for the real-time stock graph page
def real_time_stock_graph(tickers_df):
    st.title("Real-time Stock Price Chart")

    # Sidebar selections for ticker, interval, and indicator
    ticker_input = st.sidebar.text_input("Enter Stock Ticker or Company Name", value="AAPL")  # Default is Apple stock

    # Filter tickers based on input (case insensitive)
    query = ticker_input.lower()
    filtered_tickers = tickers_df[tickers_df['Ticker'].str.lower().str.contains(query) | tickers_df['Company'].str.lower().str.contains(query)]

    # Display the filtered tickers in the selectbox
    if not filtered_tickers.empty:
        selected_ticker = st.sidebar.selectbox("Select Ticker", filtered_tickers['Ticker'])
    else:
        selected_ticker = st.sidebar.selectbox("Select Ticker", ["No matches found"])

    # If no ticker selected, return
    if selected_ticker == "No matches found":
        st.sidebar.warning("No matching tickers or company names found.")
        return

    interval = st.sidebar.selectbox("Select Interval", ["1m", "5m", "30m", "60m", "1d", "5d", "1wk", "1mo"], index=0)
    indicator = st.sidebar.selectbox("Select Indicator", ["None", "RSI", "MACD"], index=0)

    # Button to start the real-time graph
    if st.sidebar.button("Start Real-Time Chart"):
        st.write(f"Displaying real-time data for: {selected_ticker} with interval: {interval} and indicator: {indicator}")

        # Loop to update the graph every minute
        while True:
            # Fetch stock data
            data = fetch_stock_data(selected_ticker, interval)
            
            # Plot the data using Plotly and the selected indicator
            plot_stock_data(data, indicator='None' if indicator == 'None' else indicator)
            
            # Sleep for a minute before fetching new data
            time.sleep(60)  # Fetch new data every minute

# Set up the sidebar for navigation
def app():
    # Load tickers and companies from CSV file
    tickers_df = load_tickers_from_csv('tickers.csv')  # Provide the correct file path here
    
    real_time_stock_graph(tickers_df)

if __name__ == "__main__":
    app()
