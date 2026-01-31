from fastapi import FastAPI, Request
from pydantic import BaseModel
import base64

from app.config import VERIFY_TOKEN, SEND_AUDIO, validate_env
from app.whatsapp import send_text, send_audio_by_bytes, get_media_url, download_media
from app.ai import handle_message_for_user

app = FastAPI(
    title="English WhatsApp Course (MVP)",
    docs_url="/docs",
    openapi_url="/openapi.json",
    redoc_url=None
)

@app.on_event("startup")
def _startup():
    # Se faltar variável no Render, vai falhar aqui.
    # (Depois a gente ajusta se necessário.)
    validate_env()

# ✅ Rota raiz para teste rápido
@app.get("/")
def root():
    return {"status": "ok", "service": "curso-de-ingles"}

# 1) Verificação do webhook (Meta chama no cadastro)
@app.get("/webhook")
def verify(hub_mode: str = "", hub_challenge: str = "", hub_verify_token: str = ""):
    if hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "verify token inválido"}

# 2) Receber mensagens do WhatsApp
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    change = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
    messages = change.get("messages", [])
    if not messages:
        return {"status": "no-messages"}

    msg = messages[0]
    phone = msg.get("from", "")
    mtype = msg.get("type", "")

    if mtype == "text":
        body = msg["text"]["body"]
        result = handle_message_for_user(phone, "text", body, None)
        send_text(phone, result["text"])
        if SEND_AUDIO and not result.get("blocked"):
            send_audio_by_bytes(phone, result["audio_bytes"])
        return {"status": "ok"}

    if mtype == "audio":
        media_id = msg["audio"]["id"]
        media_url = get_media_url(media_id)
        audio_bytes = download_media(media_url)
        result = handle_message_for_user(phone, "audio", None, audio_bytes, audio_filename="audio.ogg", audio_mime="audio/ogg")
        send_text(phone, result["text"])
        if SEND_AUDIO and not result.get("blocked"):
            send_audio_by_bytes(phone, result["audio_bytes"])
        return {"status": "ok"}

    send_text(phone, "Send me a text or a voice message in English 🙂")
    return {"status": "ok"}

# ======== TESTE LOCAL/REMOTO (sem WhatsApp) ========

class TestText(BaseModel):
    phone: str
    text: str

@app.post("/test/text")
def test_text(payload: TestText):
    result = handle_message_for_user(payload.phone, "text", payload.text, None)
    out = {"text": result["text"], "blocked": result.get("blocked", False)}
    if SEND_AUDIO and not result.get("blocked"):
        out["audio_b64"] = base64.b64encode(result["audio_bytes"]).decode("ascii")
    return out
