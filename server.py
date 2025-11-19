import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from sse_starlette.sse import EventSourceResponse
from fastmcp import FastMCP

BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY")

app = FastAPI()
mcp = FastMCP(name="brightdata-mcp")


@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a URL using BrightData Web Unlocker."""
    if not BRIGHT_DATA_API_KEY:
        return "Missing BRIGHT_DATA_API_KEY environment variable."

    headers = {"Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"}
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.brightdata.com/webunlocker/v1/uncategorized",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.text


@app.get("/")
async def root():
    return {"status": "ok", "server": "brightdata-mcp", "tools": list(mcp._tools.keys())}


@app.get("/healthz")
async def health():
    return PlainTextResponse("OK", status_code=200)


@app.get("/sse")
async def sse_get(request: Request):
    async def event_publisher():
        async for event in mcp.stream_sse():
            yield event
    return EventSourceResponse(event_publisher())


@app.post("/sse")
async def sse_post(request: Request):
    async def event_publisher():
        async for event in mcp.stream_sse():
            yield event
    return EventSourceResponse(event_publisher())
