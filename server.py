import os
from fastmcp import FastMCP
from fastmcp.clients import MCPClient

# Create your MCP server
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

# Simple ping tool (same as before)
@server.tool()
def ping() -> str:
    """Simple ping test."""
    return "pong"


# ─────────────────────────────────────────────
# Connect to Bright Data MCP server
# ─────────────────────────────────────────────

BRIGHTDATA_URL = os.getenv("BRIGHTDATA_MCP_URL")

if not BRIGHTDATA_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing")

# Client connected to the official Bright Data MCP server
brightdata = MCPClient(
    url=BRIGHTDATA_URL,
    name="brightdata"
)

# Register Bright Data tools inside your server
server.mount_client(brightdata)


# ─────────────────────────────────────────────
# Start YOUR MCP server using SSE (same as yesterday)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
