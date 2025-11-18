import os
from fastmcp import FastMCP
from mcp import ClientSession
from mcp.client.sse import sse_client

# Get the BrightData MCP SSE URL from environment
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

# -----------------------
# Utility: Connect to BrightData MCP via SSE
# -----------------------
async def call_brightdata(tool: str, arguments: dict):
    """
    Call BrightData MCP server via their hosted SSE endpoint
    """
    async with sse_client(BRIGHTDATA_MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool, arguments)
            return result.content

# -----------------------
# Tools exposed to ChatGPT
# -----------------------
@server.tool()
def ping() -> str:
    """Simple ping to test server connectivity"""
    return "pong"

@server.tool()
async def search_engine(query: str) -> list:
    """
    Search the web using BrightData's search engine.
    
    Args:
        query: The search query string
    """
    return await call_brightdata("search_engine", {"query": query})

@server.tool()
async def scrape_as_markdown(url: str) -> list:
    """
    Scrape a webpage and return its content as markdown.
    
    Args:
        url: The URL to scrape
    """
    return await call_brightdata("scrape_as_markdown", {"url": url})

@server.tool()
async def search_engine_batch(queries: list[str]) -> list:
    """
    Perform multiple searches in batch.
    
    Args:
        queries: List of search query strings
    """
    return await call_brightdata("search_engine_batch", {"queries": queries})

@server.tool()
async def scrape_batch(urls: list[str]) -> list:
    """
    Scrape multiple URLs in batch.
    
    Args:
        urls: List of URLs to scrape
    """
    return await call_brightdata("scrape_batch", {"urls": urls})

# -----------------------
# Run the MCP server
# -----------------------
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
