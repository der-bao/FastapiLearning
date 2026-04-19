from fastapi import APIRouter

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from config.db_config import get_db

from schemas.users import UserRequest   #  引入用户请求模型，参数类型
from crud import users

from fastapi import HTTPException
from starlette import status


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
    
    return{
        "code": 200,
        "msg": "注册成功",
        "data": {
            "token": "用户访问令牌",
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "avatar": user.avatar
            }
        }
    }