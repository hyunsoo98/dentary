import torch
from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
import os
from dotenv import load_dotenv

load_dotenv()

device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    token=os.getenv("HUGGINGFACE_TOKEN")
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
    return_timestamps=False
)

def transcribe(filepath):
    return asr_pipeline(filepath)["text"]
