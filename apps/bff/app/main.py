from fastapi import FastAPI, Request, Response
import httpx
import asyncio
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

app = FastAPI()

# Prometheus Metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status_code"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"])

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path, status_code=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=request.url.path).observe(process_time)
    
    return response

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
