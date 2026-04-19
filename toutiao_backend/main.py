"""
# 1. 进入对应目录
cd toutiao_backend

# 2. 运行 uvicorn 服务器（加上 --reload 以便在修改代码时热重载）
uv run uvicorn main:app --reload
"""

from fastapi import FastAPI
from routers import news  # 导入news模块的路由
from routers import users  # 导入users模块的路由
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

"""
# 跨域限制
一种浏览器的安全策略
- 浏览器会拦截前端跨域请求的响应，如果响应头里没有 Access-Control-Allow-Origin 等字段，就会报错。
- 后端本身收到请求并返回了数据，只是浏览器不让前端拿到而已。

# 解决跨域问题
 只需要在后端配置 CORS（跨域资源共享）规则，让响应带上允许跨域的头信息
"""

app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"],        # 允许所有来源
    allow_credentials=True,     # 允许携带凭证（如cookies）
    allow_methods=["*"],        # 允许所有HTTP方法
    allow_headers=["*"],        # 允许所有HTTP头
)

# 注册news模块的路由
app.include_router(news.router)

# 注册users模块的路由
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}   


