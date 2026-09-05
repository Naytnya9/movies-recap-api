import os
import time
import tempfile

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from google import genai

app = FastAPI()

Allow Snack Web Preview and mobile apps

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=False,
allow_methods=["*"],
allow_headers=["*"],
)

Gemini API

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

==========================================

TRANSCRIPT → BURMESE RECAP

==========================================

@app.post("/recap")
async def recap(movie: dict):

transcript = movie.get("transcript", "")

try:

    prompt = """

You are a professional YouTube movie recap writer.

Read the following movie transcript carefully.

Create a detailed and interesting movie recap in Burmese language.

Rules:

- Write naturally in Burmese.
- Explain the story in chronological order.
- Include important characters and events.
- Do not invent information that is not in the transcript.
- Make it suitable for YouTube movie recap narration.

Movie transcript:

""" + transcript

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

==========================================

VIDEO → GEMINI → BURMESE RECAP

==========================================

@app.post("/upload-video")
async def upload_video(
video: UploadFile = File(...)
):
  
    temp_path = None
  
    try:

    # Create temporary file
    suffix = ".mp4"

    if video.filename and "." in video.filename:
        suffix = "." + video.filename.split(".")[-1]


    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:

        temp_path = temp_file.name


        # Save uploaded video
        while True:

            chunk = await video.read(
                1024 * 1024
            )

            if not chunk:
                break

            temp_file.write(chunk)


    # Upload video to Gemini Files API
    gemini_file = client.files.upload(
        file=temp_path
    )


    # Wait until Gemini finishes processing video
    while (
        not gemini_file.state
        or gemini_file.state.name != "ACTIVE"
    ):

        time.sleep(5)

        gemini_file = client.files.get(
            name=gemini_file.name
        )


    # Ask Gemini to analyze movie
    prompt = """

You are an expert movie analyst and professional
YouTube movie recap writer.

Watch and analyze this entire video carefully.

Then create a clear, detailed and interesting
movie recap in Burmese language.

Rules:

- Explain the story in chronological order.
- Describe important characters.
- Explain important events.
- Include important plot twists.
- Do not invent scenes or information.
- Write naturally in Burmese.
- Make the result suitable for a YouTube
  movie recap narration.

Now create the complete Burmese movie recap.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[
            gemini_file,
            prompt
        ]
    )


    # Delete temporary file
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)


    return {
        "success": True,
        "recap": response.text
    }


except Exception as e:

    # Delete temporary file if error happens
    if temp_path and os.path.exists(temp_path):
        os.remove(temp_path)


    return {
        "success": False,
        "error": str(e)
    }
