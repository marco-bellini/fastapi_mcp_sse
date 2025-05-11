# Running and Debugging the MCP Server with Starlette

This guide explains how to launch, debug, and test the `weather.py` MCP server using Starlette and Uvicorn.

## 1. Launching the Server

A script is provided at `scripts/starlette_weather_server.py` to run the MCP server as an ASGI app with Starlette and Uvicorn.

### Requirements
- Python 3.8+
- Install dependencies (from project root):
  ```bash
  pip install -r requirements.txt
  # or if using pyproject.toml:
  pip install .
  ```
- Uvicorn and Starlette should be installed (they are required by the script).

### Start the Server

From the project root, run (recommended):
```bash
uvicorn scripts.starlette_weather_server:app --reload
```
This uses Uvicorn directly to serve the ASGI app with hot-reloading for development.

Alternatively, you can run:
```bash
python scripts/starlette_weather_server.py
```
This will also start the server, but hot-reloading and some features may not work as expected.

**Note:**
- If you are using the `uv` tool for dependency isolation, run:
  ```bash
  uv run uvicorn scripts.starlette_weather_server:app --reload
  ```
  Do not use `uv run python scripts/starlette_weather_server.py` for development, as it may not work correctly with ASGI servers.

The server will be available at `http://localhost:8000/`.

## 2. Debugging

- The server uses Python's `logging` module. To see debug logs, set the environment variable before running:
  ```bash
  export LOGLEVEL=DEBUG
  python scripts/starlette_weather_server.py
  ```
- You can also edit the logging level in `weather.py` or the script to show more detailed logs.
- Use breakpoints or print statements for step-by-step debugging.

## 3. Testing the Endpoints

You can test the MCP server endpoints using `curl`, `httpie`, or any API client (e.g., Postman).

### Example: Get Weather Alerts
```bash
curl "http://localhost:8000/tools/get_alerts?state=CA"
```

### Example: Get Forecast
```bash
curl "http://localhost:8000/tools/get_forecast?latitude=34.05&longitude=-118.25"
```

Replace the parameters as needed.

## 4. Notes
- The server supports CORS for development, so you can call it from a browser or frontend app.
- If you make changes to the code, use the `--reload` option with Uvicorn for automatic restarts.

---

For more details, see the code in `scripts/starlette_weather_server.py` and `src/weather.py`.
