import streamlit as st

# Set page configuration
st.set_page_config(
    page_title="Stock Price Prediction App",
    page_icon="📈",
    layout="wide",
)

# Main title
st.title("📊 Stock Price Prediction App")
st.markdown(
    """
Welcome to the **Stock Price Prediction App**! 

** TICKER ** : Search for the ticker in Yahoo Finance

This app provides powerful tools for stock market forecasting and insights, tailored for traders, analysts, and enthusiasts.

---

### Choose the Right Tool for Your Needs:
🔮 **Prophet and LSTM Models**:
- Select this option if:
  - You want to **train a new model** on the stock data.
  - You want to use **pre-trained models** for time series forecasting and predictions.
- Methods available:
  - **Prophet**: Time series forecasting with seasonality and trend analysis.
  - **LSTM**: Deep learning-based predictions for sequential data.

🤖 **LLM Insights (Ollama)**:
- Select this option if:
  - You want to **chat with an AI** about stock market analysis.
  - You need detailed insights or assistance on stock-related queries.
- Powered by advanced **Language Learning Models (LLMs)**.

---

Use the sidebar on the left to navigate between pages.
"""
)

# Add a call-to-action section with buttons
st.markdown("## 🚀 Get Started")

col1, col2 , col3 = st.columns(3)

with col1:
    if st.button("Prophet and LSTM Models"):
        st.page_link(page="pages\Models.py",label="Click Here to Start")

with col2:
    if st.button("Chat with AI (LLM Insights)"):
        st.page_link(page="pages/Ollama.py",label="Click Here to Start")

with col3:
    if st.button("Realtime Stock Graph"):
        st.page_link(page="pages/Stock_Graph.py",label="Click Here to Start")        

# Footer
st.markdown(
    """
---
✨ Developed to simplify your stock analysis journey. Whether you're a beginner or a seasoned trader, this app is for you!
"""
)

 


 # Navigate to StockPrediction.py
