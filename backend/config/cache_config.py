"""
# redis客户端配置文件
"""
from redis.asyncio import Redis
import json


REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# 创建 Redis 的连接对象
redis_client = Redis(
    host=REDIS_HOST,       # Redis 服务器地址
    port=REDIS_PORT,       # Redis 默认端口
    db=REDIS_DB,           # 使用默认数据库
    decode_responses=True  # 以字符串形式返回结果，默认是字节类型
)

# 封装缓存操作
# 1、设置缓存
async def set_cache(key: str, value, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)  # 序列化：将 Python 对象（如列表或字典）转换为 JSON 字符串
        await redis_client.setex(key, expire, value)  # 设置缓存并指定过期时间
        return True
    except Exception as e:
        print(f"设置缓存失败: {e}")
        return False

# 2.1、读取缓存(字符串)
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败: {e}")
        return None

# 2.2、读取缓存(列表或字典)
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)     # 反序列化：将 JSON 字符串转换回 Python 对象（如列表或字典）
        return None
    except Exception as e:
        print(f"获取JSON缓存失败: {e}")
        return None

# 3、删除缓存
# TODO