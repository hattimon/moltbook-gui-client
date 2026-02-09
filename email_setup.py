import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

MOLTBOOK_API_KEY = os.getenv("MOLTBOOK_API_KEY")
if not MOLTBOOK_API_KEY:
    raise RuntimeError("Brak MOLTBOOK_API_KEY w .env")

if len(sys.argv) < 2:
    raise RuntimeError("Użycie: python email_setup.py adres@email")

email = sys.argv[1]

url = "https://www.moltbook.com/api/v1/agents/me/setup-owner-email"
headers = {
    "Authorization": f"Bearer {MOLTBOOK_API_KEY}",
    "Content-Type": "application/json",
}
data = {"email": email}

resp = requests.post(url, headers=headers, json=data, timeout=30)

print("Status:", resp.status_code)
print("Body:", resp.text)
