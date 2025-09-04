import requests
import traceback
import os

class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("❌ Gemini API key missing. Set GEMINI_API_KEY in .env")
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_response(self, message: str, images: list = None) -> str:
        """
        Send a request to Gemini via OpenRouter API.
        `message` is user text, `images` is optional list of image URLs.
        """
        try:
            # Build message content
            content = [{"type": "text", "text": message}]
            if images:
                for img_url in images:
                    content.append({"type": "image_url", "image_url": {"url": img_url}})

            payload = {
                "model": "google/gemini-2.5-flash-image-preview:free",
                "messages": [{"role": "user", "content": content}],
                "temperature": 0.7  # optional, control creativity
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 401:
                return "❌ Unauthorized: Invalid Gemini API key."
            elif response.status_code == 429:
                return "⚠️ Rate limit exceeded. Try again later."
            elif response.status_code >= 500:
                return f"🔥 Gemini server error ({response.status_code})."
            elif response.status_code != 200:
                return f"❌ Gemini API error {response.status_code}: {response.text}"

            data = response.json()
            # Extract the assistant's reply safely
            try:
                return data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError):
                return "⚠️ Unexpected response format from Gemini."

        except requests.exceptions.RequestException as e:
            traceback.print_exc()
            return f"❌ Request failed: {str(e)}"
        except Exception as e:
            traceback.print_exc()
            return f"❌ Unexpected error: {str(e)}"
