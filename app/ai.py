import requests
from app.config import OPENAI_API_KEY, PAYMENT_LINK
from app.storage import get_user

OPENAI_HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

def teacher_prompt(level: str, unit: str) -> str:
    # 🔥 ALTERE AQUI O SEU "CURSO"
    return (
        "You are an English teacher running a structured WhatsApp course (1:1).\n\n"
        f"Student level: {level}\n"
        f"Lesson topic: {unit}\n\n"
        "Rules:\n"
        "- Correct the student's sentence (show corrected version).\n"
        "- Explain briefly (max 2 short lines).\n"
        "- Stay on the lesson topic.\n"
        "- End with ONE question.\n"
        "- Be friendly, concise, and use simple vocabulary for the student's level.\n"
    )

def chat_teacher(level: str, unit: str, student_text: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": teacher_prompt(level, unit)},
            {"role": "user", "content": student_text}
        ],
        "temperature": 0.6
    }
    r = requests.post(url, headers={**OPENAI_HEADERS, "Content-Type": "application/json"}, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()

def transcribe(audio_bytes: bytes, filename: str="audio.ogg", mime_type: str="audio/ogg") -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    files = {"file": (filename, audio_bytes, mime_type)}
    data = {"model": "gpt-4o-transcribe"}
    r = requests.post(url, headers=OPENAI_HEADERS, files=files, data=data, timeout=60)
    r.raise_for_status()
    return r.json()["text"].strip()

def tts(text: str) -> bytes:
    url = "https://api.openai.com/v1/audio/speech"
    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "format": "ogg",
        "input": text
    }
    r = requests.post(url, headers={**OPENAI_HEADERS, "Content-Type": "application/json"}, json=payload, timeout=60)
    r.raise_for_status()
    return r.content

def handle_message_for_user(phone: str, incoming_type: str, text: str | None, audio_bytes: bytes | None, audio_filename: str="audio.ogg", audio_mime: str="audio/ogg") -> dict:
    user = get_user(phone)
    if not user["subscription_active"]:
        return {
            "blocked": True,
            "text": f"❌ Your subscription is inactive.\nRenew to continue: {PAYMENT_LINK}"
        }

    if incoming_type == "audio":
        student_text = transcribe(audio_bytes or b"", filename=audio_filename, mime_type=audio_mime)
    else:
        student_text = text or ""

    reply_text = chat_teacher(user["level"], user["unit"], student_text)
    reply_audio = tts(reply_text)
    return {"blocked": False, "text": reply_text, "audio_bytes": reply_audio}
