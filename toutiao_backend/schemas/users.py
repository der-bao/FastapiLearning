from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserRequest(BaseModel):
    username: str
    password: str


# 响应模板的data的参数类型
# 用户信息响应
class UserInfoBase(BaseModel):
    """用户信息基础模型，包含用户的基本属性"""
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")


class UsersInfoResponse(UserInfoBase):
    id: int
    username: str

    # 模型类配置
    model_config = ConfigDict(
        # 允许从对象属性获取数据，适用于ORM对象
        from_attributes=True
    )

# 用户认证响应
class UserAuthResponse(BaseModel):
    token: str
    #  使用别名userInfo来映射响应中的userInfo字段，保持与前端约定一致
    user_info: UsersInfoResponse = Field(..., alias="userInfo")

    # 模型类配置 
    model_config = ConfigDict(
        # 允许通过字段名或别名来创建模型实例，方便从不同来源（如请求体、ORM对象）获取数据
        populate_by_name=True,
        # 允许从对象属性获取数据，适用于ORM对象
        from_attributes=True
    )

# 更新用户信息的模型类
class UserUpdateRequest(UserInfoBase):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None

# 修改密码请求模型
class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., description="旧密码", alias="oldPassword")
    new_password: str = Field(..., description="新密码", alias="newPassword", min_length=6) 


