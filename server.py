import os
import requests
from fastmcp import FastMCP
from fastapi import FastAPI

# Load secret Bright Data MCP URL
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

# Create FastMCP server
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

# Attach FastAPI app (needed for custom routes like /healthz)
app: FastAPI = server.app


# ------------------------
# HEALTH CHECK ENDPOINT
# ------------------------
@app.get("/healthz")
async def health_check():
    return {"ok": True}


# ------------------------
# HELPER – FORWARD REQUESTS TO BRIGHT DATA MCP
# ------------------------
def forward_to_brightdata(tool_name: str, arguments: dict):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": tool_name,
            "arguments": arguments,
        },
    }

    try:
        response = requests.post(
            BRIGHTDATA_MCP_URL,
            json=payload,
            timeout=30  # important: avoid Render restart
        )
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Bright Data MCP error: {e}"


# ------------------------
# TOOLS
# ------------------------
@server.tool()
def ping() -> str:
    return "pong"


@server.tool()
def search_engine(query: str) -> str:
    return forward_to_brightdata("search_engine", {"query": query})


@server.tool()
def scrape_as_markdown(url: str) -> str:
    return forward_to_brightdata("scrape_as_markdown", {"url": url})


@server.tool()
def search_engine_batch(queries: list[str]) -> str:
    return forward_to_brightdata("search_engine_batch", {"queries": queries})


@server.tool()
def scrape_batch(urls: list[str]) -> str:
    return forward_to_brightdata("scrape_batch", {"urls": urls})


# ------------------------
# RUN SERVER
# ------------------------
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000,
        path="/mcp"   # IMPORTANT: your new SSE endpoint
    )
