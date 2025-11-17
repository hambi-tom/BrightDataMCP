{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import logging\
import os\
from typing import Dict, List, Any\
\
from fastmcp import FastMCP\
from openai import OpenAI\
\
# Logging\
logging.basicConfig(level=logging.INFO)\
logger = logging.getLogger(__name__)\
\
# Env vars\
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")\
VECTOR_STORE_ID = os.environ.get("VECTOR_STORE_ID", "")\
\
openai_client = OpenAI(api_key=OPENAI_API_KEY)\
\
server_instructions = """\
This MCP server provides search and document retrieval capabilities\
for chat and deep research connectors. Use the search tool to find relevant documents\
based on keywords, then use the fetch tool to retrieve complete\
document content with citations.\
"""\
\
def create_server():\
    mcp = FastMCP(\
        name="My MCP Bridge",\
        instructions=server_instructions,\
    )\
\
    @mcp.tool()\
    async def search(query: str) -> Dict[str, List[Dict[str, Any]]]:\
        """\
        Search for documents using OpenAI Vector Store search.\
        """\
        if not query or not query.strip():\
            return \{"results": []\}\
\
        if not OPENAI_API_KEY:\
            raise ValueError("OPENAI_API_KEY env var is required")\
\
        logger.info(f"Searching vector store \{VECTOR_STORE_ID\} for query: '\{query\}'")\
\
        response = openai_client.vector_stores.search(\
            vector_store_id=VECTOR_STORE_ID,\
            query=query,\
        )\
\
        results: List[Dict[str, Any]] = []\
\
        if getattr(response, "data", None):\
            for i, item in enumerate(response.data):\
                item_id = getattr(item, "file_id", f"vs_\{i\}")\
                item_filename = getattr(item, "filename", f"Document \{i+1\}")\
\
                content_list = getattr(item, "content", [])\
                text_content = ""\
                if content_list:\
                    first_content = content_list[0]\
                    if hasattr(first_content, "text"):\
                        text_content = first_content.text\
                    elif isinstance(first_content, dict):\
                        text_content = first_content.get("text", "")\
\
                if not text_content:\
                    text_content = "No content available"\
\
                snippet = text_content[:200] + "..." if len(text_content) > 200 else text_content\
\
                result = \{\
                    "id": item_id,\
                    "title": item_filename,\
                    "text": snippet,\
                    "url": f"https://platform.openai.com/storage/files/\{item_id\}",\
                \}\
                results.append(result)\
\
        logger.info(f"Search returned \{len(results)\} results")\
        return \{"results": results\}\
\
    @mcp.tool()\
    async def fetch(id: str) -> Dict[str, Any]:\
        """\
        Fetch full document contents by file ID from the vector store.\
        """\
        if not id:\
            raise ValueError("Document ID is required")\
\
        if not OPENAI_API_KEY:\
            raise ValueError("OPENAI_API_KEY env var is required")\
\
        logger.info(f"Fetching content for file ID: \{id\}")\
\
        content_response = openai_client.vector_stores.files.content(\
            vector_store_id=VECTOR_STORE_ID,\
            file_id=id,\
        )\
\
        file_info = openai_client.vector_stores.files.retrieve(\
            vector_store_id=VECTOR_STORE_ID,\
            file_id=id,\
        )\
\
        file_content = ""\
        if getattr(content_response, "data", None):\
            parts = []\
            for content_item in content_response.data:\
                if hasattr(content_item, "text"):\
                    parts.append(content_item.text)\
            file_content = "\\n".join(parts)\
        else:\
            file_content = "No content available"\
\
        filename = getattr(file_info, "filename", f"Document \{id\}")\
\
        result = \{\
            "id": id,\
            "title": filename,\
            "text": file_content,\
            "url": f"https://platform.openai.com/storage/files/\{id\}",\
            "metadata": None,\
        \}\
\
        if getattr(file_info, "attributes", None):\
            result["metadata"] = file_info.attributes\
\
        logger.info(f"Fetched file: \{id\}")\
        return result\
\
    return mcp\
\
\
def main():\
    if not OPENAI_API_KEY:\
        raise ValueError("OPENAI_API_KEY env var is required")\
\
    logger.info(f"Using vector store: \{VECTOR_STORE_ID\}")\
    server = create_server()\
\
    logger.info("Starting MCP server on 0.0.0.0:8000 (SSE transport)")\
    server.run(transport="sse", host="0.0.0.0", port=8000)\
\
\
if __name__ == "__main__":\
    main()\
}