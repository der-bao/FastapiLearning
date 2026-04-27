from pydantic import BaseModel, Field

class FavoriteCheckResponse(BaseModel):
    is_favorited: bool = Field(...,alias="isFavorite", description="是否已收藏")
