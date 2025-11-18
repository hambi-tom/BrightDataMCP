import os
import asyncio
from fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters

BRIGHTDATA_MCP_URL = os.getenv("BRIGHTDATA_MCP_URL")
if not BRIGHTDATA_MCP_URL:
    raise RuntimeError("BRIGHTDATA_MCP_URL environment variable is missing!")


server = FastMCP(
    name="BrightData Universal MCP Proxy"
)


# -----------------------
# Utility: connect to Bright Data MCP
# -----------------------
async def call_brightdata(tool: str, arguments: dict):

    async with ClientSession(
        name="brightdata-proxy",
        transport="sse",
        url=BRIGHTDATA_MCP_URL,
        server_params=StdioServerParameters(),
    ) as session:

        result = await session.call_tool(tool, arguments)
        return result.output
        

# -----------------------
# Tools exposed to ChatGPT
# -----------------------
@server.tool()
def ping() -> str:
    return "pong"


@server.tool()
async def search_engine(query: str):
    return await call_brightdata("search_engine", {"query": query})


@server.tool()
async def scrape_as_markdown(url: str):
    return await call_brightdata("scrape_as_markdown", {"url": url})


@server.tool()
async def search_engine_batch(queries: list[str]):
    return await call_brightdata("search_engine_batch", {"queries": queries})


@server.tool()
async def scrape_batch(urls: list[str]):
    return await call_brightdata("scrape_batch", {"urls": urls})


# -----------------------
# Run the MCP server
# -----------------------
if __name__ == "__main__":
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )
