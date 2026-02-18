#!/usr/bin/env python3
"""
Search for a QuickBooks customer by name.
Loads credentials from mcp-server/.env
Usage: python search_customer.py "Todd Weidman"
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
        print("Missing credentials. Complete OAuth first (use a QuickBooks MCP tool in Cursor, or run the MCP server).")
        print("mcp-server/.env needs QUICKBOOKS_REFRESH_TOKEN and QUICKBOOKS_REALM_ID from the OAuth flow.")
        sys.exit(1)

    token = get_access_token()
    # Search by DisplayName (case-insensitive like); fallback to all customers if no match
    q = f"SELECT * FROM Customer WHERE DisplayName LIKE '%{name}%' STARTPOSITION 1 MAXRESULTS 25"
    result = query(token, q)
    customers = result.get("QueryResponse", {}).get("Customer")
    if not customers:
        # Try unfiltered to list all customers
        q_all = "SELECT * FROM Customer STARTPOSITION 1 MAXRESULTS 50"
        result = query(token, q_all)
        customers = result.get("QueryResponse", {}).get("Customer")
        if customers:
            print(f"No customer found matching '{name}'. Here are your customers:\n")
        else:
            print(f"No customer found matching '{name}', and no customers in QuickBooks.\n")
    else:
        print(f"Found {len(customers) if isinstance(customers, list) else 1} customer(s) matching '{name}':\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
