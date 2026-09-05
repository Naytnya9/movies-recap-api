import os
import time
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=False,
allow_methods=["*"],
allow_headers=["*"],
)

client = genai.Client(
api_key=os.getenv("GEMINI_API_KEY")
)

@app.get("/")
async def home():
    return {
"message": "Movie Recap AI API is running with Gemini!"
}

@app.get("/test")
async def test():
return {
"success": True,
"message": "CORS test successful!"
}

@app.post("/recap")
async def recap(movie: dict):

transcript = movie.get("transcript", "")

try:

    prompt = (
        "You are a professional movie recap writer. "
        "Read the following movie transcript carefully and create "
        "a detailed and interesting movie recap in Burmese language. "
        "Explain the story in chronological order. "
        "Do not invent information. "
        "Make it suitable for YouTube movie recap narration.\n\n"
        "Movie transcript:\n\n"
        + transcript
    )

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

@app.post("/upload-video")
async def upload_video(video: UploadFile = File(...)):

temp_path = None

try:

    suffix = ".mp4"

    if video.filename and "." in video.filename:
        suffix = "." + video.filename.split(".")[-1]

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_path = temp_file.name

        while True:

            chunk = await video.read(1024 * 1024)

            if not chunk:
                break

            temp_file.write(chunk)

    gemini_file = client.files.upload(
        file=temp_path
    )

    while True:

        gemini_file = client.files.get(
            name=gemini_file.name
        )

        if (
            gemini_file.state
            and gemini_file.state.name == "ACTIVE"
        ):
            break

        time.sleep(5)

    prompt = (
        "Watch this video carefully and analyze the story. "
        "Create a detailed and interesting movie recap in Burmese language. "
        "Explain the story in chronological order. "
        "Describe important characters and events. "
        "Include important plot twists. "
        "Do not invent information that is not shown in the video. "
        "Write naturally in Burmese and make it suitable for "
        "YouTube movie recap narration."
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            gemini_file,
            prompt
        ]
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

finally:

    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)
