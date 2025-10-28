from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, knowledge, docs
from app.middleware.exception_middleware import ExceptionMiddleware
from app.middleware.logger_middleware import LoggingMiddleware

app = FastAPI(title="智能数据洞察平台")

# 1. 日志中间件 - 最外层，记录所有请求和响应
app.add_middleware(LoggingMiddleware)

# 2. CORS中间件 - 处理跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 异常处理中间件 - 最内层，捕获所有异常
app.add_middleware(ExceptionMiddleware)

# 挂载路由
app.include_router(auth.router)
app.include_router(knowledge.router)
app.include_router(docs.router)
