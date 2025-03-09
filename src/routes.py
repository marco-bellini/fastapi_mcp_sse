from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount


def create_app(mcp):
    app = FastAPI()
    sse = SseServerTransport("/messages/")

    @app.get("/sse")
    async def handle_sse(request: Request):
        # 直接使用 sse.connect_sse 连接 MCP 服务器
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )

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

    # 挂载 /messages 路径给 sse.handle_post_message 处理
    app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

    return app
