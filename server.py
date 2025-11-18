import os
import logging
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the BrightData MCP SSE URL from environment
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

logger.info(f"BrightData MCP URL configured: {BRIGHTDATA_MCP_URL[:50]}...")

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
    try:
        from mcp import ClientSession
        from mcp.client.sse import sse_client
        
        logger.info(f"Calling BrightData tool: {tool} with args: {arguments}")
        
        async with sse_client(BRIGHTDATA_MCP_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                logger.info(f"Session initialized for tool: {tool}")
                
                result = await session.call_tool(tool, arguments)
                logger.info(f"Tool {tool} completed successfully")
                
                # Return the content
                if hasattr(result, 'content'):
                    return result.content
                return result
                
    except Exception as e:
        logger.error(f"Error calling BrightData tool {tool}: {str(e)}", exc_info=True)
        return {"error": str(e), "tool": tool}

# -----------------------
# Tools exposed to ChatGPT
# -----------------------
@server.tool()
def ping() -> str:
    """Simple ping to test server connectivity"""
    logger.info("Ping called - server is alive!")
    return "pong - BrightData MCP Proxy is running"

@server.tool()
async def search_engine(query: str) -> str:
    """
    Search the web using BrightData's search engine.
    
    Args:
        query: The search query string
    """
    try:
        logger.info(f"search_engine called with query: {query}")
        result = await call_brightdata("search_engine", {"query": query})
        return str(result)
    except Exception as e:
        logger.error(f"search_engine error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

@server.tool()
async def scrape_as_markdown(url: str) -> str:
    """
    Scrape a webpage and return its content as markdown.
    
    Args:
        url: The URL to scrape
    """
    try:
        logger.info(f"scrape_as_markdown called with url: {url}")
        result = await call_brightdata("scrape_as_markdown", {"url": url})
        return str(result)
    except Exception as e:
        logger.error(f"scrape_as_markdown error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

@server.tool()
async def search_engine_batch(queries: list[str]) -> str:
    """
    Perform multiple searches in batch.
    
    Args:
        queries: List of search query strings
    """
    try:
        logger.info(f"search_engine_batch called with {len(queries)} queries")
        result = await call_brightdata("search_engine_batch", {"queries": queries})
        return str(result)
    except Exception as e:
        logger.error(f"search_engine_batch error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

@server.tool()
async def scrape_batch(urls: list[str]) -> str:
    """
    Scrape multiple URLs in batch.
    
    Args:
        urls: List of URLs to scrape
    """
    try:
        logger.info(f"scrape_batch called with {len(urls)} urls")
        result = await call_brightdata("scrape_batch", {"urls": urls})
        return str(result)
    except Exception as e:
        logger.error(f"scrape_batch error: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

# -----------------------
# Run the MCP server
# -----------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting BrightData MCP Proxy on port {port}")
    logger.info(f"All tools registered: ping, search_engine, scrape_as_markdown, search_engine_batch, scrape_batch")
    
    try:
        server.run(
            transport="sse",
            host="0.0.0.0",
            port=port
        )
    except Exception as e:
        logger.error(f"Server failed to start: {str(e)}", exc_info=True)
        raise
