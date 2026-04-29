from pydantic import BaseModel, Field, ConfigDict
from schemas.base import NewsItemBase

from datetime import datetime

# 请求体参数

class FavoriteCheckResponse(BaseModel):
    is_favorited: bool = Field(...,alias="isFavorite", description="是否已收藏")

class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")

# 响应体参数

class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId", description="收藏ID")
    favorite_time: datetime = Field(alias="favoriteTime", description="收藏时间")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段别名进行数据验证和序列化
        from_attributes=True,   # 允许从ORM对象创建Pydantic模型实例
    )


class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field( alias="hasMore")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段别名进行数据验证和序列化
        from_attributes=True,   # 允许从ORM对象创建Pydantic模型实例
    )
 
