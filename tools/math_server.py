from mcp.server.fastmcp import FastMCP

print("Starting math_server.py")

mcp = FastMCP("Math")

@mcp.tool(name="add")
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool(name="subtract")
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool(name="multiply")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool(name="divide")
def divide(a: int, b: int) -> int:
    """divide two numbers"""
    return a / b

@mcp.tool(name="percent_of")
def percent_of(percent: float, value: float) -> float:
    """
    Calculate X% of Y. For example, percent_of(10, 50) returns 5.
    This tool can be used in sequence for chained percentages, e.g.:
    - To find 10% of 50% of 100:
      1. percent_of(50, 100) → 50
      2. percent_of(10, 50) → 5
    """
    return (percent / 100) * value

if __name__ == "__main__":
    print("Running FastMCP server...")
    mcp.run(transport="stdio")
