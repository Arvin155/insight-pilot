import os
import sys
import time
import uuid
from contextvars import ContextVar

import loguru
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint

from app.core.config import settings

# 创建上下文变量来存储当前请求的额外信息
current_request_info: ContextVar[dict] = ContextVar('current_request_info', default={})


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = self.setup_logger()
        self._patch_loguru_logger()

    def setup_logger(self):
        """配置loguru日志记录器"""
        # 确保日志目录存在
        log_dir = settings.log_file_path
        os.makedirs(log_dir, exist_ok=True)

        # 移除默认的控制台处理器
        loguru.logger.remove()

        # 添加控制台处理器
        loguru.logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | "
                   "<cyan>{extra[request_id]}</cyan> | <yellow>{extra[method]} {extra[path]}</yellow> | "
                   "Status: <magenta>{extra[status_code]}</magenta> | Duration: <blue>{extra[duration]}ms</blue> | "
                   "IP: <cyan>{extra[client_ip]}</cyan> | {message}",
            level="INFO",
            filter=lambda record: 'request_id' in record['extra'] and 'method' in record['extra']
        )

        # 添加控制台处理器 - 通用日志
        loguru.logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | "
                   "<cyan>{name}:{function}:{line}</cyan> | {message}",
            level="INFO",
            filter=lambda record: 'request_id' not in record['extra'] or 'method' not in record['extra']
        )

        # 添加文件处理器 - 访问日志
        loguru.logger.add(
            os.path.join(log_dir, "access.log"),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]:<36} | {extra[method]:<6} {extra[path]} | "
                   "Status: {extra[status_code]} | Duration: {extra[duration]}ms | "
                   "User-Agent: {extra[user_agent]} | IP: {extra[client_ip]} | "
                   "Response Size: {extra[response_size]} bytes | {message}",
            level="INFO",
            filter=lambda record: 'request_id' in record['extra'] and 'method' in record['extra']
        )

        # 添加通用日志文件处理器
        loguru.logger.add(
            os.path.join(log_dir, "general.log"),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
            level="INFO",
            filter=lambda record: 'request_id' not in record['extra'] or 'method' not in record['extra']
        )

        # 添加错误日志文件处理器
        loguru.logger.add(
            os.path.join(log_dir, "error.log"),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {extra[request_id]:<36} | {extra[method]:<6} {extra[path]} | "
                   "Status: {extra[status_code]} | Duration: {extra[duration]}ms | "
                   "User-Agent: {extra[user_agent]} | IP: {extra[client_ip]} | "
                   "Error: {message}",
            level="ERROR",
            filter=lambda record: 'request_id' in record['extra'] and 'method' in record['extra']
        )

        # 添加通用错误日志文件处理器
        loguru.logger.add(
            os.path.join(log_dir, "error.log"),
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message}",
            level="ERROR",
            filter=lambda record: 'request_id' not in record['extra'] or 'method' not in record['extra']
        )

        return loguru.logger

    def _patch_loguru_logger(self):
        """猴子补丁loguru.logger，使其自动绑定当前请求信息"""

        class AutoBindingLogger:
            def __init__(self, original_logger):
                self._original_logger = original_logger
                self._level_cache = {}

            def _get_bound_logger(self):
                request_info = current_request_info.get({})
                if request_info:
                    return self._original_logger.bind(**request_info)
                return self._original_logger

            def __getattr__(self, name):
                # 对于级别方法（debug, info等），返回自动绑定的版本
                if name in ['debug', 'info', 'success', 'warning', 'error', 'critical']:
                    if name not in self._level_cache:
                        def level_method(*args, **kwargs):
                            bound_logger = self._get_bound_logger()
                            method = getattr(bound_logger, name)
                            return method(*args, **kwargs)

                        self._level_cache[name] = level_method

                    return self._level_cache[name]

                # 对于其他方法，直接代理给原始logger
                return getattr(self._original_logger, name)

        # 替换全局logger
        loguru.logger = AutoBindingLogger(loguru.logger)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 生成请求ID
        request_id = str(uuid.uuid4())

        # 记录请求开始时间
        start_time = time.time()

        # 获取客户端IP
        client_ip = self._get_client_ip(request)

        # 创建请求上下文信息
        request_info = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "full_url": str(request.url),
            "client_ip": client_ip,
            "user_agent": request.headers.get("user-agent", "Unknown"),
            "request_headers": dict(request.headers),
            "query_params": dict(request.query_params),
        }

        # 设置上下文变量
        token = current_request_info.set(request_info.copy())

        # 添加请求ID到请求状态，便于在其他地方使用
        request.state.request_id = request_id

        try:
            # 执行请求
            response = await call_next(request)

            # 计算请求耗时
            duration = (time.time() - start_time) * 1000  # 转换为毫秒

            # 获取响应体大小
            response_size = self._get_response_size(response)

            # 更新请求上下文信息
            request_info.update({
                "status_code": response.status_code,
                "duration": round(duration, 2),
                "response_size": response_size,
            })
            current_request_info.set(request_info)

            # 记录访问日志
            access_logger = loguru.logger.bind(**request_info)
            if response.status_code >= 400:
                access_logger.error(f"Request completed with status {response.status_code}")
            else:
                access_logger.info(f"Request completed successfully")

            return response

        except Exception as exc:
            # 计算请求耗时
            duration = (time.time() - start_time) * 1000  # 转换为毫秒

            # 更新请求上下文信息
            request_info.update({
                "status_code": 500,
                "duration": round(duration, 2),
                "response_size": 0,
            })
            current_request_info.set(request_info)

            # 记录错误日志
            error_logger = loguru.logger.bind(**request_info)
            error_logger.error(f"Request failed with exception: {str(exc)}")

            # 重新抛出异常，让FastAPI处理
            raise exc
        finally:
            # 清理上下文变量
            current_request_info.reset(token)

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 尝试从X-Forwarded-For头部获取真实IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # 尝试从X-Real-IP头部获取
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # 使用客户端主机信息
        if hasattr(request.client, 'host'):
            return request.client.host
        return "Unknown"

    def _get_response_size(self, response: Response) -> int:
        """获取响应体大小"""
        try:
            # 尝试从Content-Length头部获取
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)

            # 如果没有Content-Length，尝试从响应体获取
            if hasattr(response, 'body') and response.body:
                return len(response.body)

            return 0
        except:
            return 0
