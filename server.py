import os
from fastmcp import FastMCP
import uvicorn

# IMPORTANT:
# Put your BrightData API key into Render environment variables:
# BRIGHTDATA_API_KEY = "your-key-here"

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")

server = FastMCP(
    name="BrightData Universal MCP Proxy",
    transport="sse",

    # This MUST match your Render public URL
    server_url="https://brightdatamcp.onrender.com/sse",
)

# -------------------------------------------------------
# EXAMPLE TOOL — you can add more later
# -------------------------------------------------------
@server.tool()
def ping():
    """Simple ping test."""
    return "pong"


# -------------------------------------------------------
# START THE SERVER
# -------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000,

        # REQUIRED FOR CHATGPT TO ACCEPT YOUR SERVER
        headers=[("Access-Control-Allow-Origin", "*")],
    )
