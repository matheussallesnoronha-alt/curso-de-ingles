# MVP storage em memória. Troque por Postgres depois.

USERS = {}  # phone -> dict

def get_user(phone: str) -> dict:
    if phone not in USERS:
        USERS[phone] = {
            "subscription_active": True,     # 🔥 mude para False para testar bloqueio
            "level": "A2",
            "unit": "Past Simple",
        }
    return USERS[phone]

def set_subscription(phone: str, active: bool) -> None:
    u = get_user(phone)
    u["subscription_active"] = active
