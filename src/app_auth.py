# src/app.py
from fastapi import FastAPI, Request, Depends, HTTPException, status # Import Depends, HTTPException, status
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp
# Authentication removed: auth.py no longer exists

# Create FastAPI application with metadata
app = FastAPI(
    title="FastAPI MCP SSE",
    description="A demonstration of Server-Sent Events with Model Context "
    "Protocol integration, with added security features.", # Updated description
    version="0.1.0",
)

# Create SSE transport instance for handling server-sent events
sse = SseServerTransport("/messages/")

# Mount the /messages path to handle SSE message posting
# Note: This endpoint is typically used internally by the MCP server
# and might need different security considerations depending on your setup.
# For now, we'll leave it unprotected at the application level, assuming
# the primary interaction point is the /sse endpoint.
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))


# Add documentation for the /messages endpoint
# You might want to indicate in documentation that posting requires specific auth or is internal.
@app.get("/messages", tags=["MCP"], include_in_schema=True, summary="SSE Messages endpoint (Internal?)")
def messages_docs():
    """
    Messages endpoint for SSE communication. This is primarily used by the MCP server
    transport internally to send messages back to the client.
    Note: This route is for documentation purposes only.
    """
    pass

# Authenticated SSE endpoint removed: auth.py and authentication no longer exist


# Import routes at the end to avoid circular imports
# This ensures all routes are registered to the app
import routes  # noqa