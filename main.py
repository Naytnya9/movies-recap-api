import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=[""],
allow_credentials=False,
allow_methods=[""],
allow_headers=["*"]
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
async def home():
return {"message": "Movie Recap AI API is running with Gemini!"}

@app.post("/recap")
async def recap(movie: dict):
transcript = movie.get("transcript", "")

try:
    prompt = "You are a professional movie recap writer. Read the following movie transcript and create a clear and interesting movie recap in Burmese language. Write naturally in Burmese. Explain the story in chronological order. Do not invent information. Make it suitable for YouTube movie recap narration.\n\nMovie transcript:\n\n" + transcript

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return {
        "success": True,
        "recap": response.text
    }

except Exception as e:
    return {
        "success": False,
        "error": str(e)
    }
