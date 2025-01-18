
import pandas as pd
import numpy as np
import streamlit as st
from prophet_method import Prophet
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, Dense
import matplotlib.pyplot as plt
from tensorflow.keras.callbacks import Callback



def LSTM_func(data,selected_column,periods):
    st.empty()
    st.subheader("LSTM Forecast")
    data["MA20"] = data[selected_column].rolling(window=20).mean()
    data.dropna(inplace=True)
    scaler = MinMaxScaler()
    data["Scaled"] = scaler.fit_transform(data[selected_column].values.reshape(-1, 1))
    def window(data, window_size):
        X, y = [], []
        for i in range(len(data) - window_size):
            X.append(data[i:i + window_size])
            y.append(data[i + window_size])
        return np.array(X), np.array(y)
    window_size = 30
    X, y = window(data["Scaled"].values, window_size)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)
    # Initialize Streamlit progress bar
    progress_bar = st.progress(0)  # Create progress bar initially at 0%
    # Define a callback to update the progress bar during training
    class ProgressBarCallback(Callback):
        def on_epoch_end(self, epoch, logs=None):
            progress = (epoch + 1) / self.params['epochs']
            progress_bar.progress(progress)  # Update the progress bar
    model = Sequential()
    model.add(LSTM(units=120, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=120,return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=120))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer="adam", loss="mean_squared_error")
    # Add the custom callback to the fit method
    model.fit(X_train, y_train, epochs=10, batch_size=32, validation_data=(X_test, y_test),
              callbacks=[ProgressBarCallback()])
    # Future Predictions
    future_pred = X_test[-1].copy()  # Start from the last element of X_test
    future_preds = []
    # Loop for predicting future steps
    for _ in range(periods):
        # Predict the next step
        next_pred = model.predict(future_pred.reshape(1, window_size, 1))  # Ensure the shape is (1, window_size, 1)

        # Append the predicted value (next_pred is 2D, so extract the scalar value)
        future_preds.append(next_pred[-1, 0])  # Get the last predicted value
        # Update future_pred: shift and append the new prediction
        future_pred = np.roll(future_pred, -1)  # Shift all values left by 1
        future_pred[-1] = next_pred[-1, 0]  # Append the predicted value (scalar)
    # Inverse transform future predictions
    future_preds = scaler.inverse_transform(np.array(future_preds).reshape(-1, 1))
    st.write(future_preds)
    # Plot Future Predictions
    plt.figure(figsize=(8, 5))
    plt.plot(future_preds, marker="o", color="green", label=f"Future {selected_column} Predictions")
    plt.title(f"{periods}-Step Ahead Predictions for {selected_column}")
    plt.xlabel("Future Time Steps")
    plt.ylabel(f"{selected_column} Price")
    plt.legend()
    plt.grid(True)
    st.pyplot(plt)