import os
import requests
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastmcp import FastMCP
import uvicorn

BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("Missing BRIGHTDATA_MCP_URL env variable")

# ------------------------------
# FastMCP server
# ------------------------------
mcp = FastMCP(name="BrightData Universal MCP Proxy")

@mcp.tool()
def ping() -> str:
    return "pong"


def call_bd(tool, args):
    payload = {
        "type": "message",
        "body": {
            "type": "callTool",
            "name": tool,
            "arguments": args
        }
    }
    r = requests.post(BRIGHTDATA_MCP_URL, json=payload)
    return r.text


@mcp.tool()
def search_engine(query: str):
    return call_bd("search_engine", {"query": query})

@mcp.tool()
def scrape_as_markdown(url: str):
    return call_bd("scrape_as_markdown", {"url": url})

@mcp.tool()
def search_engine_batch(queries: list[str]):
    return call_bd("search_engine_batch", {"queries": queries})

@mcp.tool()
def scrape_batch(urls: list[str]):
    return call_bd("scrape_batch", {"urls": urls})


# ------------------------------
# FastAPI wrapper — makes it SAFE
# ------------------------------
app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "server": "BrightData MCP Proxy"}

@app.get("/healthz")
def health():
    return {"ok": True}


# ------------------------------
# Proxy /sse → FastMCP SSE server
# ------------------------------
@app.get("/sse")
async def sse(request: Request):
    # Forward to FastMCP internal SSE generator
    generator = mcp.sse_handler()

    async def event_stream():
        async for event in generator:
            yield f"data: {event}\n\n"

    return Response(event_stream(), media_type="text/event-stream")


# ------------------------------
# Proxy /messages → FastMCP
# ------------------------------
@app.post("/messages/")
async def messages(request: Request):
    body = await request.json()
    response = await mcp.process_message(body)
    return JSONResponse(response)


# ------------------------------
# Run server
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
