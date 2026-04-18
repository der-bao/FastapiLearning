# 模块化路由

from fastapi import APIRouter

# 创建一个APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

# 路由处理函数

@router.get("/categories")
async def get_categories():
    return {"msg": "获取新闻分类成功"}