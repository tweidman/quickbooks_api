#!/usr/bin/env python3
"""
Example: Query QuickBooks customers via the REST API.
Run from project root with .env configured.
"""
import os
import sys
import json
import urllib.parse
import requests
from pathlib import Path

# Load .env from project root
ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / ".env"
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)

CLIENT_ID = os.getenv("QUICKBOOKS_CLIENT_ID")
CLIENT_SECRET = os.getenv("QUICKBOOKS_CLIENT_SECRET")
REALM_ID = os.getenv("QUICKBOOKS_REALM_ID")
REFRESH_TOKEN = os.getenv("QUICKBOOKS_REFRESH_TOKEN")
ENV = os.getenv("QUICKBOOKS_ENVIRONMENT", "sandbox")

BASE_URL = "https://sandbox-quickbooks.api.intuit.com" if ENV == "sandbox" else "https://quickbooks.api.intuit.com"


def get_access_token() -> str:
    """Exchange refresh token for access token."""
    resp = requests.post(
        "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Accept": "application/json"},
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def query(access_token: str, q: str) -> dict:
    """Run a QuickBooks query."""
    encoded = urllib.parse.quote(q)
    url = f"{BASE_URL}/v3/company/{REALM_ID}/query?query={encoded}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {access_token}"})
    resp.raise_for_status()
    return resp.json()


def main():
    if not all([CLIENT_ID, CLIENT_SECRET, REALM_ID, REFRESH_TOKEN]):
        print("Missing credentials. Copy .env.example to .env and add your QuickBooks API values.")
        sys.exit(1)

    token = get_access_token()
    result = query(token, "SELECT * FROM Customer WHERE Active = true STARTPOSITION 1 MAXRESULTS 10")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
