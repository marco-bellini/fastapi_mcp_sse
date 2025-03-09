from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from app import app


@app.get("/")
async def homepage():
    return HTMLResponse(
        "<h1>FastAPI MCP SSE</h1><p>Welcome to the SSE demo with MCP integration.</p>"
    )


@app.get("/about")
async def about():
    return PlainTextResponse(
        "About FastAPI MCP SSE: A demonstration of Server-Sent Events with Model Context Protocol integration."
    )


@app.get("/status")
async def status():
    status_info = {
        "status": "running",
        "server": "FastAPI MCP SSE",
        "version": "0.1.0",
    }
    return JSONResponse(status_info)


@app.get("/docs")
async def docs():
    return PlainTextResponse(
        "API Documentation:\n"
        "- GET /sse: Server-Sent Events endpoint\n"
        "- POST /messages: Send messages to be broadcasted\n"
        "- GET /status: Server status information"
    )
