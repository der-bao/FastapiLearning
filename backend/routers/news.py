"""
# 接口实现流程
- 1. 模块化路由 
- 2. 定义模型类
- 3. 在crud文件夹创建文件，封装操作数据库的方法
- 4. 在路由处理函数中调用crud封装好的方法，响应结果

"""

from fastapi import APIRouter
from fastapi import Query


from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from config.db_config import get_db
from crud import news
from crud import news_cache

# 创建一个APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

# ==================================
# 路由处理函数
# ==================================

@router.get("/categories")
async def get_categories(
    skip: int = 0, limit: int = 100, 
    db: AsyncSession = Depends(get_db)
    ):
    categories = await news_cache.get_categories(db=db, skip=skip, limit=limit)  # 调用crud封装好的方法获取数据
    return {
        "code": 200,
        "msg": "获取新闻分类成功",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),  # 从查询参数中获取categoryId，并将其映射到category_id变量
    page: int = 1, 
    page_size: int = Query(10, alias="pageSize",le=100),  # 从查询参数中获取pageSize，并将其映射到page_size变量
    db: AsyncSession = Depends(get_db)
    ):
    skip = (page - 1) * page_size  # 计算分页的偏移量

    # 获取指定分类的新闻列表
    news_list = await news_cache.get_news_list(db=db, category_id=category_id, skip=skip, limit=page_size)  # 调用crud封装好的方法获取数据
    # 获取指定分类新闻的总数
    total = await news.get_news_count(db=db, category_id=category_id)
    
    has_more = skip + len(news_list) < total  # 判断是否还有更多数据

    return {
        "code": 200,
        "msg": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,
            "hasMore": has_more
        }
    }

@router.get("/detail")
async def read_news_detail(
    news_id: int = Query(..., alias="id"),  # 从查询参数中获取newsId，并将其映射到news_id变量
    db: AsyncSession = Depends(get_db)
):
    news_detail = await news.get_news_detail(db=db, news_id=news_id)  # 调用crud封装好的方法获取数据
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻未找到")
    
    # 浏览量增加
    view_res =  await news.increment_news_views(db=db, news_id=news_detail.id)
    if not view_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    # 相关新闻（同一分类的新闻）
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "msg": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,   
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news  
        }
    }