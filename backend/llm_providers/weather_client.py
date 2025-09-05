import os
import requests

# Load from env, fallback to provided key (user-supplied)
OPENWEATHER_KEY = (
    os.getenv("OPENWEATHER_KEY")
    or os.getenv("OPENWEATHER_API_KEY")
    or "87d6b8aea467fc8873d2d9403e6ee469"
)

class WeatherClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or OPENWEATHER_KEY
        self.base = "https://api.openweathermap.org/data/2.5"
        self.geo_base = "https://api.openweathermap.org/geo/1.0"
        self._cache = {"geocode": {}, "current": {}, "forecast": {}}

    def geocode(self, query: str):
        """Resolve a city name (optionally with country code, e.g., 'Delhi,IN') to lat/lon."""
        if not self.api_key:
            return None, "Missing OPENWEATHER_KEY in environment"
        # Normalize common aliases
        aliases = {
            "pachikapallam": "Pachikapallam,IN",
        }
        qnorm = aliases.get(query.strip().lower(), query.strip())
        if qnorm in self._cache["geocode"]:
            return self._cache["geocode"][qnorm], None
        try:
            r = requests.get(
                f"{self.geo_base}/direct",
                params={"q": qnorm, "limit": 5, "appid": self.api_key},
                timeout=10,
            )
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text}"
            arr = r.json() or []
            if not arr:
                return None, f"Could not find location '{qnorm}'. Try 'City,CountryCode' (e.g., 'Delhi,IN')."
            # Prefer exact case-insensitive name match if available
            item = next((x for x in arr if str(x.get("name", "")).lower() == qnorm.split(",")[0].lower()), arr[0])
            name = item.get("name")
            country = item.get("country")
            state = item.get("state")
            display = ", ".join([p for p in [name, state, country] if p])
            loc = {"lat": item.get("lat"), "lon": item.get("lon"), "display": display}
            self._cache["geocode"][qnorm] = loc
            return loc, None
        except Exception as e:
            return None, str(e)

    def current(self, city: str, units: str = "metric"):
        if not self.api_key:
            return None, "Missing OPENWEATHER_KEY in environment"
        # Prefer geocoding for better accuracy
        loc, err = self.geocode(city)
        if err:
            return None, err
        key = f"{loc['lat']},{loc['lon']}:{units}"
        if key in self._cache["current"]:
            data = self._cache["current"][key]
            data["resolved_name"] = loc["display"]
            return data, None
        try:
            r = requests.get(
                f"{self.base}/weather",
                params={"lat": loc["lat"], "lon": loc["lon"], "appid": self.api_key, "units": units},
                timeout=10,
            )
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text}"
            data = r.json()
            # include resolved display name
            data["resolved_name"] = loc["display"]
            self._cache["current"][key] = data
            return data, None
        except Exception as e:
            return None, str(e)

    def forecast(self, city: str, units: str = "metric"):
        if not self.api_key:
            return None, "Missing OPENWEATHER_KEY in environment"
        loc, err = self.geocode(city)
        if err:
            return None, err
        key = f"{loc['lat']},{loc['lon']}:{units}"
        if key in self._cache["forecast"]:
            data = self._cache["forecast"][key]
            data["resolved_name"] = loc["display"]
            return data, None
        try:
            r = requests.get(
                f"{self.base}/forecast",
                params={"lat": loc["lat"], "lon": loc["lon"], "appid": self.api_key, "units": units},
                timeout=10,
            )
            if r.status_code != 200:
                return None, f"HTTP {r.status_code}: {r.text}"
            data = r.json()
            data["resolved_name"] = loc["display"]
            self._cache["forecast"][key] = data
            return data, None
        except Exception as e:
            return None, str(e)

    def current_text(self, city: str, units: str = "metric"):
        """Return a concise human-readable weather string."""
        try:
            loc, err = self.geocode(city)
            if err:
                return err
            r = requests.get(
                f"{self.base}/weather",
                params={"lat": loc["lat"], "lon": loc["lon"], "appid": self.api_key, "units": units},
                timeout=10,
            ).json()
            if r.get("cod") != 200:
                return f"⚠️ Could not find weather for {city}. Try 'City,CountryCode' (e.g., 'Delhi,IN')."
            temp = r["main"]["temp"]
            desc = r["weather"][0]["description"].capitalize()
            unit_symbol = "°C" if units == "metric" else ("°F" if units == "imperial" else "K")
            name = loc["display"] or city
            return f"🌤️ Weather in {name}: {temp}{unit_symbol}, {desc}"
        except Exception:
            return "⚠️ Unable to fetch weather."

