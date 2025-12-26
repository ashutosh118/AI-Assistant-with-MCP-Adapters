from mcp.server.fastmcp import FastMCP
import aiohttp
import re

print("Starting wikipedia_server.py")
mcp = FastMCP("Wikipedia")

def normalize_topic(topic: str) -> str:
    # Remove leading/trailing whitespace, collapse spaces, and title-case for Wikipedia
    topic = topic.strip()
    topic = re.sub(r'\s+', ' ', topic)
    return topic.title().replace(' ', '_')

@mcp.tool(name="wikipedia_summary")
async def wikipedia_summary(topic: str) -> str:
    """Get a summary for a topic from Wikipedia. Input is normalized and debug logging is enabled."""
    try:
        norm_topic = normalize_topic(topic)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{norm_topic}"
        print(f"[Wikipedia] Requesting: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"[Wikipedia] HTTP status: {resp.status}")
                if resp.status != 200:
                    return f"No Wikipedia summary found for {topic}. (HTTP {resp.status})"
                data = await resp.json()
                print(f"[Wikipedia] API response: {data}")
                return data.get('extract', f"No summary found for {topic}.")
    except Exception as e:
        print(f"Error in wikipedia_summary: {e}")
        import traceback; traceback.print_exc()
        return f"Error fetching Wikipedia summary: {e}"

if __name__ == "__main__":
    try:
        print("Running FastMCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        print("Error starting server:", e)
        import traceback; traceback.print_exc()
