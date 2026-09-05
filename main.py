import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.get("/")
async def home(): return {"message": "Movie Recap AI API is running with Gemini!"}

@app.get("/test")
async def test(): return {"success": True, "message": "CORS test successful!"}

@app.post("/recap")
async def recap(movie: dict):
    transcript = movie.get("transcript", "")
    try:
        response = client.models.generate_content(model="gemini-3.5-flash-lite", contents="Write a Burmese movie recap for this transcript: " + transcript)
        return {"success": True, "recap": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/upload-video")
async def upload_video(video: UploadFile = File(...)): return {"success": True, "message": "Video received successfully!", "filename": video.filename, "content_type": video.content_type}
