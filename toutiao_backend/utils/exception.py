import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError,  SQLAlchemyError
from starlette import status

"""
# 相关知识
1. 常见的状态码
- 200 OK：请求成功
- 400 Bad Request：请求参数错误或缺失
- 401 Unauthorized：未授权，通常是认证失败
- 403 Forbidden：禁止访问，通常是权限不足
- 404 Not Found：资源不存在
- 500 Internal Server Error：服务器内部错误

2. status_code 和 code
- status_code 是 HTTP 响应的状态码，表示请求的结果类型
- code 是响应体中的业务状态码，表示具体的业务处理结果

3. 全局异常处理器
- 通过 app.add_exception_handler() 方法注册，可以捕获指定类型的异常并统一处理
- 可以捕获 HTTPException、数据库异常等常见错误，返回统一格式的错误响应
- 还可以捕获 Exception 来处理所有未捕获的异常，避免泄露敏感信息

4. 开发模式 vs 生产模式
- 开发模式：返回详细错误信息，方便调试
- 生产模式：返回简洁错误信息，避免泄露敏感信息
"""

# 开发模式：返回详细错误信息
# 生产模式：返回简洁错误信息，避免泄露敏感信息

DEBUG_MODE = True  # 设置为 False 以启用生产模式

async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTPException 异常"""
    # HTTPException 通常是业务逻辑主动抛出的，data保持None
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

async def integrity_error_handler(request: Request, exc: IntegrityError):
    """处理数据库完整性错误"""
    error_msg = str(exc.orig)   # 获取数据库原始错误信息

    # 判断具体的约束错误类型
    if "username_UNIQUE" in error_msg or  "Duplicate entry" in error_msg :
        detail = "用户名已存在"    
    elif "FOREIGN KEY" in error_msg:
        detail = "关联数据不存在"
    else:
        detail = "数据约束冲突，请检查输入"
    
    # 开发模式下返回详细错误 
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": "IntegrityError",
            "error_detail": error_msg,
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": detail,
            "data": error_data
        }
    )

async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """处理 SQLAlchemy 数据库异常"""

    # 开发模式下返回详细错误信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            # 格式化异常信息为字符串 ，方便日志记录和调试
            "traceback": traceback.format_exc(),
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "数据库操作失败，请稍后再试",
            "data": error_data
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的通用异常"""

    # 开发模式下返回详细错误信息
    error_data = None
    if DEBUG_MODE:
        error_data = {
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": traceback.format_exc(),
            "path": str(request.url)
        }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器发生错误，请稍后再试",
            "data": error_data
        }
    )