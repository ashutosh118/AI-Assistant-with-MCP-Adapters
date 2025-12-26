from mcp.server.fastmcp import FastMCP
import aiohttp
import re
import os


print("Starting web_search_server.py")
mcp = FastMCP("WebSearch")

def normalize_query(query: str) -> str:
    # Remove excessive whitespace and special chars for URL safety
    return re.sub(r'\s+', ' ', query).strip()

@mcp.tool(name="web_search")
async def web_search(query: str) -> str:
    """
    Search the web for up-to-date information using DuckDuckGo Instant Answer API.
    If no relevant result is found, fallback to Google Search via SerpAPI.
    Use this tool for any real-world, current, or factual queries (e.g., latest prices, news, events, product info, etc.).
    Example queries:
    - "Search for the latest price of Mahindra Thar after new GST slab"
    - "Find recent news about AI regulation in India"
    - "Get the current weather in Paris"
    Input is normalized and debug logging is enabled.
    """
    try:
        norm_query = normalize_query(query)
        url = f"https://api.duckduckgo.com/?q={norm_query}&format=json&no_redirect=1&no_html=1"
        print(f"[WebSearch] Requesting: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"[WebSearch] HTTP status: {resp.status}")
                data = await resp.json()
                print(f"[WebSearch] API response: {data}")
                if 'AbstractText' in data and data['AbstractText']:
                    return data['AbstractText']
                elif 'RelatedTopics' in data and data['RelatedTopics']:
                    return data['RelatedTopics'][0].get('Text', 'No summary found.')
        # Fallback to SerpAPI if no result
        serpapi_key = os.getenv("SERPAPI_API_KEY")
        if not serpapi_key:
            return "No relevant web result found and SERPAPI_API_KEY not set for fallback."
        serp_url = f"https://serpapi.com/search.json?q={norm_query}&api_key={serpapi_key}&engine=google"
        print(f"[WebSearch] Fallback to SerpAPI: {serp_url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(serp_url) as resp:
                print(f"[WebSearch][SerpAPI] HTTP status: {resp.status}")
                serp_data = await resp.json()
                print(f"[WebSearch][SerpAPI] API response: {serp_data}")
                # Try to extract the top organic result snippet, title, and link
                if 'organic_results' in serp_data and serp_data['organic_results']:
                    result = serp_data['organic_results'][0]
                    snippet = result.get('snippet')
                    title = result.get('title')
                    link = result.get('link')
                    if snippet:
                        return f"{snippet}\nSource: {title} ({link})" if title and link else snippet
                    elif title and link:
                        return f"Top result: {title}\nURL: {link}"
                return "No relevant web result found from DuckDuckGo or Google (SerpAPI)."
    except Exception as e:
        print(f"Error in web_search: {e}")
        import traceback; traceback.print_exc()
        return f"Error fetching web search: {e}"

if __name__ == "__main__":
    try:
        print("Running FastMCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        print("Error starting server:", e)
        import traceback; traceback.print_exc()
