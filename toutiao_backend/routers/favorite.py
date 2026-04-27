# === 1. 第三方库 / 核心框架组件 ===
from fastapi import APIRouter,Depends,Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

# === 2. 数据库配置与 ORM 模型 ===
from models.users import User
from config.db_config import get_db

# === 3. Pydantic 数据验证模型 (Schemas) ===
from schemas.favorite import FavoriteCheckResponse

# === 4. 业务逻辑 (CRUD 操作) 与 工具类 ===
from crud import favorite
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
    news_id: int = Query(..., alias="newsId"), 
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    # 逻辑：进入请求 → 验证用户是否登录 → 检查用户是否收藏了指定的新闻 → 响应结果
    is_favorited = await favorite.is_news_favorite(db, user.id, news_id)
    print(f"查询结果为: {is_favorited}")
    return success_response(message="检查收藏状态成功", data=FavoriteCheckResponse(isFavorite=is_favorited))

