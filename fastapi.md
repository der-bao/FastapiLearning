# 一、Fastapi基础

## 1. 基础入门

```
# 基础程序
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/{name}")
def read_name(name: str):
    return {"Hello": name}

# 运行 --reload 代表会自动刷新web   -- port 指定端口 
uv run uvicorn main:app --reload --port 8444  

# 访问 http://127.0.0.1:8000/docs 可以打开交互式文档
```

## 2. 路由

路由就是URL地址和处理函数之间的映射关系，它决定了当用户访问某个特定网址时，服务器应该执行哪段代码来返回结果。

```
# 语法：@app.get("/") 采用该装饰器修饰函数
    app 是Fastapi实例
    get 是请求方法
    "/" 是请求路径

# 示例
@app.get("/{name}")
def read_name(name: str):
    return {"Hello": name}
```

## 3. 参数

参数就是客户端发送请求时附带的**额外信息和指令**，同一段接口逻辑，根据参数不同返回不同的数据。
一般有如下类型:

1. 路径参数
   - 位置：URL路径的一部分如"/book/{book_id}"
   - 作用：指向唯一的资源
   - 请求方法：GET
2. 查询参数
   - 位置：URL中"?"以后的部分如"?k1=v1&k2=v2"
   - 作用：对资源集合进行过滤、排序和分页等操作
   - 请求方法：GET
3. 请求体
   - 位置：HTTP请求的消息体（body）中
   - 作用：创建、更新资源，携带大量数据如json
   - 请求方法：POST、PUT

### 3.1 路径参数

Path是一个特殊的参数类型，用于定义路径参数。它允许我们在URL路径中捕获变量，并将其作为函数参数传递给处理请求的函数。在下面的代码中，我们使用Path来定义了一个名为book_id的路径参数，它是一个整数类型。当用户访问/book/{book_id}时，book_id的值将被捕获并传递给read_book函数。

```
@app.get("/book/{book_id}")
# Path 参数说明："..."代表必需参数, gt=0 表示 book_id 必须大于 0，lt=1000 表示 book_id 必须小于 1000
def read_book(book_id: int = Path(...,description="The ID of the book to retrieve", gt=0, lt=1000)):
    return {"book_id": book_id, "title": f"Book {book_id}"}

# Path的常见参数如下：
- ...   必填
- gt/gt  大于/大于等于
- lt/le  小于/小于等于
- description 描述
- min_length 
- max_length
```

### 3.2 查询参数

Query() 和 Path() 类似

### 3.3 请求体参数

在HTTP协议中，一个完整的请求由三部分组成:

1. 请求行:包含方法、URL、协议版本
2. 请求头:元数据信息(Content-Type、Authorization等)
3. **请求体**:实际要发送的数据内容

```
示例：
class User(BaseModel):
    name: str
    password: str

@app.post("/register")
async def register_user(user: User):
    return {"message": "User registered successfully", "user": user}
```

Field（）方法和之前类似，不同之处在于Field方法是从pydantic包导入

## 4. 响应

响应类型有如下类别：

- JSONResponse
- HTMLResponse
- PlainTextResponse
- FileResponse
- StreamingResponse
- RedirectResponse

通过 `from fastapi.responses import HTMLResponse`导入

响应类型设置方法有如下两种：

- 直接在装饰器中指定响应类(适用场景：固定返回类型如HTML，纯文本)

```
from fastapi.responses import HTMLResponse
@app.get("/html", response_class=HTMLResponse)
async def get_html():
    return "<h1>hello world</h1>"
```

- 返回响应对象（适用场景：文件下载、图片、流式响应）

```
from fastapi.responses import FileResponse
@app.get("/file")
async def get_file():
    return FileResponse("./image.jpg")
```

补充：当想要自定义响应数据格式时，可以采用如下方法实现：

```
from pydantic import BaseModel

class CustomResponse(BaseModel):
    id: int
    title: str
    content: dict

@app.get("/custom_response/{id}", response_model=CustomResponse)
async def get_custom_response(id: int):
    return {
        "id": id,
        "title": f"Custom Response {id}",
        "content": {"message": "This is a custom response"}
    }
```

## 5. 异常处理

```
from fastapi import HTTPException

@app.get("/news/{id}")
async def get_news(id: int):
    if id < 1 or id > 100:
        raise HTTPException(status_code=404, detail="News item not found")
    return {"id": id, "title": f"News {id}"}
```

# 二、Fastapi进阶

## 1. 中间件

为每一个请求添加统一的处理逻辑。
中间件会在**请求**到达路由前运行一次，并且在**响应**返回给客户端之前再运行一次。（洋葱模型，后定义的中间件在最外层）

```
@app.middleware("http")
# request: 请求对象，包含请求的所有信息；call_next: 一个函数，用于调用下一个中间件或最终的请求处理函数
async def middleware1(request, call_next):
    print("中间件1 start")
    response = await call_next(request)
    print("中间件1 end")
    return response 

@app.middleware("http")
# request: 请求对象，包含请求的所有信息；call_next: 一个函数，用于调用下一个中间件或最终的请求处理函数
async def middleware2(request, call_next):
    print("中间件2 start")
    response = await call_next(request)
    print("中间件2 end")
    return response 
```

## 2. 依赖注入

- 依赖项：可**重用**的组件（函数/类），负责提供某种功能或数据。
- 注入：Fastapi会自动帮你调用依赖项，并将结果"注入"到路由函数中
- 中间件会处理所有的请求，而依赖注入只处理部分指定的路由函数。

```
# 创建依赖项
async def common_parameters(
    skip: int = Query(0,ge=0),
    limit: int = Query(10,gt=0,le=60)
):
    return {"skip": skip, "limit": limit}

# 导入Depends
from fastapi import Depends,Query

# 声明依赖项
@app.get("/news/new_list")
async def get_news_list(commons=Depends(common_parameters)):
    return commons

@app.get("/users/user_list")
async def get_user_list(commons=Depends(common_parameters)):
    return commons
```

## 3. ORM

ORM(Object-RelationalMapping，对象关系映射)是一种编程技术，用于在面向对象编程语言和关系型数据库之间建立映射。它允许开发者通过操作对象的方式与数据库进行交互，而**无需直接编写复杂的SQL语句**。
优势:

- 减少重复的SQL代码
- 代码简洁
- 自动处理数据库连接和事务
- 自动防止SQL注入攻击

### (1) 安装

```
# sqlalchemy[asyncio]是 python的ORM，[asyncio]是对应的异步拓展
# 基于 asyncio 的 MySQL 驱动程序。
uv add sqlalchemy[asyncio] aiomysql
```

### (2) 建库、建表

```
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
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
```

### (3) 在路由中使用ORM
```

```



# 三、项目相关知识
## 1. 模块化路由
```
from fastapi import APIRouter

# 1. 创建一个APIRouter实例
router = APIRouter(prefix="/api/news", tags=["news"])

# 2. 路由处理函数

@router.get("/categories")
async def get_categories():
    return {"msg": "获取新闻分类成功"}

# 3. 在main文件中导入并注册路由
from routers import news  # 导入news模块的路由
app.include_router(news.router) # 注册news模块的路由
```