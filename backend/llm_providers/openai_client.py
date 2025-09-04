import os
import requests

class OpenAIClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_response(self, message: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",   # You can switch to gpt-3.5-turbo if needed
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)

            # Handle common errors gracefully
            if response.status_code == 429:
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            elif response.status_code == 401:
                return "❌ Invalid or expired OpenAI API key."
            elif response.status_code >= 500:
                return "🚨 OpenAI server is having issues. Try again later."

            response.raise_for_status()  # Raise error for other issues

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            return f"❌ Request failed: {str(e)}"
