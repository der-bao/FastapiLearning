"""
# 接口实现流程
- 1. 模块化路由 
- 2. 定义模型类
- 3. 在crud文件夹创建文件，封装操作数据库的方法
- 4. 在路由处理函数中调用crud封装好的方法，响应结果

"""

from fastapi import APIRouter

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db

from crud import news

# 创建一个APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

# 路由处理函数
@router.get("/categories")
async def get_categories(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
    ):
    categories = await news.get_categories(db=db, skip=skip, limit=limit)  # 调用crud封装好的方法获取数据
    return {
        "code": 200,
        "msg": "获取新闻分类成功",
        "data": categories
    }