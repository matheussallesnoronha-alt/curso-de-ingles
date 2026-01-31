import os
from dotenv import load_dotenv

load_dotenv()

def _bool(v: str, default: bool=False) -> bool:
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","y","on")

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHATSAPP_GRAPH_URL = os.getenv("WHATSAPP_GRAPH_URL", "https://graph.facebook.com/v20.0")
PAYMENT_LINK = os.getenv("PAYMENT_LINK", "https://seulink.com/assinar")
SEND_AUDIO = _bool(os.getenv("SEND_AUDIO", "true"), True)

def validate_env() -> None:
    missing = []
    for k, v in {
        "VERIFY_TOKEN": VERIFY_TOKEN,
        "WHATSAPP_TOKEN": WHATSAPP_TOKEN,
        "PHONE_NUMBER_ID": PHONE_NUMBER_ID,
        "OPENAI_API_KEY": OPENAI_API_KEY,
    }.items():
        if not v:
            missing.append(k)
    if missing:
        raise RuntimeError("Variáveis faltando no .env: " + ", ".join(missing))
