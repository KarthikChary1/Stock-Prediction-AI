# Prophet Forecast
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from prophet import Prophet

def prophet_func(data,selected_column, interval="1d", periods=10):
    st.subheader("Prophet Forecast")
    data.columns = [i[0] for i in data.columns]
    data.rename(columns={"Datetime": "ds", "Date": "ds", selected_column: "y"}, inplace=True)
    data['ds'] = pd.to_datetime(data['ds']).dt.strftime('%Y-%m-%d %H:%M:%S')
    model = Prophet(daily_seasonality=True)
    model.fit(data[['ds', 'y']])
    if interval == "1m":
        interval = "1min"
    elif interval == "5m":
        interval = "5min"
    elif interval == "30m":
        interval = "30min"
    elif interval == "60m":
        interval = "60min"   


    future = model.make_future_dataframe(periods=periods, freq=interval)
    forecast = model.predict(future)
    st.write("Forecast Data")
    st.dataframe(forecast.tail())
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(forecast['ds'], forecast['yhat'], label='Forecast')
    plt.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='blue', alpha=0.2)
    plt.xlabel('Date')
    plt.ylabel(f'Predicted {selected_column} Price')
    plt.title(f'Prophet Future Predictions for {selected_column}')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)
    # Filter to only future dates
    future_dates = future[future['ds'] > data['ds'].max()]
    forecast_only_future = forecast[forecast['ds'].isin(future_dates['ds'])]

    # Custom plot for future predictions only
    plt.figure(figsize=(10, 6))
    plt.plot(forecast_only_future['ds'], forecast_only_future['yhat'], label='Predicted')
    plt.fill_between(forecast_only_future['ds'], forecast_only_future['yhat_lower'], forecast_only_future['yhat_upper'], color='blue', alpha=0.2)
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    plt.ylabel(f'Predicted {selected_column} Price')
    plt.title(f'Future Predictions for {selected_column}')
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)