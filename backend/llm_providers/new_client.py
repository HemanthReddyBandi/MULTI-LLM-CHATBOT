# news_client.py
import requests
import os

# Load your News API key from environment or hardcode temporarily
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_API_KEY_HERE")

class NewsClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def get_latest_news(self, country="in", category=None, limit=5):
        """
        Fetch latest news articles.
        :param country: 'in' for India, 'us' for USA, etc.
        :param category: Optional category like 'technology', 'sports', 'business'
        :param limit: Number of articles to return
        :return: List of news articles (dicts)
        """
        params = {
            "country": country,
            "apiKey": self.api_key,
        }
        if category:
            params["category"] = category

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            return articles[:limit]
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return []

# Example usage
if __name__ == "__main__":
    client = NewsClient()
    news = client.get_latest_news(country="in", category="technology")
    for idx, article in enumerate(news, 1):
        print(f"{idx}. {article['title']} ({article['source']['name']})")
