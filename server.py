import os
import requests

from fastmcp import FastMCP
from fastmcp import expose_fastapi_app  # NEW for FastMCP 2.x
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi import Request

# ----------------------------------------------------------
# Environment Variables
# ----------------------------------------------------------
BRIGHTDATA_MCP_POST = os.getenv("BRIGHTDATA_MCP_POST")
BRIGHTDATA_MCP_SSE = os.getenv("BRIGHTDATA_MCP_SSE")
BRIGHTDATA_MCP_TOKEN = os.getenv("BRIGHTDATA_MCP_TOKEN")

if not BRIGHTDATA_MCP_POST or not BRIGHTDATA_MCP_SSE or not BRIGHTDATA_MCP_TOKEN:
    raise RuntimeError("Missing BrightData MCP environment variables")

HEADERS = {
    "Authorization": f"Bearer {BRIGHTDATA_MCP_TOKEN}"
}

# ----------------------------------------------------------
# Create MCP Server
# ----------------------------------------------------------
server = FastMCP(name="BrightData Universal MCP Proxy")

# ----------------------------------------------------------
# Bind FastAPI to FastMCP (FIX FOR v2.13+)
# ----------------------------------------------------------
app = expose_fastapi_app(server)


# ----------------------------------------------------------
# REQUIRED: GET /
# ----------------------------------------------------------
@app.get("/")
async def root():
    metadata = {
        "name": server.name,
        "version": "1.0.0",
        "protocol": "2024-11-06",
        "tools": []
    }

    for tool in server.tools:
        metadata["tools"].append({
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.input_model.schema() if tool.input_model else {}
        })

    return JSONResponse(metadata)


# ----------------------------------------------------------
# REQUIRED: POST /sse
# ----------------------------------------------------------
@app.post("/sse")
async def post_sse(_: Request):
    return PlainTextResponse("OK", status_code=200)


# ----------------------------------------------------------
# Simple ping tool
# ----------------------------------------------------------
@server.tool()
def ping() -> str:
    return "pong"


# ----------------------------------------------------------
# BrightData Proxy
# ----------------------------------------------------------
def call_brightdata_tool(tool_name: str, args: dict):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": tool_name,
            "arguments": args
        }
    }

    r = requests.post(
        BRIGHTDATA_MCP_POST,
        json=payload,
        headers=HEADERS
    )
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


# ----------------------------------------------------------
# Run Server (SSE transport)
# ----------------------------------------------------------
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
