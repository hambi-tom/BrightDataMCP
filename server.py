import os
import json
import asyncio
import requests

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastmcp import FastMCP
import uvicorn

# ============================================================
# BRIGHTDATA MCP ENV VARS
# ============================================================
BRIGHTDATA_MCP_POST = os.getenv("BRIGHTDATA_MCP_POST")
BRIGHTDATA_MCP_SSE  = os.getenv("BRIGHTDATA_MCP_SSE")
BRIGHTDATA_MCP_TOKEN = os.getenv("BRIGHTDATA_MCP_TOKEN")

if not (BRIGHTDATA_MCP_POST and BRIGHTDATA_MCP_SSE and BRIGHTDATA_MCP_TOKEN):
    raise RuntimeError("Missing BrightData MCP environment variables")

HEADERS = { "Authorization": f"Bearer {BRIGHTDATA_MCP_TOKEN}" }

# ============================================================
# SETUP FASTAPI + MCP SERVER
# ============================================================
app = FastAPI()
mcp = FastMCP(name="BrightData Universal MCP Proxy")

# ============================================================
# REQUIRED: /healthz (for Render)
# ============================================================
@app.get("/healthz")
async def health_check():
    return PlainTextResponse("ok", status_code=200)

# ============================================================
# REQUIRED: GET /
# ============================================================
@app.get("/")
async def root():
    return JSONResponse({
        "name": mcp.name,
        "version": "1.0.0",
        "protocol": "2024-11-06",
        "tools": [
            {"name": t.name, "description": t.description or ""}
            for t in mcp.tools
        ]
    })

# ============================================================
# REQUIRED: POST /sse  → MUST RETURN 200 (CHATGPT CHECK)
# ============================================================
@app.post("/sse")
async def post_sse(_: Request):
    return PlainTextResponse("OK", status_code=200)

# ============================================================
# REQUIRED: GET /sse  (actual SSE transport)
# ============================================================
@app.get("/sse")
async def get_sse(request: Request):
    return await mcp.handle_sse(request)

# ============================================================
# REQUIRED: POST /messages/?session_id=xxx
# ============================================================
@app.post("/messages/")
async def post_messages(session_id: str, request: Request):
    body = await request.json()
    return await mcp.handle_message(session_id, body)

# ============================================================
# BRIGHTDATA PROXY CALL
# ============================================================
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
        headers=HEADERS,
        json=payload,
        timeout=60
    )
    return r.text

# ============================================================
# TOOLS
# ============================================================
@mcp.tool()
def ping() -> str:
    return "pong"

@mcp.tool()
def search_engine(query: str) -> str:
    return call_brightdata_tool("search_engine", {"query": query})

@mcp.tool()
def scrape_as_markdown(url: str) -> str:
    return call_brightdata_tool("scrape_as_markdown", {"url": url})

@mcp.tool()
def search_engine_batch(queries: list[str]) -> str:
    return call_brightdata_tool("search_engine_batch", {"queries": queries})

@mcp.tool()
def scrape_batch(urls: list[str]) -> str:
    return call_brightdata_tool("scrape_batch", {"urls": urls})

# ============================================================
# START SERVER
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
