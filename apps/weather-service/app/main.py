from fastapi import FastAPI
import random

app = FastAPI()

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
