import os
import requests
from fastmcp import FastMCP

# Load secret Bright Data MCP URL
# IMPORTANT: Ensure this environment variable is set on Render!
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    # This will cause a quick, visible failure if the environment variable is missing
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")


server = FastMCP(name="BrightData Universal MCP Proxy")


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


# Expose the internal FastAPI app object for Uvicorn to run directly
app = server.app
