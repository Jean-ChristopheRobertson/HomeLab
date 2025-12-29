from fastapi import FastAPI, Request
from datetime import datetime
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
    return {"service": "news-service", "status": "healthy"}

@app.get("/news")
def get_news():
    return {
        "headlines": [
            {"title": "Local Man Builds Homelab", "category": "Tech", "timestamp": datetime.now().isoformat()},
            {"title": "Kubernetes Cluster Deployed Successfully", "category": "Tech", "timestamp": datetime.now().isoformat()},
            {"title": "Weather Forecast: Sunny with a chance of containers", "category": "Weather", "timestamp": datetime.now().isoformat()}
        ]
    }
