# QuickBooks API — Finish Setup

## Checklist

### 1. MCP server credentials (`mcp-server/.env`)

You already have `mcp-server/.env`. Ensure it contains:

```
QUICKBOOKS_CLIENT_ID=...
QUICKBOOKS_CLIENT_SECRET=...
QUICKBOOKS_ENVIRONMENT=sandbox   # or production for live data
```

After first use, `QUICKBOOKS_REFRESH_TOKEN` and `QUICKBOOKS_REALM_ID` are added by the OAuth flow.

### 2. Build the MCP server

```bash
cd mcp-server
npm install
npm run build
```

### 3. Add MCP server to Cursor

1. Open **Cursor Settings → Features → MCP**
2. Edit `~/.cursor/mcp.json` (or use the UI) and add:

```json
{
  "quickbooks": {
    "command": "node",
    "args": ["dist/index.js"],
    "cwd": "/Users/toddweidman/quickbooks_api/mcp-server"
  }
}
```

3. Restart Cursor or reload the window so the QuickBooks tools are available.

### 4. Python scripts (optional)

For direct REST queries:

```bash
cp .env.example .env
# Edit .env with your credentials (same as MCP, add QUICKBOOKS_REALM_ID and QUICKBOOKS_REFRESH_TOKEN)

cd scripts
pip install -r requirements.txt
python query_customers.py
```

### 5. Test

Ask Cursor: *"Search for active QuickBooks customers"* — it should use the `search_customers` MCP tool.
