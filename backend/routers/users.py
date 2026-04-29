# === 1. 第三方库 / 核心框架组件 ===
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

# === 2. 数据库配置与 ORM 模型 ===
from config.db_config import get_db
from models.users import User

# === 3. Pydantic 数据验证模型 (Schemas) ===
from schemas.users import (
    UserRequest,                 # 用户请求模型 (如登录/注册参数)
    UserAuthResponse,            # 认证响应模型
    UsersInfoResponse,           # 用户信息响应模型
    UserUpdateRequest,           # 用户更新请求模型
    UserChangePasswordRequest    # 修改密码请求模型
)

# === 4. 业务逻辑 (CRUD 操作) 与 工具类 ===
from crud import users
from utils.response import success_response
from utils.auth import get_current_user


router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    #  注册逻辑：验证用户是否存在 -> 创建用户 -> 生成访问令牌 -> 返回响应
    # 验证用户是否存在
    existing_user = await users.get_user_by_username(db, user_data.username)  # 查询用户是否存在
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    # 创建用户
    user = await users.create_user(db, user_data) 
    # 生成访问令牌
    token = await users.create_token(db, user.id)
    # return{
    #     "code": 200,
    #     "msg": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar
    #         }
    #     }
    # }
    response_data = UserAuthResponse(token=token, user_info=UsersInfoResponse.model_validate(user))  # 直接传递ORM对象，Pydantic会自动转换
    return success_response(message="注册成功", data=response_data)


@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在 -> 验证密码 -> 生成访问令牌 -> 返回响应
    #  验证用户是否存在和密码是否正确
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    # 生成访问令牌
    token = await users.create_token(db, user.id)

    response_data = UserAuthResponse(token=token, user_info=UsersInfoResponse.model_validate(user))  # 直接传递ORM对象，Pydantic会自动转换
    return success_response(message="登录成功", data=response_data)

@router.get("/info")
async def get_user_info(user: User = Depends(get_current_user)):
    # 获取用户信息逻辑：验证访问令牌 -> 获取用户信息 -> 返回响应
    return success_response(message="获取用户信息成功", data=UsersInfoResponse.model_validate(user))

@router.put("/update")
async def update_user(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 更新用户信息逻辑：验证访问令牌 -> 更新用户信息 -> 返回响应
    updated_user = await users.update_user_info(db, user_data, user.username)  # 更新用户信息
    return success_response(message="更新用户信息成功", data=UsersInfoResponse.model_validate(updated_user))

@router.put("/password")
async def update_password(
    password_data: UserChangePasswordRequest, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    res_change_pwd = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="修改密码失败，旧密码错误")
    return success_response(message="修改密码成功")