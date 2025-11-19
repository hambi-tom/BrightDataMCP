import os
import requests
from fastmcp import FastMCP
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import Request

# ---------------------------------------------------------
# Load BrightData MCP Server URL (must include token)
# ---------------------------------------------------------
BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")

if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")

# ---------------------------------------------------------
# Create MCP Server
# ---------------------------------------------------------
server = FastMCP(
    name="BrightData Universal MCP Proxy"
)

app = server.app   # FastAPI instance underlying FastMCP


# ---------------------------------------------------------
# Required MCP Metadata Endpoint (root)
# ChatGPT calls GET / to validate the connector’s safety.
# ---------------------------------------------------------
@app.get("/")
async def root():
    """
    ChatGPT calls this during connector validation.
    MUST return 200 and MCP metadata.
    """
    metadata = {
        "name": server.name,
        "version": "1.0.0",
        "protocol": "2024-11-06",
        "tools": []
    }

    # Populate with your tool definitions
    for tool in server.tools:
        metadata["tools"].append({
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.input_model.schema() if tool.input_model else {}
        })

    return JSONResponse(metadata)


# ---------------------------------------------------------
# REQUIRED: POST /sse for ChatGPT MCP handshake
#
# ChatGPT validation sends:
#   POST /sse     (validation)
#   GET  /sse     (actual SSE stream)
#
# FastMCP only implements GET /sse internally,
# so we must add this POST handler manually.
# ---------------------------------------------------------
@app.post("/sse")
async def post_sse(_: Request):
    return PlainTextResponse("OK", status_code=200)


# ---------------------------------------------------------
# Simple ping tool
# ---------------------------------------------------------
@server.tool()
def ping() -> str:
    return "pong"


# ---------------------------------------------------------
# BrightData Tool Proxies
# ---------------------------------------------------------
def call_brightdata_tool(tool_name: str, args: dict):
    """
    Common wrapper for calling BrightData MCP endpoint.
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
    r.raise_for_status()
    return r.text


@server.tool()
def search_engine(query: str) -> str:
    return call_brightdata_tool("search_engine", {"query": query})


@server.tool()
def scrape_as_markdown(url: str) -> str:
    return call_brightdata_tool("scrape_as_markdown", {"url": url})


@server.tool()
def search_engine_batch(queries: list[str]) -> str:
    return call_brightdata_tool("search_engine_batch", {"queries": queries})


@server.tool()
def scrape_batch(urls: list[str]) -> str:
    return call_brightdata_tool("scrape_batch", {"urls": urls})


# ---------------------------------------------------------
# Run Server (SSE transport required)
# ---------------------------------------------------------
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
