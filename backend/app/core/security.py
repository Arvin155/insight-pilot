from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()

# ---------- 配置 ----------
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = settings.refresh_token_expire_days


# ---------- 密码 ----------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ---------- Token ----------
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成访问令牌（短）"""
    if not expires_delta:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(uid: int) -> str:
    """生成刷新令牌（长）"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(uid), "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """仅解码，不验证"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """依赖注入：校验 access token"""
    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
