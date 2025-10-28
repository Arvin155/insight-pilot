from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session
from app.core.security import hash_password, verify_password, create_access_token
from app.crud.auth import auth_crud
from app.models.auth import User
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserChangePasswordRequest

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_200_OK)
def register(req: UserRegisterRequest, db: Session = Depends(get_session)):
    """
    用户注册接口

    Args:
        req (UserRegisterRequest): 包含用户名、手机号和密码的注册请求数据
        db (Session): 数据库会话对象

    Returns:
        JSONResponse: 注册结果响应

    Raises:
        HTTPException: 当出现各种验证失败或数据库错误时抛出相应异常
    """
    logger.info(f"开始处理用户注册请求 - 用户名: {req.username}, 手机号: {req.mobile_phone}")

    # 1. 检查用户名是否已存在
    if auth_crud.check_username_exists(db, req.username):
        logger.warning(f"注册失败 - 用户名已存在: {req.username}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在"
        )

    # 2. 检查手机号是否已存在
    if auth_crud.check_mobile_phone_exists(db, req.mobile_phone):
        logger.warning(f"注册失败 - 手机号已存在: {req.mobile_phone}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="手机号已存在"
        )

    # 3. 创建新用户对象
    logger.debug("准备创建新用户对象")
    new_user = User(
        username=req.username,
        mobile_phone=req.mobile_phone,
        password_hash=hash_password(req.password),  # 对密码进行哈希处理
        is_active=True,  # 默认激活状态
    )

    try:
        # 尝试将新用户保存到数据库
        created_user = auth_crud.create_user(db, new_user)
        logger.info(f"用户注册成功 - 用户ID: {created_user.id}, 用户名: {created_user.username}")
    except IntegrityError as e:
        # 处理数据库完整性约束错误
        db.rollback()
        logger.error(f"注册过程中发生数据库完整性错误，已回滚事务: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户数据冲突"
        )
    except Exception as e:
        # 处理其他未预期的错误
        db.rollback()
        logger.error(f"注册过程中发生未知错误，已回滚事务: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="服务器内部错误"
        )

    return JSONResponse(
        content={
            'code': status.HTTP_200_OK,
            'data': {'id': new_user.id},
            'msg': "注册成功"
        },
        status_code=status.HTTP_200_OK
    )


@router.post("/login", status_code=status.HTTP_200_OK)
def login(req: UserLoginRequest, db: Session = Depends(get_session)):
    """
    用户登录接口

    Args:
        req (UserLoginRequest): 包含手机号和密码的登录请求数据
        db (Session): 数据库会话对象

    Returns:
        JSONResponse: 登录结果及访问令牌

    Raises:
        HTTPException: 当用户不存在、密码错误或账户被禁用时抛出相应异常
    """
    logger.info(f"开始处理用户登录请求 - 手机号: {req.mobile_phone}")

    # 1. 根据手机号查找用户
    logger.debug(f"正在查询用户信息 - 手机号: {req.mobile_phone}")
    user = auth_crud.get_user_by_mobile_phone(db, req.mobile_phone)

    # 2. 验证用户是否存在
    if not user:
        logger.warning(f"登录失败 - 用户不存在: {req.mobile_phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在"
        )

    # 3. 验证密码是否正确
    logger.debug(f"正在验证用户密码 - 用户名: {user.username}")
    if not verify_password(req.password, user.password_hash):
        logger.warning(f"登录失败 - 密码错误: {req.mobile_phone}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 4. 检查账户是否处于激活状态
    if not user.is_active:
        logger.warning(f"登录失败 - 账户被禁用: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账户被禁用"
        )

    # 5. 生成访问令牌
    logger.debug("正在生成访问令牌")
    access_token_expires = timedelta(hours=settings.access_token_expire_minutes)  # 使用正确的过期时间设置
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=access_token_expires
    )
    logger.info(f"访问令牌生成成功 - 用户: {user.username}, 用户ID: {user.id}")

    # 准备登录成功的响应数据
    response_data = {
        'code': status.HTTP_200_OK,
        'data': {
            'access_token': access_token,
            'token_type': 'bearer',  # 明确令牌类型
            'user': {
                'id': user.id,
                'username': user.username,
            }
        },
        'msg': "登录成功"
    }

    logger.info(f"用户登录成功 - 用户名: {user.username}, 用户ID: {user.id}")
    return JSONResponse(
        content=response_data,
        status_code=status.HTTP_200_OK
    )


@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(
        req: UserChangePasswordRequest,
        db: Session = Depends(get_session)
):
    """
    修改用户密码接口

    Args:
        req (UserChangePasswordRequest): 包含手机号、旧密码和新密码的请求数据
        db (Session): 数据库会话对象

    Returns:
        JSONResponse: 密码修改结果响应

    Raises:
        HTTPException: 当用户不存在、旧密码错误或更新失败时抛出相应异常
    """
    logger.info(f"开始处理密码修改请求 - 手机号: {req.mobile_phone}")

    # 根据手机号获取用户信息
    logger.debug(f"正在查询用户信息 - 手机号: {req.mobile_phone}")
    user = auth_crud.get_user_by_mobile_phone(db, req.mobile_phone)

    # 检查用户是否存在
    if not user:
        logger.warning(f"密码修改失败 - 用户不存在: {req.mobile_phone}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户不存在"
        )

    # 验证旧密码是否正确
    logger.debug(f"正在验证旧密码 - 用户名: {user.username}")
    if not verify_password(req.old_password, user.password_hash):
        logger.warning(f"密码修改失败 - 旧密码错误: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )

    # 对新密码进行哈希处理并更新
    hashed_new_password = hash_password(req.new_password)
    logger.debug(f"正在对新密码进行哈希处理 - 用户名: {user.username}")

    try:
        # 更新用户密码
        updated_user = auth_crud.update_user_password(
            db,
            user.id,
            hashed_new_password
        )
        logger.info(f"用户密码修改成功 - 用户名: {updated_user.username}, 用户ID: {updated_user.id}")
    except Exception as e:
        # 处理密码更新过程中的错误
        db.rollback()
        logger.error(f"密码修改失败，已回滚事务 - 错误信息: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="修改密码失败"
        )

    # 返回密码修改成功的响应
    response_data = {
        'code': status.HTTP_200_OK,
        'data': None,
        'msg': "密码修改成功"
    }
    logger.debug(f"返回密码修改成功响应: {response_data}")
    return JSONResponse(
        content=response_data,
        status_code=status.HTTP_200_OK
    )


@router.get("/check-mobile", status_code=status.HTTP_200_OK)
def check_mobile_phone_unique(mobile_phone: str, db: Session = Depends(get_session)):
    """检查手机号是否唯一"""
    logger.debug(f"检查手机号唯一性: {mobile_phone}")

    try:
        # 检查手机号是否存在
        exists = auth_crud.check_mobile_phone_exists(db, mobile_phone)

        logger.success(f"手机号唯一性检查结果: {mobile_phone} -> {exists}")

        return JSONResponse(
            content={
                'code': status.HTTP_200_OK,
                'data': {'exists': exists},
                'msg': "查询成功"
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"手机号唯一性检查失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="手机号唯一性检查失败"
        )
