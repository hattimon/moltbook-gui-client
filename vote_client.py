import os
import requests
from dotenv import load_dotenv

load_dotenv()

MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")
MOLTBOOK_API_BASE = "https://www.moltbook.com/api/v1"

if not MOLTBOOK_API_KEY:
    raise RuntimeError("Missing MOLTBOOK_API_KEY in .env")


def _headers():
    return {
        "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
        "Content-Type": "application/json",
    }


def add_comment(post_id: str, content: str):
    """
    Dodaj komentarz do istniejącego posta.
    """
    url = f"{MOLTBOOK_API_BASE}/posts/{post_id}/comments"
    data = {"content": content}
    resp = requests.post(url, headers=_headers(), json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()
