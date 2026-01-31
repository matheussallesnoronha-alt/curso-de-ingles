import requests
from app.config import WHATSAPP_TOKEN, PHONE_NUMBER_ID, WHATSAPP_GRAPH_URL

HEADERS = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

def _raise_for(r: requests.Response) -> None:
    try:
        r.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}") from e

def send_text(to_phone: str, text: str) -> None:
    url = f"{WHATSAPP_GRAPH_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text[:4096]}
    }
    r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=30)
    _raise_for(r)

def upload_media(file_bytes: bytes, filename: str, mime_type: str) -> str:
    url = f"{WHATSAPP_GRAPH_URL}/{PHONE_NUMBER_ID}/media"
    files = {"file": (filename, file_bytes, mime_type)}
    data = {"messaging_product": "whatsapp"}
    r = requests.post(url, headers=HEADERS, files=files, data=data, timeout=60)
    _raise_for(r)
    return r.json()["id"]

def send_audio_by_bytes(to_phone: str, audio_bytes: bytes, filename: str="reply.ogg") -> None:
    media_id = upload_media(audio_bytes, filename=filename, mime_type="audio/ogg")
    url = f"{WHATSAPP_GRAPH_URL}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "audio",
        "audio": {"id": media_id}
    }
    r = requests.post(url, headers={**HEADERS, "Content-Type": "application/json"}, json=payload, timeout=30)
    _raise_for(r)

def get_media_url(media_id: str) -> str:
    url = f"{WHATSAPP_GRAPH_URL}/{media_id}"
    r = requests.get(url, headers=HEADERS, timeout=30)
    _raise_for(r)
    return r.json()["url"]

def download_media(media_url: str) -> bytes:
    r = requests.get(media_url, headers=HEADERS, timeout=60)
    _raise_for(r)
    return r.content
