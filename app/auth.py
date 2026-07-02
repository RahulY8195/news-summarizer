import os

from fastapi import Header, HTTPException

API_KEY = os.environ.get("API_KEY", "dev-key")


def require_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
