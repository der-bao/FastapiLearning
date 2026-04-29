import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from sqlalchemy import update


from models.users import User, UserToken
from schemas.users import UserRequest, UserUpdateRequest

from utils import security

from fastapi import HTTPException
from starlette import status

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

# 验证用户登录信息，返回用户对象或None
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    # 验证用户是否存在和密码是否正确
    if not user:
        return None
    if not security.verify_password(password, user.password):  
        # user.password是数据库中存储的哈希密码
        return None
    return user

# 根据token查询用户信息
async def get_user_by_token(db: AsyncSession, token: str):
    # 查询token对应的用户
    stmt = select(UserToken).where(UserToken.token == token, UserToken.expires_at > datetime.now())
    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()  # 获取单个结果，如果没有则返回None

    if not db_token:
        return None
    
    query = select(User).where(User.id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 更新用户信息
async def update_user_info(db: AsyncSession, user_data: UserUpdateRequest, username: str):
    # user_data是一个Pydantic模型实例，先转换为字典，排除 ,然后再解构
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,     # 只包含用户提供的字段
        exclude_none=True       # 排除值为None的字段
    ))
    result = await db.execute(query)
    await db.commit()  # 提交事务

    # 检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户未找到")
    return await get_user_by_username(db, username)  # 返回更新后的用户信息

    # 获取更新后的用户信息
    updated_user = await get_user_by_username(db, username)
    return updated_user

# 修改密码: 验证旧密码 -> 新密码加密 -> 修改密码 
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    # 验证旧密码是否正确
    if not security.verify_password(old_password, user.password):  
        return False
    # 新密码加密
    hashed_new_password = security.get_hash_password(new_password)
    user.password = hashed_new_password
    await db.commit()  # 提交事务
    await db.refresh(user)  # 刷新对象以获取最新信息
    return True