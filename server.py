import os
import httpx
from fastmcp import FastMCP

BRIGHT_DATA_API_KEY = os.environ.get("BRIGHT_DATA_API_KEY")

# Create MCP server
mcp = FastMCP("brightdata-mcp")


@mcp.tool()
async def fetch_url(url: str) -> str:
    """Fetch a URL using Bright Data Web Unlocker."""
    if not BRIGHT_DATA_API_KEY:
        return "Missing BRIGHT_DATA_API_KEY"

    headers = {"Authorization": f"Bearer {BRIGHT_DATA_API_KEY}"}
    payload = {"url": url}

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.brightdata.com/webunlocker/v1/uncategorized",
            headers=headers,
            json=payload,
        )
        r.raise_for_status()
        return r.text


if __name__ == "__main__":
    # Render injects PORT – default to 8000 if not set (local runs)
    port = int(os.environ.get("PORT", "8000"))
    # Run as SSE server on /
    mcp.run(transport="sse", host="0.0.0.0", port=port)
