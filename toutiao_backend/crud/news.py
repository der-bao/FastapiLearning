

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.news import Category

async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return result.scalars().all()  