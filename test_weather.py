import asyncio
import httpx

async def test_weather(lat, lon):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print(f"Testing with lat={lat}, lon={lon}")
        
        # 1. Reverse Geocoding (BigDataCloud)
        try:
            url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
            print(f"Calling {url}...")
            resp = await client.get(url, params={"latitude": lat, "longitude": lon, "localityLanguage": "en"})
            print(f"Geo Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Geo Response: {resp.text[:200]}...")
                data = resp.json()
                city = data.get("city") or data.get("locality") or "Unknown"
                print(f"Resolved City: {city}")
            else:
                print(f"Geo failed: {resp.text}")
        except Exception as e:
            print(f"Reverse geocoding exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_weather(45.42, -75.69))
