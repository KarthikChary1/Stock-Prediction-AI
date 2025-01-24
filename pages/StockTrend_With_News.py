import streamlit as st
import requests
import datetime
import yfinance as yf
from langchain_groq import ChatGroq
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.messages import HumanMessage, AIMessage

# Streamlit app
def main():
    st.title("Company News and Stock Analysis")

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # Input for company name and stock ticker
    company_name = st.sidebar.text_input("Enter the company name:", "")
    ticker = st.sidebar.text_input("Enter Stock Ticker")

    # Stock data interval
    interval = "1d"
    # columns = ["Low", "Open", "High", "All", "Close", "Adj Close", "Volume"]
    # selected_column = st.sidebar.selectbox("Select Column to Forecast", options=columns, index=3)  # Default: "Close"

    # NewsAPI configuration
    NEWS_API_KEY = st.secrets.get("News", {}).get("NEWS_API_KEY", "no api key found")
    if NEWS_API_KEY == "no api key found":
        st.error("News API key not found. Please set it in your secrets.")
        return

    NEWS_API_URL = "https://newsapi.org/v2/everything"

    # Fetch latest news
    def fetch_news(company, from_date, to_date):
        params = {
            "q": company,
            "from": from_date,
            "to": to_date,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": NEWS_API_KEY,
        }
        response = requests.get(NEWS_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch news: {response.status_code} - {response.text}")
            return None

    # Calculate dates for the last week
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)

    # Fetch news when the user clicks the button
    if st.button("Fetch Latest News and Analyze"):
        if company_name:
            st.write(f"Fetching news for: {company_name}")
            news_data = fetch_news(company_name, start_date, end_date)

            if news_data and "articles" in news_data:
                articles = news_data["articles"]
                if articles:
                    latest_article = articles[0]  # Only the latest article
                    st.success("Latest Article Found:")
                    st.markdown(f"### [{latest_article['title']}]({latest_article['url']})")
                    st.write(f"Source: {latest_article['source']['name']}")
                    st.write(f"Published At: {latest_article['publishedAt']}")
                    st.write(f"Description: {latest_article['description']}")
                    st.write("---")

                    # Download stock data
                    data = yf.download(ticker, interval=interval)
                    if data.empty:
                        st.error("No stock data found. Please check the ticker or interval.")
                        return
                    data.reset_index(inplace=True)

                    # Filter selected column or display all columns for the last 100 rows
                    
                    data = data.tail(100)
                    # st.write(f"Displaying data for {ticker} with interval {interval}")
                    # st.write(data)
                    

                    # Fetch API key for the LLM
                    groq_api_key = st.secrets.get("API_KEYS", {}).get("GROQ_API_KEY", "no api key found")
                    if groq_api_key == "no api key found":
                        st.error("GROQ API key not found. Please set it in your secrets.")
                        return

                    # Initialize ChatGroq LLM
                    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.2-90b-vision-preview")

                    # Create a pandas dataframe agent
                    pandas_df_agent = create_pandas_dataframe_agent(
                        llm,
                        data,
                        verbose=True,
                        handle_parsing_errors=True,
                        allow_dangerous_code=True,
                    )

                    # Define a prompt for stock analysis
                    stock_analysis_prompt = f"""
                    You are a friendly stock analysis expert. Given the stock data (such as Open, High, Low, Close, Volume),
                    perform technical analysis and trends. Incorporate the news: "{latest_article['description']}".
                    Provide insights and predictions based on the data in a structured format.
                    """

                    try:
                        # Generate response using the pandas_df_agent
                        response = pandas_df_agent.run(stock_analysis_prompt)

                        # Display assistant response
                        st.markdown("## Stock Analysis Insights")
                        st.write(response)

                    except Exception as e:
                        st.error(f"Error generating response: {str(e)}")
                else:
                    st.warning("No articles found for the specified company.")
            else:
                st.error("No data received from the News API.")
        else:
            st.warning("Please enter a company name to search for news.")

if __name__ == "__main__":
    main()
