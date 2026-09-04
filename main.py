import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI()

Allow Expo Snack, Web, and Mobile apps to access this API

app.add_middleware(
CORSMiddleware,
allow_origins=[""],
allow_credentials=False,
allow_methods=[""],
allow_headers=["*"],
)

client = genai.Client(
api_key=os.getenv("GEMINI_API_KEY")
)

class MovieRequest(BaseModel):
transcript: str

@app.get("/")
def home():
return {
"message": "Movie Recap AI API is running with Gemini!"
}

@app.post("/recap")
def recap(movie: MovieRequest):

prompt = f"""

You are a professional movie recap writer.

Read the following movie transcript and create a clear,
interesting movie recap in Burmese language.

Rules:

- Write naturally in Burmese.
- Explain the story in chronological order.
- Include important characters and important events.
- Do not invent information.
- Make it suitable for a YouTube movie recap narration.

Movie transcript:

{movie.transcript}
"""

try:
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
