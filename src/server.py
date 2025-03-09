import uvicorn
from app import app


def run():
    """启动 FastAPI 服务器"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
