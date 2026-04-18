from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Integer, String, Float

class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(), # 数据库自动生成
        comment="创建时间"
        )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(), # 初始值
        onupdate=func.now(),       # 更新时自动变动
        comment="更新时间"
        )

class Category(Base):
    __tablename__ = "news_category"         # !!要与数据库中的表名保持一致

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="分类ID")
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, comment="分类名称")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="排序，数值越大越靠前")

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}', sort_order={self.sort_order})"