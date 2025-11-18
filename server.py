import os
import requests
from fastmcp import FastMCP

# Load secret Bright Data MCP URL
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")


server = FastMCP(name="BrightData Universal MCP Proxy")


@server.tool()
def ping() -> str:
    return "pong"


@server.tool()
def search_engine(query: str) -> str:
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
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
