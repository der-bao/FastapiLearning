from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import update

from models.users import User
from schemas.users import UserRequest

from utils import security


# 根据用户名名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  # 获取单个结果，如果没有则返回None

# 创建新用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 加密密码
    hashed_password = security.get_hash_password(user_data.password)
    # 得到ORM对象
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)  # 添加到数据库会话
    await db.commit()  # 提交事务
    await db.refresh(user)  # 刷新对象以获取数据库生成的ID等信息
    return user

# 生成访问令牌
"""
- Token:是服务器发给客户端的一段字符串，用来在后续请求中证明“你已经登录过了”
- 作用:解决HTTP是无状态的问题，在每次请求中“自我证明身份”
"""

