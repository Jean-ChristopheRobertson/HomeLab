from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

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
