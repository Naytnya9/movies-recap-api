import os
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

app = FastAPI()

# Gemini API Client
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
interesting, and detailed movie recap in Burmese language.

Rules:
- Write naturally in Burmese language.
- Explain the story in chronological order.
- Include important characters and important events.
- Make the story easy to understand.
- Make it suitable for a YouTube Movie Recap narration.
- Do not add unnecessary information that is not in the transcript.

Movie transcript:

{movie.transcript}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.7-flash",
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
