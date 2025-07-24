import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()
MASTER_KEY = os.getenv("MASTER_KEY")

app = FastAPI()
app.mount("/static", StaticFiles(directory="/mnt/data/static"), name="static")

db_file = "/mnt/data/leaderboard.json"
if not os.path.exists(db_file):
    with open(db_file, "w") as f:
        json.dump({}, f)

def load_db():
    with open(db_file, "r") as f:
        return json.load(f)

def save_db(data):
    with open(db_file, "w") as f:
        json.dump(data, f)

class ClickData(BaseModel):
    username: str
    clicks: int

@app.post("/click")
async def update_clicks(data: ClickData):
    db = load_db()
    db[data.username] = db.get(data.username, 0) + data.clicks
    save_db(db)
    return {"message": "Clicks updated", "total": db[data.username]}

@app.get("/leaderboard")
async def get_leaderboard():
    db = load_db()
    sorted_db = dict(sorted(db.items(), key=lambda item: item[1], reverse=True))
    return sorted_db

@app.get("/admin")
async def admin(request: Request):
    key = request.headers.get("Authorization")
    if not key or key != MASTER_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"message": "Welcome to the admin panel", "data": load_db()}
