from fastapi import FastAPI
import random

app = FastAPI()

@app.get("/")
def read_root():
    return {"service": "hockey-service", "status": "healthy"}

@app.get("/scores")
def get_scores():
    # Mock data
    teams = ["Canadiens", "Maple Leafs", "Bruins", "Rangers", "Oilers"]
    games = []
    for i in range(3):
        home = random.choice(teams)
        away = random.choice([t for t in teams if t != home])
        games.append({
            "home": home,
            "away": away,
            "home_score": random.randint(0, 5),
            "away_score": random.randint(0, 5),
            "period": "Final"
        })
    return {"games": games}
