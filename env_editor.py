import os
from dotenv import load_dotenv, find_dotenv, set_key

# Ścieżka do .env w bieżącym katalogu repo
ENV_PATH = find_dotenv(usecwd=True) or os.path.join(os.getcwd(), ".env")


def load_env() -> str:
    """
    Zwraca zawartość pliku .env jako tekst.
    Jeśli plik nie istnieje, zwraca pusty string.
    """
    if not os.path.exists(ENV_PATH):
        return ""
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        return f.read()


def save_env(raw_text: str):
    """
    Zapisuje podany tekst jako zawartość .env i odświeża zmienne środowiskowe.
    """
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write(raw_text)
    load_dotenv(ENV_PATH, override=True)


def set_env_value(key: str, value: str):
    """
    Ustaw jedną zmienną w .env (tworzy plik, jeśli go nie ma).
    """
    set_key(ENV_PATH, key, value)
    load_dotenv(ENV_PATH, override=True)
