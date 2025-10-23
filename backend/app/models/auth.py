from sqlalchemy import Column, String, Boolean
from sqlmodel import Field

from app.models.base import BaseSQLModel


class User(BaseSQLModel, table=True):
    """
    用户数据模型类
    映射到MySQL数据库中的用户表
    """
    __tablename__ = "users"

    # 用户名，字符串类型，最大长度32，唯一且建立索引，不允许为空
    username: str = Field(
        sa_column=Column(String(32), unique=True, nullable=False)
    )

    # 手机号，字符串类型，最大长度255，唯一且建立索引，不允许为空
    mobile_phone: str = Field(
        sa_column=Column(String(11), unique=True, nullable=False)
    )

    # 密码哈希值，字符串类型，最大长度255，用于存储密码哈希值，不允许为空
    password_hash: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    # 是否激活，布尔类型，默认值为True，不允许为空，并建立索引
    is_active: bool = Field(
        default=True,
        sa_column=Column(Boolean, nullable=False),
        description="是否激活，布尔类型，默认值为True，不允许为空"
    )

    # 软删除标记，布尔类型，默认值为False，不允许为空，并建立索引
    is_deleted: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False),
        description="软删除标记，布尔类型，默认值为False"
    )
