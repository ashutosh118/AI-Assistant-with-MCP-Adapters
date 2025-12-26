from mcp.server.fastmcp import FastMCP

print("Starting unit_converter_server.py")
mcp = FastMCP("UnitConverter")

# Simple conversion factors for demonstration
CONVERSIONS = {
    ("mile", "kilometer"): 1.60934,
    ("kilometer", "mile"): 0.621371,
    ("kg", "lb"): 2.20462,
    ("lb", "kg"): 0.453592,
    ("celsius", "fahrenheit"): lambda c: c * 9/5 + 32,
    ("fahrenheit", "celsius"): lambda f: (f - 32) * 5/9,
}

@mcp.tool(name="unit_conversion")
def convert_unit(amount: float, from_unit: str, to_unit: str) -> str:
    """Convert between units (mile/km, kg/lb, celsius/fahrenheit, etc.)."""
    key = (from_unit.lower(), to_unit.lower())
    if key not in CONVERSIONS:
        return f"Conversion from {from_unit} to {to_unit} not supported."
    factor = CONVERSIONS[key]
    if callable(factor):
        result = factor(amount)
    else:
        result = amount * factor
    return f"{amount} {from_unit} = {result} {to_unit}"

if __name__ == "__main__":
    try:
        print("Running FastMCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        print("Error starting server:", e)
        import traceback; traceback.print_exc()
