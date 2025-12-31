from fastapi import FastAPI, Request
import random
import time
import httpx
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI()

# Prometheus Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
    
    return response

@app.get("/")
def read_root():
    return {"service": "hockey-service", "status": "healthy"}

@app.get("/scores")
async def get_scores():
    try:
        url = "https://api-web.nhle.com/v1/schedule/now"
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                return {"error": "NHL API unavailable", "games": []}
                
            data = response.json()
            games = []
            
            # Get today's games (first element of gameWeek)
            if data.get("gameWeek") and len(data["gameWeek"]) > 0:
                today_games = data["gameWeek"][0].get("games", [])
                
                for game in today_games:
                    # Determine period/status
                    period = game.get("gameState", "Scheduled")
                    if "periodDescriptor" in game:
                        pd = game["periodDescriptor"]
                        if period == "LIVE" or period == "CRIT":
                            period = f"P{pd.get('number', '?')}"
                        elif period == "OFF" or period == "FINAL":
                            period = "Final"
                            if pd.get("periodType") == "OT": period += " (OT)"
                            elif pd.get("periodType") == "SO": period += " (SO)"

                    games.append({
                        "home": game["homeTeam"]["commonName"]["default"],
                        "away": game["awayTeam"]["commonName"]["default"],
                        "home_score": game["homeTeam"].get("score", 0),
                        "away_score": game["awayTeam"].get("score", 0),
                        "period": period
                    })
            
            return {"games": games}
            
    except Exception as e:
        print(f"Error fetching scores: {e}")
        return {"error": str(e), "games": []}
