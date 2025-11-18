from fastmcp import FastMCP

# Create the MCP server
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

# Simple test tool so we know the server works
@server.tool()
def ping() -> str:
    """Simple ping test that confirms the MCP server is reachable."""
    return "pong"

# Start the MCP server with SSE transport on port 8000
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
