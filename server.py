import os
from fastmcp import FastMCP
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")

# Create MCP server
server = FastMCP(
    name="BrightData Universal MCP Proxy",
)

# Add CORS middleware so ChatGPT accepts the connector
server.app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple test tool
@server.tool()
def ping():
    """Ping test"""
    return "pong"

# Start server
if __name__ == "__main__":
    uvicorn.run(
        server.app,  # ← THIS IS CORRECT
        host="0.0.0.0",
        port=8000,
    )
