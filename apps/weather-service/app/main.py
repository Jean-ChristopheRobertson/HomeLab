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
    return {"service": "weather-service", "status": "healthy"}

@app.get("/weather/coordinates")
async def get_weather_by_coords(lat: float, lon: float):
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # 1. Reverse Geocoding to get City Name
            city_name = f"{lat:.2f}, {lon:.2f}" # Default fallback
            try:
                # Use BigDataCloud for reverse geocoding (No API key required, free tier)
                reverse_geo_url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
                geo_resp = await client.get(reverse_geo_url, params={"latitude": lat, "longitude": lon, "localityLanguage": "en"})
                
                if geo_resp.status_code == 200:
                    data = geo_resp.json()
                    city_name = data.get("city") or data.get("locality") or city_name
                else:
                    print(f"Reverse geocoding failed with status {geo_resp.status_code}: {geo_resp.text}")
            except Exception as e:
                print(f"Reverse geocoding exception: {e}")

            # 2. Weather
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true"
            }
            weather_resp = await client.get(weather_url, params=params)
            
            if weather_resp.status_code != 200:
                print(f"Weather API failed with status {weather_resp.status_code}: {weather_resp.text}")
                return {"error": "Weather API unavailable"}
                
            data = weather_resp.json()["current_weather"]
            
            # Map WMO codes to text
            wmo_code = data["weathercode"]
            condition = "Unknown"
            if wmo_code == 0: condition = "Clear sky"
            elif wmo_code in [1, 2, 3]: condition = "Partly cloudy"
            elif wmo_code in [45, 48]: condition = "Fog"
            elif wmo_code in [51, 53, 55, 56, 57]: condition = "Drizzle"
            elif wmo_code in [61, 63, 65, 66, 67, 80, 81, 82]: condition = "Rain"
            elif wmo_code in [71, 73, 75, 77, 85, 86]: condition = "Snow"
            elif wmo_code >= 95: condition = "Thunderstorm"

            return {
                "city": city_name,
                "temperature": data["temperature"],
                "condition": condition,
                "unit": "C"
            }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {
            "city": "Unknown",
            "temperature": 0,
            "condition": "Error fetching data",
            "unit": "C"
        }

@app.get("/weather/{city}")
async def get_weather(city: str):
    try:
        async with httpx.AsyncClient() as client:
            # 1. Geocoding
            geo_url = "https://geocoding-api.open-meteo.com/v1/search"
            geo_resp = await client.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"})
            
            if geo_resp.status_code != 200 or "results" not in geo_resp.json():
                # Fallback to mock data if API fails or city not found
                return {
                    "city": city, 
                    "temperature": random.randint(-10, 35),
                    "condition": "Mock Data (City Not Found)",
                    "unit": "C"
                }
            
            location = geo_resp.json()["results"][0]
            lat = location["latitude"]
            lon = location["longitude"]
            real_name = location["name"]
            
            # 2. Weather
            weather_url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true"
            }
            weather_resp = await client.get(weather_url, params=params)
            
            if weather_resp.status_code != 200:
                return {"city": city, "error": "Weather API unavailable"}
                
            data = weather_resp.json()["current_weather"]
            
            # Map WMO codes to text
            wmo_code = data["weathercode"]
            condition = "Unknown"
            if wmo_code == 0: condition = "Clear sky"
            elif wmo_code in [1, 2, 3]: condition = "Partly cloudy"
            elif wmo_code in [45, 48]: condition = "Fog"
            elif wmo_code in [51, 53, 55, 56, 57]: condition = "Drizzle"
            elif wmo_code in [61, 63, 65, 66, 67, 80, 81, 82]: condition = "Rain"
            elif wmo_code in [71, 73, 75, 77, 85, 86]: condition = "Snow"
            elif wmo_code >= 95: condition = "Thunderstorm"

            return {
                "city": real_name,
                "temperature": data["temperature"],
                "condition": condition,
                "unit": "C"
            }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return {
            "city": city,
            "temperature": 0,
            "condition": "Error fetching data",
            "unit": "C"
        }
