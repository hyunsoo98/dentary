import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()
cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
firebase_admin.initialize_app(cred)

db = firestore.client()

def save_transcription(filename: str, text: str):
    doc_ref = db.collection("transcriptions").document()
    doc_ref.set({
        "filename": filename,
        "text": text,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
