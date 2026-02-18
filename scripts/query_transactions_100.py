#!/usr/bin/env python3
"""
Query QuickBooks for transactions of exactly $100 in the last 3 months.
Loads credentials from mcp-server/.env
"""
import os
import json
import urllib.parse
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Load .env from mcp-server
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

# 3 months ago from today
three_months_ago = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")


def get_access_token() -> str:
    resp = requests.post(
        "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
        auth=(CLIENT_ID, CLIENT_SECRET),
        headers={"Accept": "application/json"},
        data={"grant_type": "refresh_token", "refresh_token": REFRESH_TOKEN},
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def query(access_token: str, q: str) -> dict:
    encoded = urllib.parse.quote(q)
    url = f"{BASE_URL}/v3/company/{REALM_ID}/query?query={encoded}"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()


def main():
    if not all([CLIENT_ID, CLIENT_SECRET, REALM_ID, REFRESH_TOKEN]):
        print("Missing credentials.")
        exit(1)

    token = get_access_token()
    all_results = []

    # Query each transaction type for TotalAmt = 100, TxnDate in last 3 months
    entities = [
        ("Invoice", "invoices"),
        ("Bill", "bills"),
        ("Purchase", "purchases"),
        ("Payment", "customer payments"),
        ("BillPayment", "bill payments"),
    ]

    # Fetch all transactions in date range, filter for $100 in Python
    # (QuickBooks amount filter can be finicky with decimals)
    for entity, label in entities:
        q = f"SELECT * FROM {entity} WHERE TxnDate >= '{three_months_ago}' STARTPOSITION 1 MAXRESULTS 1000"
        try:
            result = query(token, q)
            items = result.get("QueryResponse", {}).get(entity)
            if items:
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    amt = item.get("TotalAmt") or item.get("Balance")
                    if amt is not None and float(amt) == 100:
                        item["_EntityType"] = entity
                        all_results.append(item)
        except Exception:
            pass

    # Sort by date
    def get_date(t):
        return t.get("TxnDate") or t.get("MetaData", {}).get("CreateTime") or ""

    all_results.sort(key=get_date)

    print(f"Transactions of exactly $100 (last 3 months, since {three_months_ago}):\n")
    if not all_results:
        print("No transactions found.")
    else:
        print(json.dumps(all_results, indent=2))

    print(f"\n--- Total: {len(all_results)} transaction(s) ---")


if __name__ == "__main__":
    main()
