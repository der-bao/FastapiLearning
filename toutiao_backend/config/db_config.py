from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


# 数据库URL
ASYNC_DATABASE_URL = "mysql+aiomysql://root:ad839116@localhost:3306/news_app?charset=utf8mb4"

# 创建异步引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL, 
    echo=True,
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 超出连接池大小的最大连接数
    )

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False      # 提高性能，提交后不自动过期对象
)

# 依赖项：管理异步数据库会话
async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            yield session
            await session.commit()  # 提交事务
    except Exception as e:
        await session.rollback()  # 回滚事务
        raise e
    finally:
        await session.close()  # 关闭会话

