
import logging
from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp, get_alerts, get_forecast
from fastapi import Query



# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application with metadata
app = FastAPI(
    title="FastAPI MCP SSE",
    description="A demonstration of Server-Sent Events with Model Context "
    "Protocol integration",
    version="0.1.0",
)

# REST endpoint for get_alerts
@app.get("/get_alerts", tags=["Weather"])
async def rest_get_alerts(state: str = Query(..., description="Two-letter US state code (e.g. CA, NY)")):
    """REST endpoint to get weather alerts for a US state."""
    return await get_alerts(state)

# REST endpoint for get_forecast
@app.get("/get_forecast", tags=["Weather"])
async def rest_get_forecast(
    latitude: float = Query(..., description="Latitude of the location"),
    longitude: float = Query(..., description="Longitude of the location")
):
    """REST endpoint to get weather forecast for a location."""
    return await get_forecast(latitude, longitude)

# Create SSE transport instance for handling server-sent events
sse = SseServerTransport("/messages/")

# Mount the /messages path to handle SSE message posting
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))


# Add documentation for the /messages endpoint
@app.get("/messages", tags=["MCP"], include_in_schema=True)
def messages_docs():
    """
    Messages endpoint for SSE communication

    This endpoint is used for posting messages to SSE clients.
    Note: This route is for documentation purposes only.
    The actual implementation is handled by the SSE transport.
    """
    logger.debug("/messages documentation endpoint called.")
    pass  # This is just for documentation, the actual handler is mounted above


@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    """
    SSE endpoint that connects to the MCP server

    This endpoint establishes a Server-Sent Events connection with the client
    and forwards communication to the Model Context Protocol server.
    """
    logger.info("/sse endpoint called. Establishing SSE connection.")
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            logger.debug("SSE connection established. Running MCP server.")
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )
            logger.info("MCP server run completed for SSE connection.")
    except Exception as e:
        logger.exception(f"Exception in /sse endpoint: {e}")


# Import routes at the end to avoid circular imports
# This ensures all routes are registered to the app
import routes  # noqa
