from fastapi import FastAPI
import httpx
import asyncio

app = FastAPI()

# Service URLs (Kubernetes DNS)
WEATHER_URL = "http://weather-service"
HOCKEY_URL = "http://hockey-service"
NEWS_URL = "http://news-service"

@app.get("/")
def read_root():
    return {"service": "bff", "status": "healthy"}

@app.get("/dashboard")
async def get_dashboard():
    async with httpx.AsyncClient() as client:
        # Fetch data in parallel
        weather_task = client.get(f"{WEATHER_URL}/weather/Montreal")
        hockey_task = client.get(f"{HOCKEY_URL}/scores")
        news_task = client.get(f"{NEWS_URL}/news")

        results = await asyncio.gather(weather_task, hockey_task, news_task, return_exceptions=True)

    dashboard_data = {
        "weather": results[0].json() if not isinstance(results[0], Exception) else {"error": "Service unavailable"},
        "hockey": results[1].json() if not isinstance(results[1], Exception) else {"error": "Service unavailable"},
        "news": results[2].json() if not isinstance(results[2], Exception) else {"error": "Service unavailable"},
    }
    return dashboard_data
