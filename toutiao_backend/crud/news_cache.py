from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import update

from models.news import Category, News
from cache.news_cache import (get_cached_categories, set_cached_categories,
                              set_cache_news_list, get_cache_news_list)

from fastapi.encoders import jsonable_encoder  # 导入jsonable_encoder函数用于将ORM对象转换为可序列化的格式

# 获取新闻分类列表
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    # 先从缓存中获取分类列表
    cache_categories = await get_cached_categories()
    if cache_categories is not None:
        return cache_categories  # 如果缓存中有数据，直接返回
    
    # 如果缓存中没有数据，则从数据库查询
    result = await db.execute(select(Category).offset(skip).limit(limit))
    categories = result.scalars().all()

    # 将查询结果缓存起来
    if categories: 
        # 此时的categories是一个ORM对象列表，需要转换成可序列化的格式（如字典列表）才能缓存
        categories = jsonable_encoder(categories)
        await set_cached_categories(categories)
    return categories

# 获取指定分类的新闻列表
async def get_news_list(
        db: AsyncSession, 
        category_id: int, 
        skip: int = 0,
        limit: int = 10
    ):
    # 先从缓存中获取新闻列表
    cache_news_list = await get_cache_news_list(category_id, skip // limit + 1, limit)
    if cache_news_list:
        return [News(item) for item in cache_news_list]  # 如果缓存中有数据，直接返回，并将字典转换回ORM对象


    # 从数据库查询所有指定分类的新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()  # 获取所有结果，如果没有则返回空列表

    # 将查询结果缓存起来
    if news_list:
        news_list = jsonable_encoder(news_list)
        await set_cache_news_list(category_id, skip // limit + 1, limit, news_list)

    return news_list

# 获取指定分类新闻的总数
async def get_news_count(
        db: AsyncSession, 
        category_id: int
    ):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 获取单个标量值，即新闻总数

# 获取新闻详情
async def get_news_detail(
        db: AsyncSession,
        news_id: int
):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  # 获取单个结果，即新闻详情

# 浏览量增加
async def increment_news_views(
        db: AsyncSession,
        news_id: int
):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()

    # 检查数据库中是否成功更新了浏览量
    return result.rowcount > 0      # rowcount属性表示受影响的行数，如果大于0则表示更新成功

# 相关新闻（同一分类的不同新闻）
async def get_related_news(
        db: AsyncSession, news_id: int,
        category_id: int, limit: int = 5):
    stmt = select(News).where(
            News.category_id == category_id,    # 同一分类
            News.id != news_id                  # 排除当前新闻
        ).order_by(
            News.views.desc(),                  # 浏览量降序排序，优先展示热门新闻
            News.publish_time.desc()            # 按发布时间降序排序，获取最新的相关新闻
            ).limit(limit)  
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    # 返回核心字段，避免返回过多数据
    return [{
        "id": news.id,
        "title": news.title,
        "content": news.content,
        "image": news.image,
        "author": news.author,   
        "publishTime": news.publish_time,
        "categoryId": news.category_id,
        "views": news.views,
    } for news in related_news]  # 列表推导式，提取核心字段