import requests
import traceback
import os
import json

class GeminiClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("❌ Gemini API key missing. Set GEMINI_API_KEY in .env")
        self.api_key = api_key
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        # Allow overriding the model from env, default to a stable supported model
        self.model = os.getenv("GEMINI_MODEL", "google/gemini-2.0-flash-001")

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
                    # OpenRouter multimodal content accepts image_url entries
                    content.append({"type": "image_url", "image_url": {"url": img_url}})

            system_prompt = os.getenv(
                "GEMINI_SYSTEM_PROMPT",
                (
                    "You are a helpful assistant. If the user provides an image, describe it in clear, "
                    "natural English sentences suitable for a general audience. Do not return JSON, "
                    "code blocks, or bounding boxes. Avoid technical detection outputs."
                ),
            )

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                    {"role": "user", "content": content},
                ],
                "temperature": 0.7,
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
                # Provide a helpful hint when the model isn't available
                if response.status_code == 404 and "No endpoints found" in response.text:
                    return (
                        "❌ Gemini model not available on OpenRouter. Set GEMINI_MODEL to a supported "
                        "model (e.g., 'google/gemini-2.0-flash-001' or a ':free' variant) and restart."
                    )
                return f"❌ Gemini API error {response.status_code}: {response.text}"

            data = response.json()
            # Extract the assistant's reply safely
            try:
                raw = data["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError):
                return "⚠️ Unexpected response format from Gemini."

            # Heuristic: if model returns code fences or JSON-like results, convert to plain English
            text = raw
            if text.startswith("```") and text.endswith("```"):
                # strip code fences
                text = text.strip("`")
                # if it had a language tag like ```json\n...```
                if "\n" in text:
                    text = text.split("\n", 1)[1]
            text = text.strip()

            # Try to interpret common detection JSON [{label:..}] into a sentence
            try:
                parsed = json.loads(text)
                if isinstance(parsed, list):
                    labels = []
                    for item in parsed:
                        if isinstance(item, dict) and "label" in item:
                            labels.append(str(item["label"]))
                    if labels:
                        uniq = []
                        for l in labels:
                            if l not in uniq:
                                uniq.append(l)
                        return "The image appears to contain: " + ", ".join(uniq) + "."
            except Exception:
                pass

            return text

        except requests.exceptions.RequestException as e:
            traceback.print_exc()
            return f"❌ Request failed: {str(e)}"
        except Exception as e:
            traceback.print_exc()
            return f"❌ Unexpected error: {str(e)}"
