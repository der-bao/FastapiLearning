# === 1. 第三方库 / 核心框架组件 ===
from fastapi import APIRouter
from fastapi import Depends, HTTPException, Query
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

# === 2. 数据库配置与 ORM 模型 ===
from models.users import User
from config.db_config import get_db

# === 3. Pydantic 数据验证模型 (Schemas) ===
from schemas.history import HistoryAddRequest, HistoryListResponse

# === 4. 业务逻辑 (CRUD 操作) 与 工具类 ===
from crud.history import (add_news_history, get_news_history_list, 
                          delete_news_history, clear_all_history)

from utils.auth import get_current_user
from utils.response import success_response

# 创建一个APIRouter实例
router = APIRouter(prefix="/api/history", tags=["history"])

# ==================================
# 路由处理函数
# ==================================

@router.post("/add")        # post请求方法，请求体参数，需要定义一个Pydantic模型来验证请求体数据
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 判断是否已存在历史记录 → 响应结果
    result = await add_news_history(db, user.id, data.news_id)
    return success_response(message="添加历史记录成功", data=result)

@router.get("/list")        # get请求方法，查询参数
async def get_history_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100,alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 统计浏览历史总数 → 分页查询浏览历史列表《联表查询》 → 响应结果
    total_count, rows = await get_news_history_list(db, user.id, page, page_size)

    history_list = [{
        **news.__dict__,
        "view_time": view_time
    } for news, view_time in rows]

    has_more = (page * page_size) < total_count  # 是否有下一页
    data = HistoryListResponse(list=history_list, total=total_count, has_more=has_more)  # 构造响应数据
    return success_response(message="查询历史记录成功", data=data)


@router.delete("/delete/{history_id}")     # delete请求方法，查询参数
async def delete_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 删除历史记录 → 响应结果
    is_deleted = await delete_news_history(db, history_id, user.id)
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除历史记录成功")

@router.delete("/clear")     # delete请求方法，无参数
async def clear_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 逻辑：进入请求 → 验证用户是否登录 → 删除所有历史记录 → 响应结果
    count = await clear_all_history(db, user.id)  # 删除所有历史记录，返回删除的记录数
    return success_response(message=f"清空了{count}条历史记录")