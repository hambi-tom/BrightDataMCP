import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sse_starlette.sse import EventSourceResponse
from fastmcp import FastMCP

BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY")


# Create MCP engine
mcp = FastMCP(name="brightdata-mcp")


# Tool registration (FASTMCP 2.13.1 compatible)
@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a URL using BrightData Web Unlocker."""
    if not BRIGHT_DATA_API_KEY:
        return "Missing BRIGHT_DATA_API_KEY"

    headers = {"Authorization": f"Bearer " + BRIGHT_DATA_API_KEY}
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.brightdata.com/webunlocker/v1/uncategorized",
            headers=headers,
            json=payload
        )
        r.raise_for_status()
        return r.text


# ---------- FASTAPI APP ----------
app = FastAPI()


@app.get("/")
async def root():
    return {"status": "ok", "tools": list(mcp._tools.keys())}


@app.get("/healthz")
async def health():
    return PlainTextResponse("OK", status_code=200)


# ---------- SSE ENDPOINTS (Bypass fastmcp wrappers) ----------
# ChatGPT *requires* GET and POST for /sse


async def mcp_event_generator():
    # Core MCP event generator.
    # This uses the FastMCP ASGI interface internally.
    async for event in mcp.run_sse():
        yield event


@app.get("/sse")
async def sse_get(request: Request):
    return EventSourceResponse(mcp_event_generator())


@app.post("/sse")
async def sse_post(request: Request):
    return EventSourceResponse(mcp_event_generator())
