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
    ticker = st.sidebar.text_input("Enter Stock Ticker", value="^NSEI")

    # Stock data interval
    interval = "1d"

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

    # Function to handle LLM response gracefully
    def handle_llm_response(response):
        try:
            # Check if the response contains technical details or structured information
            if "analysis" in response.lower() or "predictions" in response.lower():
                return response
            else:
                # If it's a generic response, provide a more helpful fallback
                return "The response does not seem structured enough. Please try again with a more detailed analysis."
        except Exception as e:
            return f"An error occurred while processing the response: {str(e)}"

    # Fetch news and stock data when button is clicked
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

                    # Limit data to the last 100 rows
                    data = data.tail(100)

                    # Fetch API key for the LLM
                    groq_api_key = st.secrets.get("API_KEYS", {}).get("GROQ_API_KEY", "no api key found")
                    if groq_api_key == "no api key found":
                        st.error("GROQ API key not found. Please set it in your secrets.")
                        return

                    # Initialize ChatGroq LLM
                    llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

                    # Create a pandas dataframe agent
                    pandas_df_agent = create_pandas_dataframe_agent(
                        llm,
                        data,
                        verbose=True,
                        handle_parsing_errors=True,
                        allow_dangerous_code=True,
                    )

                    # Refined prompt to guide the analysis
                    stock_analysis_prompt = f"""
                    You are a stock analysis expert. Given the stock data (such as Open, High, Low, Close, Volume), perform a detailed technical analysis. 
                    Analyze the trends, predict future movements, and incorporate insights from this news: {latest_article['description']}. 
                    Provide a structured response with specific analysis on potential trends, including whether the stock is oversold or overbought, any breakout signals, 
                    and predictions based on the data you have.
                    """

                    # Add progress bar during processing
                    with st.spinner("Generating stock analysis..."):
                        progress_bar = st.progress(0)
                        try:
                            # Simulate a progress update
                            response = pandas_df_agent.run(stock_analysis_prompt)
                            for i in range(100):
                                progress_bar.progress(i + 1)

                            # Handle and validate the response
                            parsed_response = handle_llm_response(response)

                            # Display assistant response
                            st.markdown("## Stock Analysis Insights")
                            st.write(parsed_response)

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
