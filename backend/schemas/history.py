from pydantic import BaseModel, Field, ConfigDict
from schemas.base import NewsItemBase
from datetime import datetime


# 请求体参数
class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")

# 响应体参数

class HistoryNewsItemResponse(NewsItemBase):
    view_time: datetime = Field(alias="viewTime", description="浏览时间")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段别名进行数据验证和序列化
        from_attributes=True,   # 允许从ORM对象创建Pydantic模型实例
    )

class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore", description="是否有下一页")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段别名进行数据验证和序列化
        from_attributes=True,   # 允许从ORM对象创建Pydantic模型实例
    )