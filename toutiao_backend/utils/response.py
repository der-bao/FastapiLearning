from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def success_response(message: str="success", data=None):
    """
    统一成功响应结构
    
    该设计的作用：
    - 统一返回格式：保证所有接口具有固定的 code/msg/data 结构，方便前端拦截与解析。
    - 兼容复杂类型：支持直接传递 Pydantic schema 模型或 ORM 对象。
    """
    content = {
        "code": 200,
        "msg": message,
        "data": data
    }
    # jsonable_encoder: 负责将 Pydantic 模型、ORM 对象、datetime 等复杂类型转为可 JSON 序列化的基础类型（dict/list 等）。
    # JSONResponse: 接收基础类型，序列化为 JSON 字符串并返回，同时自动设置 Content-Type 为 application/json。
    return JSONResponse(content=jsonable_encoder(content))