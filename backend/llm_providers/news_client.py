# news_client.py
import requests
import os

# Load your News API key from environment
NEWS_API_KEY = os.environ.get("NEWS_API_KEY") or os.environ.get("NEWSAPI_KEY")

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
            "pageSize": max(1, min(100, int(limit or 5))),
        }
        if category:
            params["category"] = category

        try:
            if not self.api_key:
                return [], "Missing NEWS_API_KEY. Set it in backend/.env and restart."

            response = requests.get(self.base_url, params=params, timeout=10)
            if response.status_code != 200:
                try:
                    body = response.json()
                except Exception:
                    body = {"raw": response.text}
                return [], f"HTTP {response.status_code}: {body}"

            data = response.json()
            status = data.get("status")
            if status != "ok":
                return [], f"API status: {status} details: {data}"

            articles = data.get("articles", [])
            return articles[:limit], None
        except requests.exceptions.RequestException as e:
            return [], f"Request error: {e}"

# Example usage
if __name__ == "__main__":
    client = NewsClient()
    news = client.get_latest_news(country="in", category="technology")
    for idx, article in enumerate(news, 1):
        print(f"{idx}. {article['title']} ({article['source']['name']})")
