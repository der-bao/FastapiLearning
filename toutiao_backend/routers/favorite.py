# === 1. 第三方库 / 核心框架组件 ===
from fastapi import APIRouter,Depends,Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

# === 2. 数据库配置与 ORM 模型 ===
from models.users import User
from config.db_config import get_db

# === 3. Pydantic 数据验证模型 (Schemas) ===


# === 4. 业务逻辑 (CRUD 操作) 与 工具类 ===
from utils.auth import get_current_user
from utils.response import success_response

# =================================================



# 创建一个APIRouter实例
router = APIRouter(prefix="/api/favorite", tags=["favorite"])

# ==================================
# 路由处理函数
# ==================================

@router.get("/check")
async def check_favorite(
    new_id: int = Query(...,alias = "newId"), 
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    return success_response(message="检查收藏状态成功")