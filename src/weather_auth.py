# src/weather.py
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from fastapi import HTTPException, status # Import for raising HTTP exceptions
import logging # Import logging
from src.weather_support import make_nws_request, format_alert

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0" # Use a more descriptive user agent

# # --- Improved API Request Handling ---
# async def make_nws_request(url: str) -> dict[str, Any] | None:
#     """Make a request to the NWS API with proper error handling."""
#     headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
#     async with httpx.AsyncClient() as client:
#         try:
#             logger.info(f"Making NWS request to: {url}")
#             response = await client.get(url, headers=headers, timeout=30.0)
#             response.raise_for_status() # Raise HTTPStatusError for bad responses (4xx or 5xx)
#             logger.info(f"Successfully fetched data from {url}")
#             return response.json()
#         except httpx.RequestError as exc:
#             # Log specific request errors (e.g., network issues, timeouts)
#             logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
#             return None
#         except httpx.HTTPStatusError as exc:
#             # Log HTTP errors (e.g., 404, 500)
#             logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
#             # Optionally, return more specific information based on status code
#             if exc.response.status_code == 404:
#                 return None # Or return {"error": "Not Found"}
#             return None # Default for other HTTP errors
#         except Exception as e:
#             # Catch any other unexpected exceptions
#             logger.error(f"An unexpected error occurred during NWS request: {e}", exc_info=True)
#             return None


# # --- Data Formatting ---
# def format_alert(feature: dict) -> str:
#     """Format an alert feature into a readable string."""
#     props = feature.get("properties", {}) # Use .get() for safer access
#     return f"""
# Event: {props.get('event', 'Unknown')}
# Area: {props.get('areaDesc', 'Unknown')}
# Severity: {props.get('severity', 'Unknown')}
# Description: {props.get('description', 'No description available')}
# Instructions: {props.get('instruction', 'No specific instructions provided')}
# """

def format_forecast_period(period: dict) -> str:
    """Formats a single forecast period into a readable string."""
    return f"""
{period.get('name', 'Unknown Period')}:
Temperature: {period.get('temperature', 'N/A')}°{period.get('temperatureUnit', 'N/A')}
Wind: {period.get('windSpeed', 'N/A')} {period.get('windDirection', 'N/A')}
Forecast: {period.get('detailedForecast', 'No detailed forecast available')}
"""


# --- MCP Tools with Input Validation ---
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    # Input Validation: Basic check for state code format
    if not (isinstance(state, str) and len(state) == 2 and state.isalpha()):
         # In a real tool, you might return a specific error message
         # or raise a tool-specific error if supported by MCP.
         # For now, return an informative string.
        return "Invalid state code format. Please provide a two-letter US state code."

    url = f"{NWS_API_BASE}/alerts/active/area/{state.upper()}" # Use upper() for consistency
    data = await make_nws_request(url)

    if data is None: # Check for explicit None from make_nws_request on error
        return "An error occurred while fetching alerts."

    if "features" not in data or not isinstance(data["features"], list):
         logger.error(f"Unexpected response format for alerts: {data}")
         return "Unable to fetch alerts or unexpected data format."

    if not data["features"]:
        return f"No active alerts found for {state.upper()}."

    # Format alerts (using list comprehension as before)
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location (e.g. 34.0522)
        longitude: Longitude of the location (e.g. -118.2437)
    """
    # Input Validation: Check for valid latitude and longitude ranges
    if not (-90 <= latitude <= 90):
        return "Invalid latitude value. Must be between -90 and 90."
    if not (-180 <= longitude <= 180):
        return "Invalid longitude value. Must be between -180 and 180."

    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if points_data is None:
        return "Unable to fetch forecast grid data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_data.get("properties", {}).get("forecast") # Use .get safely
    if not forecast_url:
        logger.error(f"Forecast URL not found in points data: {points_data}")
        return "Unable to find forecast data for this location."

    forecast_data = await make_nws_request(forecast_url)

    if forecast_data is None:
        return "Unable to fetch detailed forecast data."

    periods = forecast_data.get("properties", {}).get("periods") # Use .get safely
    if not isinstance(periods, list):
         logger.error(f"Unexpected response format for forecast periods: {forecast_data}")
         return "Unable to fetch detailed forecast or unexpected data format."

    if not periods:
        return "No forecast periods available for this location."


    # Format the periods into a readable forecast
    forecasts = [format_forecast_period(period) for period in periods[:5]] # Only show next 5 periods
    return "\n---\n".join(forecasts)


if __name__ == "__main__":
    # Initialize and run the server
    # Note: Running with `if __name__ == "__main__":` is for development.
    # In production, use a proper ASGI server like `uvicorn src.server:app`.
    # Also, ensure SECRET_KEY environment variable is set for JWTs.
    mcp.run(transport="sse")