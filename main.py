from fastapi import FastAPI, WebSocket
import uuid
import wave
import os
import sys

# Ensure proper import path for Render deployment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api.route.whisper_stt import transcribe
from api.route.diarization import run_diarization
from api.preprocessing.firebase_client import save_transcription

os.makedirs("audio", exist_ok=True)

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Dentary backend is running"}

def save_audio(audio_bytes, filename):
    path = f"./audio/{filename}"
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio_bytes)
    return path

@app.websocket("/ws/stt")
async def stt_socket(websocket: WebSocket):
    await websocket.accept()
    buffer = bytearray()

    try:
        while True:
            chunk = await websocket.receive_bytes()
            buffer.extend(chunk)

            if len(buffer) >= 16000 * 2 * 5:
                filename = f"{uuid.uuid4()}.wav"
                path = save_audio(buffer, filename)
                buffer.clear()

                text = transcribe(path)
                speakers = run_diarization(path)

                save_transcription(filename, text)
                await websocket.send_json({
                    "text": text,
                    "filename": filename,
                    "speakers": speakers
                })

    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
