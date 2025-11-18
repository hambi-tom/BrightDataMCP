import os
import requests
from fastmcp import FastMCP

BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

@server.tool()
def ping() -> str:
    return "pong"


def call_brightdata(tool_name: str, args: dict):
    """
    Bright Data requires POSTing MCP-formatted JSON to the SSE endpoint.
    We MUST wrap the result in valid MCP response format or FastMCP will ignore us.
    """

    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": tool_name,
            "arguments": args
        }
    }

    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)

    # IMPORTANT: wrap result so FastMCP accepts it
    return {
        "raw_response": r.text
    }


@server.tool()
def search_engine(query: str):
    return call_brightdata("search_engine", {"query": query})


@server.tool()
def scrape_as_markdown(url: str):
    return call_brightdata("scrape_as_markdown", {"url": url})


@server.tool()
def search_engine_batch(queries: list[str]):
    return call_brightdata("search_engine_batch", {"queries": queries})


@server.tool()
def scrape_batch(urls: list[str]):
    return call_brightdata("scrape_batch", {"urls": urls})


if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
