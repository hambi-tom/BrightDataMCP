import os
import requests
from fastmcp import FastMCP
from starlette.responses import Response

# Load secret Bright Data MCP URL
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")


server = FastMCP(name="BrightData Universal MCP Proxy")

# The previous code to fix POST /sse is being removed because 'server.app' does not exist
# on your version of FastMCP, causing the deployment to fail.

@server.tool()
def ping() -> str:
    """A basic tool to check if the server is running."""
    return "pong"


@server.tool()
def search_engine(query: str) -> str:
    """Performs a search engine query via Bright Data MCP."""
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "search_engine",
            "arguments": {"query": query}
        }
    }
    return requests.post(BRIGHTDATA_MCP_URL, json=payload).text


@server.tool()
def scrape_as_markdown(url: str) -> str:
    """Scrapes a given URL and returns the content in Markdown format."""
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "scrape_as_markdown",
            "arguments": {"url": url}
        }
    }
    return requests.post(BRIGHTDATA_MCP_URL, json=payload).text


@server.tool()
def search_engine_batch(queries: list[str]) -> str:
    """Performs multiple search engine queries in a batch via Bright Data MCP."""
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "search_engine_batch",
            "arguments": {"queries": queries}
        }
    }
    return requests.post(BRIGHTDATA_MCP_URL, json=payload).text


@server.tool()
def scrape_batch(urls: list[str]) -> str:
    """Scrapes multiple URLs in a batch via Bright Data MCP."""
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "scrape_batch",
            "arguments": {"urls": urls}
        }
    }
    return requests.post(BRIGHTDATA_MCP_URL, json=payload).text


if __name__ == "__main__":
    server.run(
        transport="sse", # Must use SSE transport as required
        host="0.0.0.0",
        port=8000
    )
