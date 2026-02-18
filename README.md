# QuickBooks API Explorer

Project for querying QuickBooks Online data via the API and MCP server. Use this when QuickBooks built-in reports don't meet your needs and you have specific queries to run.

## Project Structure

```
quickbooks_api/
├── mcp-server/       # Intuit's official QuickBooks MCP server (Node.js)
├── scripts/          # Python scripts for direct API queries
├── .env.example      # Template for credentials
└── README.md
```

## Quick Start

### 1. Get API Credentials

1. Go to [Intuit Developer Portal](https://developer.intuit.com/)
2. Create a new app (or use an existing one)
3. Get **Client ID** and **Client Secret** from the app's keys section
4. Add `http://localhost:8000/callback` to Redirect URIs

### 2. MCP Server (for AI/Cursor integration)

```bash
cd mcp-server
npm install
```

Copy `mcp-server/.env` and fill in your credentials. For production data, set:

```
QUICKBOOKS_ENVIRONMENT=production
```

Add the MCP server to Cursor (after `npm run build` in `mcp-server/`):
1. Open **Cursor Settings → MCP**
2. Add a new server. The server reads credentials from `mcp-server/.env` — configure `cwd` so it finds that file:

```json
{
  "quickbooks": {
    "command": "node",
    "args": ["dist/index.js"],
    "cwd": "/Users/toddweidman/quickbooks_api/mcp-server"
  }
}
```

### 3. Direct API Scripts (Python)

```bash
cd scripts
pip install -r requirements.txt
```

Copy `.env.example` to `.env` in the project root and add your credentials. Run example queries:

```bash
python query_customers.py
```

## API Query Syntax (Quick Reference)

QuickBooks uses SQL-like syntax with limitations:

```sql
SELECT * FROM Customer WHERE active = true
SELECT * FROM Invoice WHERE TxnDate >= '2024-01-01' ORDERBY metadata.lastupdatedtime DESC
SELECT * FROM Bill STARTPOSITION 1 MAXRESULTS 100
```

**Limitations:** No `JOIN`, `GROUP BY`, or `OR` in WHERE. Use `STARTPOSITION` / `MAXRESULTS` for pagination.

## Resources

- [QuickBooks Online API Docs](https://developer.intuit.com/app/developer/qbo/docs/learn/explore-the-quickbooks-online-api)
- [API Explorer](https://developer.intuit.com/app/developer/qbo/docs/develop/rest-api/query-syntax)
- [MCP Server Repo](https://github.com/intuit/quickbooks-online-mcp-server)
