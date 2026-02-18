#!/usr/bin/env python3
"""
Search for a QuickBooks vendor by name.
Loads credentials from mcp-server/.env
Usage: python search_vendor.py "Todd Weidman"
"""
import os
import sys
import json
import urllib.parse
import requests
from pathlib import Path

# Load .env from mcp-server (where QuickBooks creds live)
ROOT = Path(__file__).resolve().parent.parent
env_path = ROOT / "mcp-server" / ".env"
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
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "Todd Weidman"

    if not all([CLIENT_ID, CLIENT_SECRET, REALM_ID, REFRESH_TOKEN]):
        print("Missing credentials. Complete OAuth first.")
        sys.exit(1)

    token = get_access_token()
    q = f"SELECT * FROM Vendor WHERE DisplayName LIKE '%{name}%' STARTPOSITION 1 MAXRESULTS 25"
    result = query(token, q)
    vendors = result.get("QueryResponse", {}).get("Vendor")
    if not vendors:
        q_all = "SELECT * FROM Vendor STARTPOSITION 1 MAXRESULTS 50"
        result = query(token, q_all)
        vendors = result.get("QueryResponse", {}).get("Vendor")
        if vendors:
            print(f"No vendor found matching '{name}'. Here are your vendors:\n")
        else:
            print(f"No vendor found matching '{name}', and no vendors in QuickBooks.\n")
    else:
        count = len(vendors) if isinstance(vendors, list) else 1
        print(f"Found {count} vendor(s) matching '{name}':\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
