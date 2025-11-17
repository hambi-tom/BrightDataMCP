import os
import json
import logging
from typing import Dict, Any, List

from fastmcp import FastMCP
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("brightdata-mcp")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
BRIGHTDATA_MCP_URL = os.environ.get("BRIGHTDATA_MCP_URL")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY")

if not BRIGHTDATA_MCP_URL:
    raise ValueError("Missing BRIGHTDATA_MCP_URL")

client = OpenAI(api_key=OPENAI_API_KEY)

instructions = """
This MCP server forwards ALL requests to BrightData’s MCP.
You may use any BrightData tool: search_engine, scrape_as_markdown,
search_engine_batch, scrape_batch, or any others.

- Use the `search` tool for initial discovery/search queries.
- Use the `fetch` tool for detailed scraping, rendering, batch jobs,
  or any BrightData sub-tool.

This server simply proxies BrightData tools to ChatGPT.
"""


def create_server():
    mcp = FastMCP(
        name="BrightData Universal MCP Proxy",
        instructions=instructions
    )

    # -------------------------------------------------------------------
    # UNIVERSAL SEARCH
    # -------------------------------------------------------------------
    @mcp.tool()
    async def search(query: str, tool: str = "search_engine") -> Dict[str, Any]:
        """
        Universal Search wrapper.
        Uses BrightData search_engine or search_engine_batch depending on user choice.

        Args:
            query: text to search
            tool: which BrightData tool to use ("search_engine", "search_engine_batch")
        """

        logger.info(f"search() called: query={query}, tool={tool}")

        if tool not in ["search_engine", "search_engine_batch"]:
            raise ValueError("Invalid search tool")

        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"Use BrightData tool `{tool}` with query: {query}",
            tools=[{
                "type": "mcp",
                "server_label": "brightdata",
                "server_url": BRIGHTDATA_MCP_URL,
                "allowed_tools": [
                    "search_engine",
                    "search_engine_batch",
                ],
                "require_approval": "never"
            }],
            reasoning={"effort": "low"}
        )

        results = []
        for out in response.output:
            if out.type != "tool_result":
                continue

            try:
                data = json.loads(out.content[0].text)
            except:
                continue

            for item in data.get("results", []):
                url = item.get("url") or item.get("link") or ""
                title = item.get("title") or url

                results.append({
                    "id": url,
                    "title": title,
                    "url": url
                })

        return {"results": results}

    # -------------------------------------------------------------------
    # UNIVERSAL FETCH
    # -------------------------------------------------------------------
    @mcp.tool()
    async def fetch(
        id: str,
        tool: str = "scrape_as_markdown",
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Universal BrightData fetch wrapper.

        Args:
            id: usually a URL
            tool: ANY BrightData MCP tool:
                - scrape_as_markdown
                - scrape_batch
                - search_engine
                - search_engine_batch
                - (ALL FUTURE TOOLS SUPPORTED)
            params: extra arguments passed to the BrightData tool
        """

        logger.info(f"fetch() called: id={id}, tool={tool}, params={params}")

        if params is None:
            params = {}

        # Build tool input
        tool_input = {
            "url": id,
            **params
        }

        response = client.responses.create(
            model="gpt-4o-mini",
            input=f"Use BrightData tool `{tool}` with args: {tool_input}",
            tools=[{
                "type": "mcp",
                "server_label": "brightdata",
                "server_url": BRIGHTDATA_MCP_URL,
                "allowed_tools": [
                    "scrape_as_markdown",
                    "scrape_batch",
                    "search_engine",
                    "search_engine_batch"
                ],
                "require_approval": "never"
            }],
            reasoning={"effort": "low"}
        )

        full_text = ""

        for out in response.output:
            if out.type == "tool_result":
                try:
                    data = json.loads(out.content[0].text)
                    full_text += json.dumps(data, indent=2)
                except:
                    continue
            elif out.type == "output_text":
                full_text += out.text

        return {
            "id": id,
            "title": f"BrightData fetch via {tool}",
            "text": full_text,
            "url": id,
            "metadata": {"tool_used": tool}
        }

    return mcp


def main():
    logger.info("Starting BrightData universal MCP proxy server...")
    server = create_server()
    server.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )


if __name__ == "__main__":
    main()
