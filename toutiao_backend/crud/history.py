from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete

from models.history import History
from models.news import News

from datetime import datetime

async def add_news_history(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    # 判断是否已存在历史记录
    stmt = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(stmt)
    history_record = result.scalar_one_or_none()

    if history_record:
        # 记录存在，直接修改该 ORM 对象的属性，SQLAlchemy 会自动追踪变更
        history_record.view_time = datetime.now()
    else:
        # 记录不存在，创建新记录并添加到 session
        history_record = History(user_id=user_id, news_id=news_id)
        db.add(history_record)
        
    await db.commit()
    await db.refresh(history_record)  # 刷新实例以获取数据库生成的ID等字段
    return history_record  # 返回历史记录


# 获取新闻浏览历史列表（联表查询）
async def get_news_history_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10
):
    # 统计浏览历史总数
    count_stmt = select(func.count()).select_from(History).where(History.user_id == user_id)
    result = await db.execute(count_stmt)
    total_count = result.scalar_one()

    # 分页查询浏览历史列表《联表查询》
    stmt = (
        select(News, History.view_time.label("view_time"))
        .join(History, News.id == History.news_id)  # 联表查询，连接条件: News.id == History.news_id
        .where(History.user_id == user_id)          # 根据用户ID筛选历史记录
        .order_by(History.view_time.desc())         # 根据浏览时间降序排序
        .offset((page - 1) * page_size)             # 分页功能，计算偏移量
        .limit(page_size)
    )
    result = await db.execute(stmt)
    history_list = result.all()

    return total_count, history_list


# 删除单条历史记录
async def delete_news_history(
    db: AsyncSession,
    history_id: int,
    user_id: int
):
    stmt = delete(History).where(History.news_id == history_id, History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # 返回是否成功删除了记录

# 清空指定用户的所有浏览记录
async def clear_all_history(
    db: AsyncSession,
    user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0  # 返回是否成功删除了记录
