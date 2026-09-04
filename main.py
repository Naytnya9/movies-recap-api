import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=[""], allow_credentials=False, allow_methods=[""], allow_headers=["*"])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
async def home(): return {"message": "Movie Recap AI API is running with Gemini!"}

@app.post("/recap")
async def recap(movie: dict): return {"success": True, "recap": client.models.generate_content(model="gemini-3.5-flash-lite", contents="Write a Burmese movie recap for this transcript: " + movie.get("transcript", "")).text}
