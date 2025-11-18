import os
import requests
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.integrations.fastapi import mount_fastmcp
import uvicorn

BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

# Your MCP server
mcp = FastMCP(name="BrightData Universal MCP Proxy")

# -----------------------
# Required MCP routes
# -----------------------

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "server": "BrightData MCP Proxy"}

@app.get("/healthz")
def health():
    return {"ok": True}

# Mount FastMCP on /sse and /messages
mount_fastmcp(app, mcp)


# -----------------------
# Tools
# -----------------------

@mcp.tool()
def ping() -> str:
    return "pong"

def wrap(result: str):
    return {
        "type": "result",
        "content": [{"type": "text", "text": result}]
    }

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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

@mcp.tool()
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


# -----------------------
# Start server
# -----------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
