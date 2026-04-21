from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db

from fastapi import HTTPException
from starlette import status

from crud import users

# 根据token查询用户信息，返回用户
async def get_current_user(
        authorization: str = Header(..., alias = "Authorization"),
        db: AsyncSession = Depends(get_db)):
    # authorization: "Bearer <token>" 或 "<token>"
    token = authorization.split(" ")[1] if " " in authorization else authorization  
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的token或token已过期")
    return user
