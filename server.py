import os
from fastmcp import FastMCP
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Load API key (you will need this later)
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")

# Create server using FastMCP v2.x (NO transport, NO server_url)
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

# Add CORS (mandatory for ChatGPT MCP Connectors)
server.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test tool
@server.tool()
def ping():
    """Health check tool."""
    return "pong"


# Start the server normally — FastMCP handles the MCP layer internally
if __name__ == "__main__":
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000
    )
