# src/routes.py

import logging
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi import APIRouter, Depends, HTTPException, status # Import necessary modules
# from fastapi.security import OAuth2PasswordRequestForm
from weather_app import app
# Authentication removed: auth.py no longer exists
from datetime import timedelta

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a router with a general tag for API documentation organization
router = APIRouter(tags=["General"])

# --- Existing Routes ---
@router.get("/")
async def homepage():
    """Root endpoint that returns a simple HTML welcome page"""
    logger.info("Homepage (/) endpoint called.")
    html_content = (
        "<h1>FastAPI MCP SSE</h1>"
        "<p>Welcome to the SSE demo with MCP integration.</p>"
    )
    return HTMLResponse(html_content)


@router.get("/about")
async def about():
    """About endpoint that returns information about the application"""
    logger.info("About (/about) endpoint called.")
    return PlainTextResponse(
        "About FastAPI MCP SSE: A demonstration of Server-Sent Events "
        "with Model Context Protocol integration."
    )

# Note: /status is left public, but you might want to protect it.
@router.get("/status")
async def status():
    """Status endpoint that returns the current server status"""
    logger.info("Status (/status) endpoint called.")
    status_info = {
        "status": "running",
        "server": "FastAPI MCP SSE",
        "version": "0.1.0",
    }
    return JSONResponse(status_info)

# Authentication endpoints removed: auth.py no longer exists

# --- Example Protected Endpoint ---
# Protected endpoint removed: auth.py and authentication no longer exist

# --- Example Role-Restricted Endpoint ---
# @router.get("/admin-only", tags=["Admin"], summary="Admin-only endpoint")
# async def admin_only_endpoint(current_user: dict = Depends(require_role("admin"))):
#     """Endpoint only accessible by users with the 'admin' role."""
#     return {"message": "Welcome, admin!", "user": current_user}


# Include the router in the main application
app.include_router(router)