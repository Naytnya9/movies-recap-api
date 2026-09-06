import os
import time
import tempfile
import base64
import wave
import uuid
import subprocess
import shutil

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google import genai


app = FastAPI()


# Create folder for generated audio files
os.makedirs("generated_audio", exist_ok=True)

# Create folder for generated video files
os.makedirs("generated_video", exist_ok=True)


# Serve generated audio files
app.mount(
    "/audio",
    StaticFiles(directory="generated_audio"),
    name="audio"
)


# Serve generated video files
app.mount(
    "/video",
    StaticFiles(directory="generated_video"),
    name="video"
)


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


@app.get("/gemini-test")
async def gemini_test():
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents="Say hello in Burmese"
        )

        return {
            "success": True,
            "result": response.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/recap")
async def recap(movie: dict):
    try:
        transcript = movie.get("transcript", "")

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=f"""
Write a detailed movie recap in Burmese language.

Explain the story clearly from beginning to end.

Movie transcript:

{transcript}
"""
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

        while (
            not gemini_file.state
            or gemini_file.state.name != "ACTIVE"
        ):
            time.sleep(5)

            gemini_file = client.files.get(
                name=gemini_file.name
            )

        result = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=[
                gemini_file,
                """
Analyze this movie video and create a detailed movie recap
in Burmese language.

Explain the complete story clearly from beginning to end.
"""
            ]
        )

        return {
            "success": True,
            "recap": result.text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.get("/video-test")
async def video_test():
    return {
        "success": True,
        "message": "Video system ready!"
    }


@app.post("/generate-audio")
async def generate_audio(data: dict):

    try:
        text = data.get("text", "").strip()

        if not text:
            return {
                "success": False,
                "error": "No text provided"
            }

        interaction = client.interactions.create(
            model="gemini-3.1-flash-tts-preview",
            input=text,
            response_format={
                "type": "audio"
            },
            generation_config={
                "speech_config": [
                    {
                        "voice": "Kore"
                    }
                ]
            }
        )

        audio_data = base64.b64decode(
            interaction.output_audio.data
        )

        # Create unique filename
        filename = f"recap_{uuid.uuid4().hex}.wav"

        audio_path = os.path.join(
            "generated_audio",
            filename
        )

        # Save PCM audio as WAV
        with wave.open(audio_path, "wb") as audio_file:
            audio_file.setnchannels(1)
            audio_file.setsampwidth(2)
            audio_file.setframerate(24000)
            audio_file.writeframes(audio_data)

        audio_url = (
            "https://movies-recap-api.onrender.com/audio/"
            + filename
        )

        return {
            "success": True,
            "message": "Audio generated successfully",
            "audio_url": audio_url
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Test whether FFmpeg is installed
@app.get("/ffmpeg-test")
async def ffmpeg_test():

    try:

        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True
        )

        return {
            "success": True,
            "ffmpeg_installed": result.returncode == 0,
            "version": result.stdout[:500]
        }

    except FileNotFoundError:

        return {
            "success": False,
            "ffmpeg_installed": False,
            "error": "FFmpeg is not installed on this server"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }