import os
import requests
from fastmcp import FastMCP
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn

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
# Create MCP Server (tools only)
# ----------------------------------------------------------
mcp_server = FastMCP(name="BrightData Universal MCP Proxy")

# ----------------------------------------------------------
# Create separate FastAPI app
# ----------------------------------------------------------
app = FastAPI()

# ----------------------------------------------------------
# REQUIRED: GET /
# ----------------------------------------------------------
@app.get("/")
async def root():
    metadata = {
        "name": mcp_server.name,
        "version": "1.0.0",
        "protocol": "2024-11-06",
        "tools": []
    }

    for tool in mcp_server.tools:
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
# Bind MCP SSE route manually
# ----------------------------------------------------------
@app.get("/sse")
async def sse(request: Request):
    return await mcp_server.handle_sse(request)

# ----------------------------------------------------------
# Bind MCP messages endpoint
# ----------------------------------------------------------
@app.post("/messages/")
async def messages(session_id: str, request: Request):
    body = await request.json()
    return await mcp_server.handle_message(session_id, body)

# ----------------------------------------------------------
# Tools (proxied)
# ----------------------------------------------------------
@mcp_server.tool()
def ping() -> str:
    return "pong"

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

@mcp_server.tool()
def search_engine(query: str) -> str:
    return call_brightdata_tool("search_engine", {"query": query})

@mcp_server.tool()
def scrape_as_markdown(url: str) -> str:
    return call_brightdata_tool("scrape_as_markdown", {"url": url})

@mcp_server.tool()
def search_engine_batch(queries: list[str]) -> str:
    return call_brightdata_tool("search_engine_batch", {"queries": queries})

@mcp_server.tool()
def scrape_batch(urls: list[str]) -> str:
    return call_brightdata_tool("scrape_batch", {"urls": urls})

# ----------------------------------------------------------
# Uvicorn Server
# ----------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
