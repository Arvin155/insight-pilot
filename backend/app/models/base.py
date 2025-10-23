from datetime import datetime, timezone
from typing import Optional

import sqlalchemy as sa
from sqlmodel import SQLModel, Field


class BaseSQLModel(SQLModel):
    """基础模型类，包含所有模型的共同字段"""
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        index=True,
        description="主键ID"
    )

    created_time: datetime = Field(
        default=datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime, nullable=False),
        description="创建时间"
    )

    updated_time: Optional[datetime] = Field(
        default=datetime.now(timezone.utc),
        sa_column=sa.Column(sa.DateTime),
        description="更新时间"
    )
