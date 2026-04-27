from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from models.favorite import Favorite
from config.db_config import get_db


async def is_news_favorite(
        db: AsyncSession,
        user_id: int, 
        news_id: int):
    stmt = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None  # 如果查询结果不为None，说明用户已经收藏了该新闻
