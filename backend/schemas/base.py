from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")   # category_id字段，使用别名categoryId进行数据验证和序列化
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")

    model_config = ConfigDict(
        populate_by_name=True,  # 允许使用字段别名进行数据验证和序列化
        from_attributes=True,   # 允许从ORM对象创建Pydantic模型实例
    )
