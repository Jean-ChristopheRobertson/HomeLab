import httpx
import asyncio
import json

async def test_nhl_api():
    url = "https://api-web.nhle.com/v1/schedule/now"
    print(f"Testing URL: {url}")
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Success!")
                data = response.json()
                # Print the first game of the first date to understand structure
                if data.get("gameWeek") and len(data["gameWeek"]) > 0:
                    today_games = data["gameWeek"][0]
                    print(f"Date: {today_games.get('date')}")
                    if today_games.get("games"):
                        print("First game sample:")
                        print(json.dumps(today_games["games"][0], indent=2))
                    else:
                        print("No games for this date.")
                else:
                    print("No game week data found.")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_nhl_api())
