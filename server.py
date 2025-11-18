import os
from fastmcp import FastMCP
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# -------------------------------------------------------
# LOAD ENV VARIABLES
# -------------------------------------------------------
BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
if not BRIGHT_DATA_API_KEY:
    raise RuntimeError(
        "BRIGHT_DATA_API_KEY environment variable is not set. "
        "Add it in Render → Environment → Add Env Var."
    )

BRIGHTDATA_API_BASE = "https://api.brightdata.com"


# -------------------------------------------------------
# INIT SERVER (SSE TRANSPORT FOR RENDER)
# -------------------------------------------------------
server = FastMCP(
    name="BrightData Universal MCP Proxy",
    transport="sse",
)


# -------------------------------------------------------
# CORS FIX (REQUIRED FOR CHATGPT)
# -------------------------------------------------------
server.fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# BASIC PING TOOL
# -------------------------------------------------------
@server.tool()
def ping():
    """Simple ping to verify MCP server works."""
    return "pong"


# -------------------------------------------------------
# EXAMPLE — Bright Data Tool: List Proxies
# -------------------------------------------------------
import requests

@server.tool()
def list_proxies():
    """List all Bright Data proxies."""
    url = f"{BRIGHTDATA_API_BASE}/proxies"
    headers = {"Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"}

    resp = requests.get(url, headers=headers)
    return resp.json()


# -------------------------------------------------------
# START SERVER (REQUIRED FOR RENDER)
# -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        server.fastapi,   # ← MUST BE fastapi
        host="0.0.0.0",
        port=8000,
        headers=[("Access-Control-Allow-Origin", "*")],
    )
