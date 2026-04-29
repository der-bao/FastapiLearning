# 新闻相关的缓存方法
from config.cache_config import set_cache, get_json_cache
from typing import Dict, Any, List, Optional

# 新闻分类的读取和写入
# key - value
CATOGORIES_KEY = "news:categories"

# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATOGORIES_KEY)

# 写入新闻分类缓存
async def set_cached_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATOGORIES_KEY, data, expire)


# =================================

# 新闻列表的读取和写入
# key - value
# news_list:category_id:page:page_size

NEWS_LIST_KEY_PREFIX = "news_list:"

# 写入新闻列表缓存
async def set_cache_news_list(
    category_id: Optional[int],
    page: int,
    page_size: int,
    news_list: List[Dict[str, Any]],
    expire: int = 1800 
):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return await set_cache(key, news_list, expire)


# 获取新闻列表缓存
async def get_cache_news_list( category_id: Optional[int], page: int, page_size: int ):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{page_size}"
    return await get_json_cache(key)