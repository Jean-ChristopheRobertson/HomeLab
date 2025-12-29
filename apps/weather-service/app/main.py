from fastapi import FastAPI, Request
import random
import time
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
    return {"service": "weather-service", "status": "healthy"}

@app.get("/weather/{city}")
def get_weather(city: str):
    # Mock data for now
    conditions = ["Sunny", "Cloudy", "Rainy", "Snowy"]
    temp = random.randint(-10, 35)
    return {
        "city": city,
        "temperature": temp,
        "condition": random.choice(conditions),
        "unit": "C"
    }
