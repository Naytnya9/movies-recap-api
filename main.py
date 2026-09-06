import os
import time
import tempfile
import base64
import wave
import uuid
import subprocess

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google import genai


app = FastAPI()


# =========================
# CREATE FOLDERS
# =========================

os.makedirs("generated_audio", exist_ok=True)
os.makedirs("generated_video", exist_ok=True)


# =========================
# SERVE AUDIO FILES
# =========================

app.mount(
    "/audio",
    StaticFiles(directory="generated_audio"),
    name="audio"
)


# =========================
# SERVE VIDEO FILES
# =========================

app.mount(
    "/video",
    StaticFiles(directory="generated_video"),
    name="video"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# GEMINI CLIENT
# =========================

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================
# HOME
# =========================

@app.get("/")
async def home():

    return {
        "message": "Movie Recap AI API is running with Gemini!"
    }


# =========================
# TEST
# =========================

@app.get("/test")
async def test():

    return {
        "success": True,
        "message": "CORS test successful!"
    }


# =========================
# GEMINI TEST
# =========================

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


# =========================
# TRANSCRIPT RECAP
# =========================

@app.post("/recap")
async def recap(movie: dict):

    try:

        transcript = movie.get(
            "transcript",
            ""
        )

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


# =========================
# VIDEO UPLOAD + ANALYZE
# =========================

@app.post("/upload-video")
async def upload_video(
    video: UploadFile = File(...)
):

    temp_path = None


    try:

        suffix = ".mp4"


        if (
            video.filename
            and "." in video.filename
        ):

            suffix = (
                "."
                + video.filename.split(".")[-1]
            )


        # Save uploaded video temporarily

        with tempfile.NamedTemporaryFile(

            delete=False,
            suffix=suffix

        ) as temp_file:


            temp_path = temp_file.name


            while True:

                chunk = await video.read(
                    1024 * 1024
                )


                if not chunk:
                    break


                temp_file.write(chunk)


        print(
            "VIDEO UPLOADED TO SERVER"
        )


        # Upload video to Gemini

        gemini_file = client.files.upload(
            file=temp_path
        )


        print(
            "WAITING FOR GEMINI VIDEO PROCESSING"
        )


        # Wait until Gemini file is ready

        while (

            not gemini_file.state
            or gemini_file.state.name != "ACTIVE"

        ):

            time.sleep(5)


            gemini_file = client.files.get(
                name=gemini_file.name
            )


        print(
            "GEMINI VIDEO READY"
        )


        # Generate Burmese recap

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

        print(
            "VIDEO ANALYSIS ERROR:",
            str(e)
        )


        return {

            "success": False,
            "error": str(e)

        }


    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(temp_path)


# =========================
# VIDEO SYSTEM TEST
# =========================

@app.get("/video-test")
async def video_test():

    return {

        "success": True,
        "message": "Video system ready!"

    }


# =========================
# GENERATE AI AUDIO
# =========================

@app.post("/generate-audio")
async def generate_audio(
    data: dict
):

    try:

        text = data.get(
            "text",
            ""
        ).strip()


        if not text:

            return {

                "success": False,
                "error": "No text provided"

            }


        print(
            "GENERATING AI VOICE"
        )


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

        filename = (
            f"recap_{uuid.uuid4().hex}.wav"
        )


        audio_path = os.path.join(

            "generated_audio",

            filename

        )


        # Save audio as WAV

        with wave.open(
            audio_path,
            "wb"
        ) as audio_file:


            audio_file.setnchannels(1)

            audio_file.setsampwidth(2)

            audio_file.setframerate(24000)

            audio_file.writeframes(
                audio_data
            )


        audio_url = (

            "https://movies-recap-api.onrender.com/audio/"
            + filename

        )


        print(
            "AUDIO GENERATED:",
            audio_url
        )


        return {

            "success": True,

            "message":
                "Audio generated successfully",

            "audio_url":
                audio_url

        }


    except Exception as e:

        print(
            "AUDIO ERROR:",
            str(e)
        )


        return {

            "success": False,
            "error": str(e)

        }


# =========================
# GENERATE FINAL RECAP VIDEO
# =========================

@app.post("/generate-recap-video")
async def generate_recap_video(

    video: UploadFile = File(...),

    audio_filename: str = Form(...)

):

    temp_video_path = None


    try:

        print(
            "FINAL VIDEO REQUEST RECEIVED"
        )

        print(
            "Audio filename:",
            audio_filename
        )


        # Find generated audio

        audio_path = os.path.join(

            "generated_audio",

            audio_filename

        )


        if not os.path.exists(
            audio_path
        ):

            return {

                "success": False,

                "error":
                    f"Audio file not found: {audio_filename}"

            }


        # Get video extension

        suffix = ".mp4"


        if (
            video.filename
            and "." in video.filename
        ):

            suffix = (
                "."
                + video.filename.split(".")[-1]
            )


        # Save uploaded video temporarily

        with tempfile.NamedTemporaryFile(

            delete=False,

            suffix=suffix

        ) as temp_file:


            temp_video_path = temp_file.name


            while True:

                chunk = await video.read(
                    1024 * 1024
                )


                if not chunk:
                    break


                temp_file.write(chunk)


        print(
            "FINAL VIDEO UPLOADED"
        )


        # Create output filename

        output_filename = (
            f"recap_video_{uuid.uuid4().hex}.mp4"
        )


        output_path = os.path.join(

            "generated_video",

            output_filename

        )


        print(
            "STARTING FFMPEG"
        )


        # Combine original video + AI voice

        command = [

            "ffmpeg",

            "-y",

            "-i",
            temp_video_path,

            "-i",
            audio_path,

            "-map",
            "0:v:0",

            "-map",
            "1:a:0",

            "-c:v",
            "copy",

            "-c:a",
            "aac",

            "-shortest",

            output_path

        ]


        result = subprocess.run(

            command,

            capture_output=True,

            text=True

        )


        if result.returncode != 0:

            print(
                "FFMPEG ERROR:"
            )

            print(
                result.stderr
            )


            return {

                "success": False,

                "error":
                    result.stderr[-3000:]

            }


        print(
            "FINAL VIDEO CREATED SUCCESSFULLY"
        )


        video_url = (

            "https://movies-recap-api.onrender.com/video/"
            + output_filename

        )


        return {

            "success": True,

            "message":
                "Recap video generated successfully!",

            "video_url":
                video_url

        }


    except Exception as e:

        print(
            "FINAL VIDEO ERROR:",
            str(e)
        )


        return {

            "success": False,

            "error":
                str(e)

        }


    finally:

        # Delete temporary uploaded video

        if (

            temp_video_path

            and os.path.exists(
                temp_video_path
            )

        ):

            os.remove(
                temp_video_path
            )


# =========================
# FFMPEG TEST
# =========================

@app.get("/ffmpeg-test")
async def ffmpeg_test():

    try:

        result = subprocess.run(

            ["ffmpeg", "-version"],

            capture_output=True,

            text=True

        )


        return {

            "success":
                result.returncode == 0,

            "ffmpeg_installed":
                result.returncode == 0,

            "version":
                result.stdout[:500]

        }


    except Exception as e:

        return {

            "success": False,

            "ffmpeg_installed": False,

            "error": str(e)

        }