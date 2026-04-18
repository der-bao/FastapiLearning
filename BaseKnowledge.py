from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/book/{book_id}")
# # Path 参数说明："..."代表必需参数, gt=0 表示 book_id 必须大于 0，lt=1000 表示 book_id 必须小于 1000
# def read_book(book_id: int = Path(...,description="The ID of the book to retrieve", gt=0, lt=1000)):
#     return {"book_id": book_id, "title": f"Book {book_id}"}

# @app.get("/news/news_list")
# async def get_news_list(
#     # Query 参数说明：skip 是一个整数，默认值为 0，表示要跳过的项目数量；limit 是一个整数，默认值为 10，表示要检索的项目数量
#     skip:int = Query(0, description="跳过的记录数"),
#     limit:int = Query(10, description="要检索的记录数")
# ):
#     return {"skip": skip, "limit": limit}

# ### 3.3 请求体参数
# class User(BaseModel):
#     name: str = Field(default="linkai", description="The name of the user")
#     password: str = Field(..., description="The password of the user", min_length=6)

# @app.post("/register")
# async def register_user(user: User):
#     return {"message": "User registered successfully", "user": user}

# class Book(BaseModel):
#     name:str = Field(..., min_length=2, max_length=20)
#     author:str = Field(min_length=2,max_length=10)
#     publisher:str = Field(default="黑马出版社")
#     price:float = Field(...,gt=0, description="The price of the book")

# @app.post("/add_book")
# async def add_book(book: Book):
#     return {"message": "Book added successfully", "book": book}

# # 4 响应 - 装饰器内指定响应类型

# from fastapi.responses import HTMLResponse

# @app.get("/html", response_class=HTMLResponse)
# async def get_html():
#     return "<h1>hello world</h1>"

# from fastapi.responses import FileResponse
# @app.get("/file")
# async def get_file():
#     return FileResponse("./image.jpg")

# # 自定义响应数据格式
# from pydantic import BaseModel

# class CustomResponse(BaseModel):
#     id: int
#     title: str
#     content: dict

# @app.get("/custom_response/{id}", response_model=CustomResponse)
# async def get_custom_response(id: int):
#     return {
#         "id": id,
#         "title": f"Custom Response {id}",
#         "content": {"message": "This is a custom response"}
#     }

# # 5 异常处理
# from fastapi import HTTPException

# @app.get("/news/{id}")
# async def get_news(id: int):
#     if id < 1 or id > 100:
#         raise HTTPException(status_code=404, detail="News item not found")
#     return {"id": id, "title": f"News {id}"}


# # 1 中间件
# @app.middleware("http")
# # request: 请求对象，包含请求的所有信息；call_next: 一个函数，用于调用下一个中间件或最终的请求处理函数
# async def middleware1(request, call_next):
#     print("中间件1 start")
#     response = await call_next(request)
#     print("中间件1 end")
#     return response 

# @app.middleware("http")
# # request: 请求对象，包含请求的所有信息；call_next: 一个函数，用于调用下一个中间件或最终的请求处理函数
# async def middleware2(request, call_next):
#     print("中间件2 start")
#     response = await call_next(request)
#     print("中间件2 end")
#     return response 

# # 2 依赖注入

# from fastapi import Depends,Query
# async def common_parameters(
#     skip: int = Query(0,ge=0),
#     limit: int = Query(10,gt=0,le=60)
# ):
#     return {"skip": skip, "limit": limit}

# @app.get("/news/new_list")
# async def get_news_list(commons=Depends(common_parameters)):
#     return commons

# @app.get("/users/user_list")
# async def get_user_list(commons=Depends(common_parameters)):
#     return commons


# ===== ORM ========
from sqlalchemy.ext.asyncio import create_async_engine 
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Integer, String, Float

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
    pubisher: Mapped[str] = mapped_column(String(255), comment="出版社")

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


