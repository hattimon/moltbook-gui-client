import requests

MOLTBOOK_REGISTER_URL = "https://www.moltbook.com/api/v1/agents/register"


def register_agent(name: str, description: str):
    """
    Zarejestruj agenta w Moltbook.
    """
    payload = {
        "name": name,
        "description": description,
    }
    resp = requests.post(MOLTBOOK_REGISTER_URL, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    # Przykład użycia CLI – można zostawić lub usunąć
    data = register_agent(
        name="Example_Agent",
        description="Example agent registered from CLI.",
    )
    import json

    print(json.dumps(data, indent=2))
