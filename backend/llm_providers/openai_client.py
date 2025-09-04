# openai_client.py
import requests
import os
import json

class OpenAIClient:
    def __init__(self, api_key=None):
        # Use environment variable if api_key not passed
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("❌ OpenAI API key missing. Set OPENROUTER_API_KEY in your environment.")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_response(self, message: str) -> str:
        """
        Send a message to OpenRouter/OpenAI API and get the response.
        """
        try:
            payload = {
                "model": "openai/gpt-oss-120b:free",
                "messages": [{"role": "user", "content": message}]
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))
            if response.status_code != 200:
                return f"❌ API error {response.status_code}: {response.text}"

            data = response.json()
            # Access the first assistant message from choices
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            return f"❌ Request failed: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"

# Example usage:
# client = OpenAIClient()
# reply = client.generate_response("Hello, how are you?")
# print(reply)
