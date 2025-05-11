# src/app.py
from fastapi import FastAPI, Request, Depends, HTTPException, status # Import Depends, HTTPException, status
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp
from auth import get_current_user # Import the authentication dependency

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

@app.get("/sse", tags=["MCP"], summary="Connect to MCP SSE (Authenticated)")
async def handle_sse(
    request: Request,
    current_user: dict = Depends(get_current_user) # Require authentication to establish SSE connection
):
    """
    SSE endpoint that connects to the MCP server.
    Requires a valid JWT token in the Authorization header to establish the connection.

    Once connected, the client can interact with the MCP server via SSE.
    The authenticated user's information is available via the `current_user` dependency
    and could potentially be passed to the MCP tools if the MCP library supports it.
    """
    # If get_current_user doesn't raise an HTTPException, the user is authenticated.
    # You could add further authorization checks here based on `current_user` if needed
    # (e.g., checking for a specific role or permission to access the MCP tools).
    # Example:
    # if "can_use_weather_tools" not in current_user.get("permissions", []):
    #      raise HTTPException(
    #          status_code=status.HTTP_403_FORBIDDEN,
    #          detail="User not authorized to use weather tools"
    #      )

    # Use sse.connect_sse to establish an SSE connection with the MCP server
    # This part proceeds only if authentication and optional authorization succeeded.
    async with sse.connect_sse(request.scope, request.receive, request._send) as (
        read_stream,
        write_stream,
    ):
        # Pass the authenticated user information to the MCP server if the MCP library supports it.
        # This would allow your tools in weather.py to know which user is calling them.
        # As per the MCP documentation or library capabilities, you might modify
        # create_initialization_options() or pass extra arguments to mcp._mcp_server.run()
        # Example (conceptual, depends on MCP library):
        # initialization_options = mcp._mcp_server.create_initialization_options()
        # initialization_options["user"] = current_user # Add user info to options
        # await mcp._mcp_server.run(read_stream, write_stream, initialization_options)

        # For now, we'll run without explicitly passing user info to MCP,
        # relying on the connection itself being authenticated.
        await mcp._mcp_server.run(
            read_stream,
            write_stream,
            mcp._mcp_server.create_initialization_options(),
        )


# Import routes at the end to avoid circular imports
# This ensures all routes are registered to the app
import routes  # noqa