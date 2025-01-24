import streamlit as st
import requests
import datetime

# Streamlit app
st.title("Company Quarterly News Fetcher")

# Input for the company name
company_name = st.text_input("Enter the company name:", "")


NEWS_API_KEY = st.secrets.get("News", {}).get("NEWS_API_KEY", "no api key found")
if NEWS_API_KEY == "no api key found":
    st.error("API key not found. Please set it in your secrets.")

NEWS_API_URL = "https://newsapi.org/v2/everything"

# Helper function to fetch news
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

# Calculate dates for the last quarter
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=5)

# Fetch news when the user clicks the button
if st.button("Fetch Latest Quarterly News"):
    if company_name:
        st.write(f"Fetching news for: {company_name}")
        news_data = fetch_news(company_name, start_date, end_date)

        if news_data and "articles" in news_data:
            articles = news_data["articles"]
            if articles:
                st.success(f"Found {len(articles)} articles:")
                for article in articles:
                    st.markdown(f"### [{article['title']}]({article['url']})")
                    st.write(f"Source: {article['source']['name']}")
                    st.write(f"Published At: {article['publishedAt']}")
                    st.write(f"Description: {article['description']}")
                    st.write("---")
            else:
                st.warning("No articles found for the specified company.")
        else:
            st.error("No data received from the API.")
    else:
        st.warning("Please enter a company name to search for news.")

# Footer
