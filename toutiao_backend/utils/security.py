"""

"""

from passlib.context import CryptContext

# 创建加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], # bcrypt算法进行密码加密
                           deprecated="auto")  # 自动处理过时的算法

# 密码加密
def get_hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 密码验证
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)