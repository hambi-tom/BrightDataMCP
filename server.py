import os
from fastmcp import FastMCP
from langchain_brightdata import (
    BrightDataSERP,
    BrightDataUnlocker,
    BrightDataWebScraperAPI,
)

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------

BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
if not BRIGHT_DATA_API_KEY:
    raise RuntimeError(
        "BRIGHT_DATA_API_KEY environment variable is not set. "
        "Add it in your Render service settings."
    )

# Create the FastMCP server
server = FastMCP("BrightData Universal MCP Proxy")

# Create Bright Data tool clients (reused by our MCP tools)
serp_client = BrightDataSERP(bright_data_api_key=BRIGHT_DATA_API_KEY)
unlocker_client = BrightDataUnlocker(bright_data_api_key=BRIGHT_DATA_API_KEY)
scraper_client = BrightDataWebScraperAPI(bright_data_api_key=BRIGHT_DATA_API_KEY)

# -------------------------------------------------------
# TOOLS
# -------------------------------------------------------

@server.tool()
def ping() -> str:
    """Simple connectivity test."""
    return "pong"


@server.tool()
def search_engine(
    query: str,
    search_engine: str = "google",
    country: str = "us",
    language: str = "en",
    results_count: int = 10,
    search_type: str | None = None,
    device_type: str | None = None,
    parse_results: bool = False,
):
    """
    Run a Bright Data SERP search.

    Parameters roughly match BrightDataSERP:
    - query: search query
    - search_engine: e.g. 'google'
    - country: 2-letter country code, e.g. 'us', 'gb'
    - language: 2-letter language code, e.g. 'en', 'de'
    - results_count: number of results
    - search_type: None, 'isch', 'shop', 'nws', 'jobs'
    - device_type: None, 'mobile', 'ios', 'android'
    - parse_results: if True, return structured JSON where possible
    """
    params = {
        "query": query,
        "search_engine": search_engine,
        "country": country,
        "language": language,
        "results_count": results_count,
        "search_type": search_type,
        "device_type": device_type,
        "parse_results": parse_results,
    }
    # Drop None values so we only send what’s set
    params = {k: v for k, v in params.items() if v is not None}
    return serp_client.invoke(params)


@server.tool()
def unlock_url(
    url: str,
    country: str | None = None,
    data_format: str | None = "markdown",
    zone: str | None = "unblocker",
):
    """
    Fetch a URL through Bright Data Unlocker.

    - url: page to fetch
    - country: 2-letter code for geo-routing (optional)
    - data_format: None (HTML), 'markdown', or 'screenshot'
    - zone: Bright Data zone to use (default 'unblocker')
    """
    params = {
        "url": url,
        "country": country,
        "data_format": data_format,
        "zone": zone,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return unlocker_client.invoke(params)


@server.tool()
def scrape_structured(
    url: str,
    dataset_type: str,
    zipcode: str | None = None,
):
    """
    Use Bright Data Web Scraper API to get structured data.

    Examples of dataset_type:
    - 'amazon_product'
    - 'amazon_product_reviews'
    - 'linkedin_person_profile'
    - 'linkedin_company_profile'
    """
    params = {
        "url": url,
        "dataset_type": dataset_type,
        "zipcode": zipcode,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return scraper_client.invoke(params)


# -------------------------------------------------------
# START THE SERVER
# -------------------------------------------------------

if __name__ == "__main__":
    # FastMCP will start an SSE server on port 8000
    server.run()
