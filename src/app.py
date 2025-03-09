from fastapi import FastAPI, Request
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp

# 创建 FastAPI 应用
app = FastAPI()
# 创建 SSE 传输实例
sse = SseServerTransport("/messages/")
# 挂载 /messages 路径给 sse.handle_post_message 处理
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))


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
