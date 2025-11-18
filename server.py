import os
import requests
from fastmcp import FastMCP

# Load secret Bright Data MCP URL (with token inside it)
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")

if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")


# Create MCP server
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)


# ---- Simple ping ----
@server.tool()
def ping() -> str:
    return "pong"


# ---- Helper: wrap responses in valid MCP format ----
def wrap(result_text: str):
    return {
        "type": "result",
        "content": [
            {
                "type": "text",
                "text": result_text
            }
        ]
    }


# ---- Bright Data: search_engine ----
@server.tool()
def search_engine(query: str):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "search_engine",
            "arguments": {"query": query}
        }
    }
    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)
    return wrap(r.text)


# ---- Bright Data: scrape_as_markdown ----
@server.tool()
def scrape_as_markdown(url: str):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "scrape_as_markdown",
            "arguments": {"url": url}
        }
    }
    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)
    return wrap(r.text)


# ---- Bright Data: search_engine_batch ----
@server.tool()
def search_engine_batch(queries: list[str]):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "search_engine_batch",
            "arguments": {"queries": queries}
        }
    }
    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)
    return wrap(r.text)


# ---- Bright Data: scrape_batch ----
@server.tool()
def scrape_batch(urls: list[str]):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": "scrape_batch",
            "arguments": {"urls": urls}
        }
    }
    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)
    return wrap(r.text)


# ---- Run server (same as yesterday) ----
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
