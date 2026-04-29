from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Integer, String, Float

# ==================== ORM相关概念 ========================
"""
相关概念介绍：
    1. ORM（对象关系映射）：
        - ORM是一种将数据库表映射为Python类的技术，使开发者能够使用面向对象的方式操作数据库。
        - 通过ORM，开发者可以使用Python对象来表示数据库中的数据，并通过方法调用来执行数据库操作，而无需编写原始SQL语句。
    
    2. 异步引擎：
        - 异步引擎是SQLAlchemy中用于异步数据库操作的对象，支持异步连接和查询。
        - 创建异步引擎时需要指定数据库URL，并且使用适当的数据库驱动（如aiomysql、asyncpg等）。

    3. 连接池；
        - 数据库连接：是程序与 MySQL 之间建立的一个 TCP 通讯管道。
        - 连接池是一个持续保留数据库连接的池子

    4. 会话：
        - 会话是在数据库连接上进行操作的对象，负责管理对象的生命周期和数据库事务。
        - 会话结束后需要关闭，以释放数据库连接资源。数据库连接池会自动管理连接的复用和释放。
        - 会话工厂是一个用于创建会话的工厂对象，通常使用 SQLAlchemy 的 sessionmaker 来创建。
"""


# ==================== 建库、建表 ========================
"""
思路：
    - 创建异步数据库引擎
    - 定义模型类（基类 + 表对应的模型类）
    - 创建表：定义函数建表 → Fastapi启动时调用建表函数
"""

# 1. 创建异步数据库引擎
AYNC_DATABASE_URL = "mysql+aiomysql://root:ad839116@localhost:3306/fastapi_first?charset=utf8"
async_engine = create_async_engine(
    AYNC_DATABASE_URL, 
    echo=True,              # 可选，用于输出 SQL 语句日志
    pool_size=10,          # 可选，连接池大小 
    max_overflow=20,       # 可选，连接池溢出时允许的最大连接数
)

# 2.定义模型类 基类 + 表对应的模型类
# 基类：创建时间，更新时间；    书籍类：id，书名、作者、价格、出版社
class Base(DeclarativeBase):
    # 使用 server_default 让数据库处理初始值，更符合生产环境规范
    create_time: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), # 数据库自动生成
        comment="创建时间"
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime, 
        server_default=func.now(), # 初始值
        onupdate=func.now(),       # 更新时自动变动
        comment="更新时间"
    )

class Book(Base):
    __tablename__ = "book"          # 指定表名,父类的属性会被子类继承

    id: Mapped[int] = mapped_column(
        primary_key=True, 
        autoincrement=True, 
        comment="主键ID"
    )

    bookname: Mapped[str] = mapped_column(
        String(255),        # 字符串类型，最大长度为255
        comment="书名"
    )

    author: Mapped[str] = mapped_column(String(255),comment="作者")
    price: Mapped[float] = mapped_column(Float, comment="价格")
    publisher: Mapped[str] = mapped_column(String(255), comment="出版社")

# 3. 创建表: 定义函数建表 → Fastapi启动时调用建表函数

async def create_tables():
    # 获取异步引擎，创建事务 - 建表
    async with async_engine.begin() as conn:
        await conn.run_sync(
            # 通过 Base.metadata.create_all 方法创建所有继承自 Base 的模型对应的表
            Base.metadata.create_all    # 这里的create_all不能加括号
            )     
    print("数据库表同步完成")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 【启动时】执行建表操作
    await create_tables()
    yield
    # 【关闭时】释放数据库连接池
    await async_engine.dispose()
    print("数据库连接已释放")

app = FastAPI(lifespan=lifespan)

# ==================== 路由使用ORM ========================
"""
思路：创建依赖项，使用Depends注入到处理函数中
    - 创建异步会话工厂
    - 定义依赖项，用于获取数据库会话
    - 在路由处理函数中使用Depends注入数据库会话
"""

# 1. 创建异步会话工厂
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,          # 绑定异步引擎
    expire_on_commit=False,     # 可选, Fasle表示提交后会话不会过期，可以继续使用，占用数据库连接，不用查询数据库
    class_=AsyncSession         # 指定使用异步会话类
)

# 2. 定义依赖项，用于获取数据库会话，会话管理
async def get_db():
    async with AsyncSessionLocal() as session:  # 创建异步会话
        try:
            yield session               # 返回数据库会话给路由处理函数使用
            await session.commit()      # 提交事务
        except Exception as e:
            await session.rollback()    # 回滚事务
            raise e                     # 继续抛出异常，交由 FastAPI 处理
        finally:
            await session.close()       # 关闭会话，释放数据库连接

# 3. 在路由处理函数中使用Depends注入数据库会话
from fastapi import Depends
from sqlalchemy import select

@app.get("/book/books")
async def get_book_list(db: AsyncSession = Depends(get_db)):
    # 查询
    # result = await db.execute(select(Book))     # 执行查询，返回结果对象，包含了查询结果的元数据和数据
    # return result.scalars().all()               # scalars()方法提取结果中的标量值（即Book对象），all()方法将所有结果作为列表返回
    # return result.scalars().first()              # 获取单条数据，返回Book对象或None
    return await db.get(Book, 3)                      # 通过主键查询单条数据，返回Book对象或None
# ================ ORM操作数据 - 查询 =====================
"""
# 查询数据
    (1) select(模型类)     
    result = await db.execute(select(模型类))     # 执行查询，返回结果对象，包含了查询结果的元数据和数据
    result.scalars().all()          # 返回所有查询结果
    result.scalars().first()        # 获取单条数据
    result.scalar_one_or_none()     # 获取单条数据，返回模型对象或None
    result.scalar()                 # 获取单条数据的标量值，返回具体属性值或None

    (2) get(模型类，主键值)
    # 通过主键查询单条数据，返回模型对象或None

# 条件查询
    select(模型类).where(条件表达式1, 条件表达式2, ...)
    条件：
        - 比较判断：==、!=、>、<、>=、<=
        - 模糊查询：模型类.属性.like("%值%")  # 模糊匹配，%表示任意字符
        - 与非查询：&、|、~（分别表示与、或、非）
        - 包含查询: 模型类.属性.in_([值1, 值2, ...])

"""

# 比较判断 
@app.get("/book/get_book/{book_id}")
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()    # 获取单条数据，返回Book对象或None

@app.get("/book/search")
async def search_books(price: float, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.price > price))
    return result.scalars().all()        # 返回所有查询结果

# 模糊查询 和 与非查询
@app.get("/book/search_like")
async def search_books_like(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.publisher.like("%出版社%") & (Book.price < 50)))
    return result.scalars().all()        # 返回所有查询结果

# 包含查询
@app.get("/book/search_in")
async def search_books_in(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.id.in_([1, 3, 5])))
    return result.scalars().all()        # 返回所有查询结果

"""
# 聚合查询
    select(func.聚合函数(模型类.属性))     
    常用聚合函数：
        - count(): 计数
        - sum(): 求和
        - avg(): 平均值
        - max(): 最大值
        - min(): 最小值
"""

@app.get("/book/count")
async def count_books(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.avg(Book.id)))
    return result.scalar()       # 获取聚合结果，返回计数值

"""
# 分页查询
    slect(模型类).offset(偏移量).limit(每页数量)    
    偏移量 = (页码 - 1) * 每页数量
"""
@app.get("/book/page")
async def get_books_page(
    page: int = 1, 
    page_size: int = 3, 
    db: AsyncSession = Depends(get_db)
    ):
    offset = (page - 1) * page_size
    stmt = select(Book).offset(offset).limit(page_size)     #  构建分页查询语句，指定偏移量和每页数量
    result = await db.execute(stmt)
    return result.scalars().all()        # 返回当前页的查询结果列表


# ================ ORM操作数据 - 增加 =====================
"""
# 增加数据
    定义ORM对象 → session.add(ORM对象) → session.commit()

    用户采用post方法上传请求体参数

"""

from pydantic import BaseModel

# 定义请求体模型类
class Bookbase(BaseModel):
    bookname: str
    author: str
    price: float
    publisher: str

# 定义路由处理函数，接收请求体参数，并使用ORM对象进行数据增加
@app.post("/book/add_book")
async def add_book(book: Bookbase, db: AsyncSession = Depends(get_db)):
    # 定义ORM对象
    book_obj = Book(**book.model_dump())   
    
    db.add(book_obj)       # 将ORM对象添加到会话中
    await db.commit()     # 提交事务，执行插入操作
    return book


# ================ ORM操作数据 - 更新 =====================
"""
思路：
    路径参数(book_id) → 查询数据(ORM对象) → 修改ORM对象属性 → session.commit()

    采用put方法，路径参数传递book_id，请求体参数传递修改内容，使用ORM对象进行数据更新
"""
from fastapi import HTTPException

@app.put("/book/update_book/{book_id}")
async def update_book(book_id: int, book: Bookbase, db: AsyncSession = Depends(get_db)):
    book_obj = await db.get(Book, book_id)     # 通过主键查询单条数据，返回Book对象或None
    
    if not book_obj:    # 如果查询结果为None，说明没有找到对应的书籍，抛出404异常
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 修改ORM对象属性
    book_obj.bookname = book.bookname if book.bookname else book_obj.bookname
    book_obj.author = book.author if book.author else book_obj.author
    book_obj.price = book.price if book.price else book_obj.price
    book_obj.publisher = book.publisher if book.publisher else book_obj.publisher

    await db.commit()     # 提交事务，执行更新操作
    return book_obj 

# ================ ORM操作数据 - 删除 =====================
"""
思路：
    路径参数(book_id) → 查询数据(ORM对象) → session.delete(ORM对象) → session.commit()

"""

@app.delete("/book/delete_book/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    book_obj = await db.get(Book, book_id)     # 通过主键查询单条数据，返回Book对象或None
    
    if not book_obj:    # 如果查询结果为None，说明没有找到对应的书籍，抛出404异常
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(book_obj)   # 删除ORM对象
    await db.commit()           # 提交事务，执行删除操作
    return {"message": "Book deleted successfully"}
