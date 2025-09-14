from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
import traceback
from dotenv import load_dotenv
import feedparser

# Load environment variables from backend/.env regardless of current working dir
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Import LLM clients
from .llm_providers.openai_client import OpenAIClient
from .llm_providers.gemini_client import GeminiClient
from .llm_providers.deepseek_client import DeepSeekClient
from .llm_providers.news_client import NewsClient
from .llm_providers.weather_client import WeatherClient

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

# Auth includes (renamed to avoid conflicts)
from auth_module.router import router as auth_router
from auth_module.database import engine
from auth_module.models import Base

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
    "news": NewsClient(api_key=os.getenv("NEWS_API_KEY") or os.getenv("NEWSAPI_KEY")),
    "weather": WeatherClient(api_key=os.getenv("OPENWEATHER_KEY") or os.getenv("OPENWEATHER_API_KEY")),
}

# Real-time API keys
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")
OPENWEATHER_KEY = os.getenv("OPENWEATHER_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY") or os.getenv("NEWSAPI_KEY")

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

# Include auth routes
app.include_router(auth_router, prefix="", tags=["auth"])

@app.on_event("startup")
async def on_startup():
    if Base and engine:
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            pass

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

        # --- Call LLM or News based on provider ---
        if provider not in llm_clients:
            raise HTTPException(status_code=400, detail=f"❌ Provider '{provider}' not supported.")

        client = llm_clients[provider]

        # News provider: fetch headlines
        if provider == "news":
            # parse simple hints from message (e.g., "technology in us")
            country = "in"
            category = None
            tokens = request.message.lower().split()
            for tok in tokens:
                if tok in ["us","in","gb","au","ca","de","fr","it","es","jp"]:
                    country = tok
            for cat in ["business","entertainment","general","health","science","sports","technology"]:
                if cat in tokens:
                    category = cat
            articles, err = client.get_latest_news(country=country, category=category, limit=5)
            if err:
                return ChatResponse(response=f"⚠️ News API error: {err}", provider="news")
            if not articles:
                return ChatResponse(response="⚠️ No news found.", provider="news")
            headlines = "\n".join([f"• {a.get('title','Untitled')} ({(a.get('source') or {}).get('name','')})" for a in articles])
            return ChatResponse(response=f"📰 Top headlines{f' in {country.upper()}' if country else ''}{f' - {category}' if category else ''}:\n{headlines}", provider="news")

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

# --- Dedicated News endpoints ---
@app.get("/news/global")
async def news_global():
    if not NEWS_API_KEY:
        raise HTTPException(status_code=400, detail="Missing NEWS_API_KEY in environment")
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {"status": r.status_code, "error": r.text}
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/in")
async def news_india():
    if not NEWS_API_KEY:
        raise HTTPException(status_code=400, detail="Missing NEWS_API_KEY in environment")
    url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {"status": r.status_code, "error": r.text}
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/sources")
async def news_sources():
    if not NEWS_API_KEY:
        raise HTTPException(status_code=400, detail="Missing NEWS_API_KEY in environment")
    url = f"https://newsapi.org/v2/top-headlines/sources?language=en&apiKey={NEWS_API_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return {"status": r.status_code, "error": r.text}
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/combined")
async def news_combined(country: str = "in", category: str | None = None, q: str | None = None):
    if not NEWS_API_KEY:
        raise HTTPException(status_code=400, detail="Missing NEWS_API_KEY in environment")
    base = f"https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}"
    if country:
        base += f"&country={country}"
    if category:
        base += f"&category={category}"
    if q:
        base += f"&q={q}"
    headlines_url = base
    sources_url = f"https://newsapi.org/v2/top-headlines/sources?language=en&apiKey={NEWS_API_KEY}"
    try:
        h = requests.get(headlines_url, timeout=10)
        s = requests.get(sources_url, timeout=10)
        return {
            "headlines": h.json() if h.status_code == 200 else {"status": h.status_code, "error": h.text},
            "sources": s.json() if s.status_code == 200 else {"status": s.status_code, "error": s.text}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/stocks")
async def news_stocks(feed_url: str | None = None, limit: int = 20):
    """
    Fetch stock/market news from RSS (Moneycontrol by default).
    Override feed_url to point to a specific stock/market feed if desired.
    """
    default_feed = os.getenv("NEWS_STOCK_RSS", "https://www.moneycontrol.com/rss/latestnews.xml")
    url = feed_url or default_feed
    try:
        parsed = feedparser.parse(url)
        items = []
        for entry in parsed.entries[: max(1, min(50, limit))]:
            items.append({
                "title": entry.get("title"),
                "link": entry.get("link"),
                "published": entry.get("published") or entry.get("updated"),
                "summary": entry.get("summary"),
            })
        return {"feed": parsed.feed.get("title", "stocks"), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Weather endpoints ---
@app.get("/weather/current")
async def weather_current(city: str, units: str = "metric"):
    wc = llm_clients.get("weather")
    data, err = wc.current(city=city, units=units)
    if err:
        # Fallback to text response for clearer client message
        return {"detail": wc.current_text(city=city, units=units)}
    return data

@app.get("/weather/forecast")
async def weather_forecast(city: str, units: str = "metric"):
    wc = llm_clients.get("weather")
    data, err = wc.forecast(city=city, units=units)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return data

@app.get("/weather/combined")
async def weather_combined(city: str, units: str = "metric"):
    wc = llm_clients.get("weather")
    cur, e1 = wc.current(city=city, units=units)
    fc, e2 = wc.forecast(city=city, units=units)
    return {"current": cur or {"detail": e1}, "forecast": fc or {"detail": e2}}
 