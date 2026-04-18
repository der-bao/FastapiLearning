"""
# 1. 进入对应目录
cd toutiao_backend

# 2. 运行 uvicorn 服务器（加上 --reload 以便在修改代码时热重载）
uv run uvicorn main:app --reload
"""

from fastapi import FastAPI
from routers import news  # 导入news模块的路由

app = FastAPI()

# 注册news模块的路由
app.include_router(news.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}   


