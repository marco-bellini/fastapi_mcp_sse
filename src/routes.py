# src/routes.py
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi import APIRouter, Depends, HTTPException, status # Import necessary modules
from fastapi.security import OAuth2PasswordRequestForm
from app import app
from auth import create_access_token, verify_password, get_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, require_role # Import auth components
from datetime import timedelta

# Create a router with a general tag for API documentation organization
router = APIRouter(tags=["General"])

# --- Existing Routes ---
@router.get("/")
async def homepage():
    """Root endpoint that returns a simple HTML welcome page"""
    html_content = (
        "<h1>FastAPI MCP SSE</h1>"
        "<p>Welcome to the SSE demo with MCP integration.</p>"
    )
    return HTMLResponse(html_content)


@router.get("/about")
async def about():
    """About endpoint that returns information about the application"""
    return PlainTextResponse(
        "About FastAPI MCP SSE: A demonstration of Server-Sent Events "
        "with Model Context Protocol integration."
    )

# Note: /status is left public, but you might want to protect it.
@router.get("/status")
async def status():
    """Status endpoint that returns the current server status"""
    status_info = {
        "status": "running",
        "server": "FastAPI MCP SSE",
        "version": "0.1.0",
    }
    return JSONResponse(status_info)

# --- New Login Endpoint ---
@router.post("/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to obtain a JWT access token by providing username and password.
    """
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "roles": user.get("roles", [])}, # Include roles in token payload
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# --- Example Protected Endpoint ---
@router.get("/protected-status", tags=["General"], summary="Get server status (Authenticated)")
async def protected_status(current_user: dict = Depends(get_current_user)):
    """
    Returns the current server status, requires a valid JWT token.
    Also shows information about the authenticated user.
    """
    status_info = {
        "status": "running",
        "server": "FastAPI MCP SSE",
        "version": "0.1.0",
        "authenticated_user": current_user # Include authenticated user info
    }
    return JSONResponse(status_info)

# --- Example Role-Restricted Endpoint ---
# @router.get("/admin-only", tags=["Admin"], summary="Admin-only endpoint")
# async def admin_only_endpoint(current_user: dict = Depends(require_role("admin"))):
#     """Endpoint only accessible by users with the 'admin' role."""
#     return {"message": "Welcome, admin!", "user": current_user}


# Include the router in the main application
app.include_router(router)