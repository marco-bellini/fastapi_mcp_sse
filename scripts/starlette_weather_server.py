# scripts/starlette_weather_server.py
"""
Launch the weather.py MCP server using Starlette ASGI app.
"""
import logging
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import sys


# Use the FastAPI app directly from src/app.py
sys.path.append("../src")
from weather_app import app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Starting FastAPI MCP server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
