import streamlit as st
import yfinance as yf
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, AIMessage
import pandas as pd

def ollama():

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # User input for ticker and interval
    ticker = st.sidebar.text_input("Enter Stock Ticker", value="^NSEI")
    interval = st.sidebar.selectbox(
        "Select Interval",
        options=["1m", "5m", "30m", "60m", "1d", "5d", "1wk", "1mo", "3mo"],
        index=0,
    )
    columns = ["Low", "Open", "High", "All", "Close", "Adj Close", "Volume"]
    selected_column = st.sidebar.selectbox("Select Column to Forecast", options=columns, index=3,)  # Default: "Close"
    period = st.sidebar.slider("Select Number of Days", min_value=1, max_value=300, value=7)
    # Download stock data
    data = yf.download(ticker, interval=interval)
    if data.empty:
        st.error("No data found. Please check the ticker or interval.")
        return
    data.reset_index(inplace=True)
    data.rename(columns={"Date": "Datetime"}, inplace=True)
    # Filter selected column or display all columns for the last 30 days
    if selected_column == "All":
        data = data.tail(period)
    else:
        data = data[["Datetime", selected_column]].tail(period)

    # Fetch API key for the LLM
    groq_api_key = st.secrets.get("API_KEYS", {}).get("GROQ_API_KEY", "no api key found")
    if groq_api_key == "no api key found":
        st.error("API key not found. Please set it in your secrets.")
        return

    # Initialize ChatGroq LLM
    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

    # Create a pandas dataframe agent
    pandas_df_agent = create_pandas_dataframe_agent(
        llm,
        data,
        verbose=True,
        handle_parsing_errors="Check your output and make sure it conforms!",
                        allow_dangerous_code=True,  agent_executor_kwargs={"handle_parsing_errors": True}
    )

    # Define a simpler prompt to instruct the LLM as a stock analyst
    stock_analysis_prompt = """
    You are a friendly stock analysis expert. Given the stock data provided (such as Open, High, Low, Close, Volume),
    you can perform technical analysis and trends. Please provide insights and predictions based on the data.
    """

    # Initialize session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User query input
    query = st.chat_input("Ask me anything about the stock data...")
    if query:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.write(query)

        # Simplified query and agent interaction
        full_query = f"{stock_analysis_prompt} Respond to the following query based on the data: {query}"

        try:
            # Generate response using the pandas_df_agent
            response = pandas_df_agent.run(full_query)

            # Add assistant response to session state and display it
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.chat_history.extend(
                [HumanMessage(query.strip()), AIMessage(content=response)]
            )

            # Display assistant response
            with st.chat_message("assistant"):
                st.write(response)

        except Exception as e:
            # Log the error and inputs that caused it
            st.error(f"Error generating response: {str(e)}")
            st.write(f"Inputs causing error: {full_query}")
            st.write(f"Data snapshot: {data.tail()}")

if __name__ == "__main__":
    ollama()
