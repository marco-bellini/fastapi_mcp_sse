# 

import logging
from mcp.server.fastmcp import FastMCP
from weather_support import make_nws_request, format_alert


# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("weather")


# Constants
NWS_API_BASE = "https://api.weather.gov"





@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    logger.info(f"get_alerts called with state: {state}")
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        logger.warning(f"No data or features for state: {state}")
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        logger.info(f"No active alerts for state: {state}")
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    logger.debug(f"Returning {len(alerts)} alerts for state: {state}")
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    logger.info(f"get_forecast called with latitude={latitude}, longitude={longitude}")
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        logger.warning(f"No points data for lat={latitude}, lon={longitude}")
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        logger.warning(f"No forecast data for lat={latitude}, lon={longitude}")
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        logger.debug(f"Formatting forecast period: {period.get('name', 'N/A')}")
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    logger.info(f"Returning {len(forecasts)} forecast periods for lat={latitude}, lon={longitude}")
    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    logger.info("Running weather.py as main. Starting MCP server with SSE transport.")
    # Initialize and run the server
    mcp.run(transport="sse")
