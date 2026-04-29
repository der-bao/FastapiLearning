from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from utils.exception import http_exception_handler, integrity_error_handler, sqlalchemy_error_handler
from utils.exception import general_exception_handler 

def register_exception_handler(app):
    """ 注册全局异常处理器 """
    # add_exception_handler() 方法用于注册异常处理器
    # add_exception_handler 的第一个参数是异常类型，第二个参数是处理该异常的函数
    app.add_exception_handler(HTTPException, http_exception_handler)        # 业务
    app.add_exception_handler(IntegrityError, integrity_error_handler)      # 数据库完整性错误
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)    # 其他数据库错误
    app.add_exception_handler(Exception, general_exception_handler)         # 捕获所有未处理的异常，避免泄露敏感信息
