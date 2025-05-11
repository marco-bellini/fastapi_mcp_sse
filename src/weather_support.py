import logging
from typing import Any
import httpx

# Configure logging for this module
logger = logging.getLogger(__name__)

# Constants
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    logger.debug(f"Making NWS request to: {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {url}")
            return response.json()
        except Exception as e:
            logger.error(f"Error during NWS request to {url}: {e}")
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    logger.debug(f"Formatting alert: {props}")
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""
