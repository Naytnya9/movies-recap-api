from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MovieRequest(BaseModel):
    transcript: str

@app.get("/")
def home():
    return {
        "message": "Movie Recap API is running!"
    }

@app.post("/recap")
def recap(movie: MovieRequest):

    text = movie.transcript

    return {
        "success": True,
        "original_text": text,
        "recap": "ဒီနေရာမှာ AI Movie Recap ထွက်လာမယ်"
    }
