import uvicorn
from weather import mcp
from routes import create_app

# 创建 FastAPI 应用
app = create_app(mcp)


def run():
    """启动 FastAPI 服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
