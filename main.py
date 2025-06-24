from fastapi import FastAPI, WebSocket
import uuid
import wave
import os
from whisper_stt import transcribe
from diarization import run_diarization
from firebase_client import save_transcription

os.makedirs("audio", exist_ok=True)

app = FastAPI()

def save_audio(audio_bytes, filename):
    path = f"./audio/{filename}"
    os.makedirs("audio", exist_ok=True)
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
