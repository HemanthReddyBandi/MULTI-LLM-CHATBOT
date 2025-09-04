from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLM clients
from llm_providers.openai_client import OpenAIClient
from llm_providers.gemini_client import GeminiClient
from llm_providers.deepseek_client import DeepSeekClient

# Initialize FastAPI
app = FastAPI(title="Multi-LLM + Real-Time Chatbot API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    provider: str
    message: str
    images: Optional[List[str]] = []  # Optional image URLs for Gemini

class ChatResponse(BaseModel):
    response: str
    provider: str

# Initialize LLM clients
llm_clients = {
    "openai": OpenAIClient(api_key=os.getenv("OPENAI_API_KEY")),
    "gemini": GeminiClient(api_key=os.getenv("GEMINI_API_KEY")),
    "deepseek": DeepSeekClient(api_key=os.getenv("DEEPSEEK_API_KEY")),
}

# Real-time API keys
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# Store conversation history per session & provider
conversation_histories = {}  # { session_id: { provider: [messages] } }

# --- Helper Functions for Real-Time Data ---
def get_stock_price(symbol: str) -> str:
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_KEY}"
        r = requests.get(url).json()
        price = r["Global Quote"]["05. price"]
        return f"📈 {symbol} price: ${price}"
    except:
        return "⚠️ Unable to fetch stock price."

def get_weather(city: str) -> str:
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
        r = requests.get(url).json()
        temp = r["main"]["temp"]
        desc = r["weather"][0]["description"]
        return f"🌤️ Weather in {city}: {temp}°C, {desc}"
    except:
        return "⚠️ Unable to fetch weather."

def get_news() -> str:
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWSAPI_KEY}&pageSize=5"
        r = requests.get(url).json()
        articles = r.get("articles", [])
        headlines = "\n".join([f"• {a['title']}" for a in articles])
        return f"📰 Latest headlines:\n{headlines}"
    except:
        return "⚠️ Unable to fetch news."

# --- Routes ---
@app.get("/")
async def root():
    return {"message": "🚀 Multi-LLM + Real-Time Chatbot API is running!"}

@app.get("/providers")
async def get_providers():
    return {"providers": list(llm_clients.keys())}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, session_id: str = "default"):
    """
    Send a message to the LLM or real-time API based on content.
    Maintains session-based conversation history for context.
    """
    try:
        msg = request.message.lower()
        provider = request.provider

        # Initialize session history if not exists
        session_history = conversation_histories.get(session_id, {})
        history = session_history.get(provider, [])

        # # --- Check for real-time triggers ---
        # if "stock" in msg:
        #     symbol = msg.split()[-1].upper()
        #     response = get_stock_price(symbol)
        #     return ChatResponse(response=response, provider="realtime")

        # elif "weather" in msg:
        #     city = msg.split()[-1].capitalize()
        #     response = get_weather(city)
        #     return ChatResponse(response=response, provider="realtime")

        # elif "news" in msg:
        #     response = get_news()
        #     return ChatResponse(response=response, provider="realtime")

        # --- Call LLM for normal conversation ---
        if provider not in llm_clients:
            raise HTTPException(status_code=400, detail=f"❌ Provider '{provider}' not supported.")

        client = llm_clients[provider]

        # Gemini with optional images
        if provider == "gemini":
            response = client.generate_response(request.message, images=request.images)

        # DeepSeek with history
        elif provider == "deepseek":
            response, history = client.generate_response(request.message, history)

        # OpenAI or other LLMs
        else:
            response = client.generate_response(request.message)

        # Save updated history
        session_history[provider] = history
        conversation_histories[session_id] = session_history

        return ChatResponse(response=response, provider=provider)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")
