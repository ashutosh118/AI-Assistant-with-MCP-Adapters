from mcp.server.fastmcp import FastMCP
import aiohttp
import re

print("Starting currency_converter_server.py")
mcp = FastMCP("CurrencyConverter")

# Simple normalization for common currency names
CURRENCY_ALIASES = {
    "dollar": "USD",
    "usd": "USD",
    "euro": "EUR",
    "eur": "EUR",
    "pound": "GBP",
    "gbp": "GBP",
    "yen": "JPY",
    "jpy": "JPY",
    "rupee": "INR",
    "inr": "INR",
    "cad": "CAD",
    "aud": "AUD",
    "cny": "CNY",
    "yuan": "CNY",
    "franc": "CHF",
    "chf": "CHF",
    # Add more as needed
}

def normalize_currency(cur: str) -> str:
    cur = cur.strip().lower()
    cur = re.sub(r'[^a-z]', '', cur)  # Remove non-alpha chars
    return CURRENCY_ALIASES.get(cur, cur.upper())

@mcp.tool(name="convert_currency")
async def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert amount from one currency to another using exchangerate.host API. Accepts currency names or codes."""
    try:
        from_cur = normalize_currency(from_currency)
        to_cur = normalize_currency(to_currency)
        url = f"https://api.exchangerate.host/convert?from={from_cur}&to={to_cur}&amount={amount}"
        print(f"[CurrencyConverter] Requesting: {url}")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"[CurrencyConverter] HTTP status: {resp.status}")
                data = await resp.json()
                print(f"[CurrencyConverter] API response: {data}")
                if 'result' in data:
                    return f"{amount} {from_cur} = {data['result']} {to_cur}"
                else:
                    return f"Could not fetch conversion. API response: {data}"
    except Exception as e:
        print(f"Error in convert_currency: {e}")
        import traceback; traceback.print_exc()
        return f"Error converting currency: {e}"

if __name__ == "__main__":
    try:
        print("Running FastMCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        print("Error starting server:", e)
        import traceback; traceback.print_exc()
