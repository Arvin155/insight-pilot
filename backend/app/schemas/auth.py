import re

from pydantic import BaseModel, Field, field_validator


# 用户注册请求参数
class UserRegisterRequest(BaseModel):
    # 必填字段 - 使用 ...
    username: str = Field(
        ...,
        title="用户名",
        max_length=32,
        description="用户名"
    )
    mobile_phone: str = Field(
        ...,
        title="手机号",
        max_length=11,
        description="手机号"
    )
    password: str = Field(
        ...,
        title="密码",
        description="密码"
    )

    @field_validator("mobile_phone")
    def validate_mobile_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v


# 用户登录请求参数
class UserLoginRequest(BaseModel):
    mobile_phone: str = Field(
        ...,
        title="手机号",
        max_length=11,
        description="手机号"
    )
    password: str = Field(
        ...,
        title="密码",
        description="密码"
    )


class UserChangePasswordRequest(BaseModel):
    mobile_phone: str = Field(
        ...,
        title="手机号",
        max_length=11,
        description="手机号"
    )
    old_password: str = Field(
        ...,
        title="旧密码",
        description="旧密码"
    )
    new_password: str = Field(
        ...,
        title="新密码",
        description="新密码"
    )