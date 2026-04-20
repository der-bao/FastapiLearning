import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import update


from models.users import User, UserToken
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
async def create_token(db: AsyncSession, user_id: int):
    # 生成token + 设置过期时间 → 查询数据库当前用户是否有token → 没有则添加token，有则更新token
    token = str(uuid.uuid4())  # 生成唯一的token字符串
    expires_at = datetime.now() + timedelta(days=7)  # 设置过期时间为7天后

    # 查询数据库当前用户是否有token
    stmt = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    user_token = result.scalar_one_or_none()

    if user_token:
        # 更新token和过期时间
        stmt = update(UserToken).where(UserToken.user_id == user_id).values(token=token, expires_at=expires_at)
        await db.execute(stmt) 
    else:
        # 创建新的token记录
        new_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(new_token)

    await db.commit()  # 提交事务
    return token

