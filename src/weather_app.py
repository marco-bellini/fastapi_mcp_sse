import logging
from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp, get_alerts, get_forecast
from fastapi import Query




import tempfile
import os



# Use a fixed log file path to avoid multiple log files on reloads
log_file_path = os.path.join("/tmp", "weather_app.log")

# Print the log file path at startup for CLI access
print(f"[weather_app.py] Log file path: {log_file_path}")

# Ensure root logger is configured to write to the log file and console
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove all handlers associated with the root logger object (avoid duplicate logs)
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))

root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

# Create FastAPI application with metadata
app = FastAPI(
    title="FastAPI MCP SSE",
    description="A demonstration of Server-Sent Events with Model Context "
    "Protocol integration",
    version="0.1.0",
)


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
    pass  # This is just for documentation, the actual handler is mounted above


@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    """
    SSE endpoint that connects to the MCP server

    This endpoint establishes a Server-Sent Events connection with the client
    and forwards communication to the Model Context Protocol server.
    """
    # Use sse.connect_sse to establish an SSE connection with the MCP server
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        # Run the MCP server with the established streams
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )
        logger.info("SSE connection established with client")


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

# # Create SSE transport instance for handling server-sent events
# sse = SseServerTransport("/sse")  # Root path for SSE events since we handle specific paths in routes

# # Add CORS middleware to allow SSE connections
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount the messages path to handle SSE message posting
# app.router.routes.append(Mount("/messages", app=sse.handle_post_message))



from fastapi.responses import PlainTextResponse

@app.get("/logs", tags=["Logs"], response_class=PlainTextResponse)
async def get_logs():
    """
    Endpoint to retrieve the latest application logs.
    Returns the contents of the log file as plain text.
    Limits the response to the last 1000 lines for performance.
    """
    try:
        if not os.path.exists(log_file_path):
            return "Log file not found."
        
        # Read the last 1000 lines of the log file
        lines = []
        with open(log_file_path, "r") as f:
            for line in f:
                lines.append(line)
                if len(lines) > 1000:
                    lines.pop(0)
        
        return "".join(lines)
    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return f"Error accessing logs: {str(e)}"

# @app.get("/messages", tags=["MCP"], include_in_schema=True)
# def messages_docs():
#     """
#     Messages endpoint for SSE communication

#     This endpoint is used for posting messages to SSE clients.
#     Note: This route is for documentation purposes only.
#     The actual implementation is handled by the SSE transport.
#     """
#     pass

# @app.get("/", tags=["MCP"])
# async def handle_sse(request: Request):
#     """
#     Root SSE endpoint that connects to the MCP server

#     This endpoint establishes a Server-Sent Events connection with the client
#     and forwards communication to the Model Context Protocol server.
#     """
#     if not request.headers.get("accept") == "text/event-stream":
#         return {"message": "This endpoint requires SSE connection"}
    
#     logger.info("SSE connection request received")
#     try:
#         logger.debug("Setting up SSE connection")
#         async with sse.connect_sse(request.scope, request.receive, request._send) as (
#             read_stream,
#             write_stream,
#         ):
#             logger.info(f"SSE connection established with client")
#             try:
#                 await mcp._mcp_server.run(
#                     read_stream,
#                     write_stream,
#                     mcp._mcp_server.create_initialization_options(),
#                 )
#                 logger.info("MCP server run completed normally")
#             except Exception as e:
#                 logger.error(f"Error in MCP server run: {e}", exc_info=True)
#                 raise
#             finally:
#                 logger.debug("MCP server run block completed")
#     except Exception as e:
#         logger.error(f"Error in SSE connection: {e}", exc_info=True)
#         raise
#     finally:
#         logger.info("SSE connection handler completed")


# Import routes at the end to avoid circular imports
# This ensures all routes are registered to the app
import routes  # noqa
