import traceback

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware


# 异常处理中间件
class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except HTTPException as http_exc:
            # 统一处理 HTTPException，转换为你的标准响应格式
            logger.error(f"业务异常: {http_exc.detail}")
            return JSONResponse(
                status_code=http_exc.status_code,
                content={
                    'code': http_exc.status_code,
                    'msg': http_exc.detail,
                }
            )

        except ValidationError as ve:
            # 处理Pydantic验证错误
            logger.error(f"数据验证错误: {str(ve)}")
            return JSONResponse(
                status_code=422,
                content={
                    'code': 422,
                    'msg': "请求数据验证失败",
                }
            )

        except Exception as exc:
            # 处理所有其他异常
            logger.error(f"未处理异常: {str(exc)}")
            logger.error(traceback.format_exc())

            return JSONResponse(
                status_code=500,
                content={
                    'code': 500,
                    'msg': "服务器内部错误，请稍后重试",
                }
            )
