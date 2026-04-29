# === 1. 第三方库 / 核心框架组件 ===
from fastapi import APIRouter,Depends, Query, HTTPException
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

# === 2. 数据库配置与 ORM 模型 ===
from models.users import User
from config.db_config import get_db

# === 3. Pydantic 数据验证模型 (Schemas) ===
from schemas.favorite import FavoriteCheckResponse,FavoriteAddRequest, FavoriteListResponse

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

@router.post("/add")    # post请求方法，请求体参数，需要定义一个Pydantic模型来验证请求体数据
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 将指定的新闻添加到用户的收藏列表 → 响应结果
    result = await favorite.add_news_favorite(db, user.id, data.news_id)
    return success_response(message="添加收藏成功", data=result)

@router.delete("/remove")    # delete请求方法，查询参数
async def remove_favorite(
    news_id: int = Query(..., alias="newsId"), 
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 将指定的新闻从用户的收藏列表中移除 → 响应结果
    is_removed = await favorite.remove_news_favorite(db, user.id, news_id)
    if not is_removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="收藏记录不存在")
    return success_response(message="移除收藏成功")

@router.get("/list")    # get请求方法，查询参数
async def get_favorite_list(
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100, alias="pageSize"), 
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 统计收藏总量 → 《联表查询收藏新闻》→ 是否有更多（下一页） → 响应结果
    rows, total =  await favorite.get_favorite_list(db, user.id, page, page_size)
    favorite_list = [{
        **news.__dict__,                    # 将ORM对象转换为字典
        "favorite_time": favorite_time,     # 添加收藏时间字段
        "favorite_id": favorite_id          # 添加收藏ID字段
    } for news, favorite_time, favorite_id in rows]  

    has_more = total > page * page_size  # 判断是否有下一页

    data = FavoriteListResponse(list=favorite_list, total=total, hasMore=has_more)  # 使用Pydantic模型进行数据验证和序列化
    return success_response(message="获取收藏列表成功", data=data)

@router.delete("/clear")                    # delete请求方法，无参数
async def clear_favorites(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 清空用户的收藏列表 → 响应结果
    count = await favorite.remove_all_favorites(db, user.id)
    return success_response(message=f"清空了 {count} 条收藏记录")