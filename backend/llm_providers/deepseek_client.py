import requests
import traceback

class DeepSeekClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("❌ DeepSeek API key is missing.")
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_response(self, message: str, history=None):
        """Send chat request with limited history to DeepSeek / OpenRouter"""
        if history is None:
            history = []

        # Add the current user message
        history.append({"role": "user", "content": message})

        # Limit history to last 4 messages (API safe)
        payload_history = history[-4:]

        payload = {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": payload_history,
            "temperature": 0.7
        }

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 401:
                return "❌ Unauthorized: Invalid API key.", history
            elif response.status_code != 200:
                return f"❌ Error {response.status_code}: {response.text}", history

            data = response.json()
            assistant_reply = data["choices"][0]["message"]["content"].strip()

            # Add assistant reply to history
            history.append({"role": "assistant", "content": assistant_reply})

            return assistant_reply, history

        except Exception as e:
            traceback.print_exc()
            return f"❌ Unexpected error: {str(e)}", history
