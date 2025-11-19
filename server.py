import os
import httpx
from fastapi import FastAPI
from fastmcp import FastMCP, expose_fastapi_app

BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY")

# Create MCP instance
mcp = FastMCP(name="brightdata-mcp")

# Register MCP Tool
@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a URL using BrightData Web Unlocker."""
    if not BRIGHT_DATA_API_KEY:
        return "Missing BRIGHT_DATA_API_KEY"

    headers = {"Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"}
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.brightdata.com/webunlocker/v1/uncategorized",
            headers=headers,
            json=payload
        )
        r.raise_for_status()
        return r.text


# FastAPI app
app = FastAPI()

# Expose the MCP server correctly (REQUIRED BY FASTMCP 2.13.1)
expose_fastapi_app(app, mcp)


@app.get("/")
async def root():
    return {"status": "ok", "tools": list(mcp._tools.keys())}
