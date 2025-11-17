from fastmcp import FastMCP
import uvicorn

# Create MCP server
server = FastMCP(name="BrightData MCP")

# Simple tool
@server.tool()
def ping():
    """Test tool"""
    return "pong"

# Start server
if __name__ == "__main__":
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8000
    )
