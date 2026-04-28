from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from models.favorite import Favorite
from models.news import News 
from config.db_config import get_db

# 查看指定的新闻是否被当前用户收藏
async def is_news_favorite(
        db: AsyncSession,
        user_id: int, 
        news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None  # 如果查询结果不为None，说明用户已经收藏了该新闻

# 添加收藏
async def add_news_favorite(
        db: AsyncSession,
        user_id: int, 
        news_id: int):
    new_favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(new_favorite)
    await db.commit()
    await db.refresh(new_favorite)  # 刷新实例以获取数据库生成的ID等字段
    return new_favorite  # 返回新添加的收藏记录，可以根据需要返回特定字段

# 移除收藏
async def remove_news_favorite(
        db: AsyncSession,
        user_id: int, 
        news_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # 返回是否成功删除了记录

# 获取用户的收藏列表
async def get_favorite_list(
        db: AsyncSession,
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ):
    # 计算总收藏数
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    # 查询收藏列表 - 联表查询 join() + 排序功能(时间) + 分页功能
    """
    # 联表查询
    - 语法: select(查询主体模型类, 字段别名).join(联合查询的模型类, 联合查询的条件)
    - 查询主体模型类: 代表查询结果中每一行数据的模型类，这里是News，因为我们最终要返回新闻列表
    - 联合查询的模型类: 代表我们要联合查询的模型类，这里是Favorite，因为我们要根据收藏记录来**筛选**新闻
    - News和Favorite中有重复的字段,通过取别名避免冲突。如: Favorite.created_at.label("favorite_time")
    """
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
            .join(Favorite, Favorite.news_id == News.id)    # 联表查询，连接条件: Favorite.news_id == News.id
            .where(Favorite.user_id == user_id)             # 根据用户ID筛选收藏记录
            .order_by(Favorite.created_at.desc())           # 根据收藏时间降序排序
            .offset((page - 1) * page_size).limit(page_size))       # 分页查询，计算偏移量和限制返回的记录数
    
    result =  await db.execute(query)   # 执行查询
    """
    这里不能采用scalars()方法，因为查询结果包含了多个模型类（News和Favorite），
    而scalars()方法只能处理单一模型类的结果。我们需要使用all()方法来获取完整的查询结果列表，
    每一行数据都是一个包含多个字段的元组。然后我们可以根据需要对这些数据进行处理和转换，以返回给前端。
    # 返回结果示例：
    [
        (新闻对象, 收藏时间, 收藏ID),   
        (新闻对象, 收藏时间, 收藏ID),   
        ...
    ]
    """
    rows = result.all()                 # 获取所有查询结果
    return rows, total  # 返回查询结果列表和总收藏数
    

# 清空收藏列表
async def remove_all_favorites(
        db: AsyncSession,
        user_id: int):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0  # 返回删除的记录数

 


