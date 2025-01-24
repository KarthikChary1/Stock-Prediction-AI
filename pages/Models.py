import yfinance as yf
import streamlit as st
from prophet_method import prophet_func
from LSTM import LSTM_func

st.sidebar.header("Configuration")

ticker = st.sidebar.text_input("Enter Stock Ticker", value="^NSEI")
interval = st.sidebar.selectbox("Select Interval", options=["1m", "5m", "30m", "60m", "1d", "5d"], index=0)
forecast_method = st.sidebar.selectbox("Select Forecast Method", ["Prophet", "LSTM"], index=0)
periods = st.sidebar.number_input("Future Prediction Periods (Prophet)", min_value=1, max_value=365, value=10)

# Column selection for prediction
columns = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
selected_column = st.sidebar.selectbox("Select Column to Forecast", options=columns, index=3)  # Default: "Close"

def get_stock_data(ticker, interval="1d"):
    """Fetch stock data from yfinance."""
    stock_data = yf.download(ticker, interval=interval)
    if stock_data.empty:
        st.error("No data retrieved. Check the ticker or internet connection.")
        return None
    stock_data.reset_index(inplace=True)
    return stock_data

data = get_stock_data(ticker, interval)

# Ensure that we clear session state and output if switching between forecast methods
if "forecast_output" in st.session_state:
    st.session_state.forecast_output = None  # Reset previous forecast output

if data is not None:
    st.write(f"Displaying data for {ticker} with interval {interval}")
    st.dataframe(data.tail())

    # Display method-specific forecast
    if forecast_method == "Prophet":
        if "forecast_output" not in st.session_state or st.session_state.forecast_output != "Prophet":
            # Clear any previous output (e.g., LSTM results) when switching to Prophet
            st.session_state.forecast_output = "Prophet"  # Set the output method
            prophet_func(data=data, selected_column=selected_column, interval=interval, periods=periods)

    elif forecast_method == "LSTM":
        if "forecast_output" not in st.session_state or st.session_state.forecast_output != "LSTM":
            # Clear any previous output (e.g., Prophet results) when switching to LSTM
            st.session_state.forecast_output = "LSTM"  # Set the output method
            # Call LSTM function
            LSTM_func(data=data, selected_column=selected_column, periods=periods)
else:
    st.error("Data preparation failed. Please check the inputs or try again.")
