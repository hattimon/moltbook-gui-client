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


def post_to_moltbook(submolt: str, title: str, content: str):
    """
    Utwórz post w danym submolcie.
    """
    url = f"{MOLTBOOK_API_BASE}/posts"
    data = {
        "submolt": submolt,
        "title": title,
        "content": content,
    }
    resp = requests.post(url, headers=_headers(), json=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


def list_posts(sort: str = "hot", limit: int = 20):
    """
    Pobierz listę postów (np. sort=hot|new).
    """
    url = f"{MOLTBOOK_API_BASE}/posts"
    params = {"sort": sort, "limit": limit}
    resp = requests.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_post(post_id: str):
    """
    Pobierz szczegóły pojedynczego posta.
    """
    url = f"{MOLTBOOK_API_BASE}/posts/{post_id}"
    resp = requests.get(url, headers=_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_post_comments(post_id: str):
    """
    Pobierz komentarze pod postem.
    """
    url = f"{MOLTBOOK_API_BASE}/posts/{post_id}/comments"
    resp = requests.get(url, headers=_headers(), timeout=30)
    resp.raise_for_status()
    return resp.json()
