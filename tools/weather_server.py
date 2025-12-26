from mcp.server.fastmcp import FastMCP

print("Starting weather_server.py")
mcp = FastMCP("Weather")

import aiohttp

@mcp.tool(name="get_weather")
async def get_weather(location: str) -> str:
    """Get real-time weather for a location using Open-Meteo API."""
    try:
        # Geocode location to get latitude and longitude
        async with aiohttp.ClientSession() as session:
            geo_url = f"https://nominatim.openstreetmap.org/search?format=json&q={location}"
            async with session.get(geo_url) as geo_resp:
                geo_data = await geo_resp.json()
                if not geo_data:
                    return f"Could not find location: {location}"
                lat = geo_data[0]['lat']
                lon = geo_data[0]['lon']

            # Fetch weather data
            weather_url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                "&current_weather=true"
            )
            async with session.get(weather_url) as weather_resp:
                weather_data = await weather_resp.json()
                if 'current_weather' not in weather_data:
                    return f"Could not fetch weather for {location}"
                temp = weather_data['current_weather']['temperature']
                wind = weather_data['current_weather']['windspeed']
                return f"Current temperature in {location} is {temp}°C with windspeed {wind} km/h."
    except Exception as e:
        return f"Error fetching weather: {e}"

if __name__ == "__main__":
    try:
        print("Running FastMCP server...")
        mcp.run(transport="stdio")
    except Exception as e:
        print("Error starting server:", e)
        import traceback; traceback.print_exc()
