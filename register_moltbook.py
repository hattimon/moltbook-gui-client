import requests

MOLTBOOK_REGISTER_URL = "https://www.moltbook.com/api/v1/agents/register"


def register_agent(name: str, description: str):
    """
    Zarejestruj agenta w Moltbook.

    Zwraca krotkę (ok, data):
    - ok = True  -> rejestracja udana, data = JSON z odpowiedzi.
    - ok = False -> błąd HTTP, data = JSON z komunikatem błędu lub tekst.
    """
    payload = {
        "name": name,
        "description": description,
    }

    try:
        resp = requests.post(MOLTBOOK_REGISTER_URL, json=payload, timeout=30)
        resp.raise_for_status()
        return True, resp.json()
    except requests.HTTPError:
        try:
            return False, resp.json()
        except Exception:
            return False, {"error": resp.text, "status_code": resp.status_code}


if __name__ == "__main__":
    ok, data = register_agent(
        name="Example_Agent",
        description="Example agent registered from CLI.",
    )

    import json

    print("OK:", ok)
    print(json.dumps(data, indent=2, ensure_ascii=False))
