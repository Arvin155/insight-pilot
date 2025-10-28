from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from app.models.knowledge import VectorDatabaseType


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(
        ...,
        title="知识库名称",
        max_length=50,
        description="知识库名称"
    )
    description: Optional[str] = Field(
        None,
        title="知识库描述",
        max_length=500,
        description="知识库的详细描述"
    )
    tags: List[str] = Field(
        default=[],
        title="知识库标签",
        description="知识库的标签列表"
    )
    user_id: int = Field(
        ...,
        title="拥有者ID",
        description="知识库拥有者的用户ID"
    )
    chunk_size: int = Field(
        default=1024,
        title="切片大小",
        description="文档切片的大小"
    )
    chunk_overlap: int = Field(
        default=20,
        title="切片重叠",
        description="文档切片之间的重叠大小"
    )
    vector_db_type: Optional[str] = Field(
        default=VectorDatabaseType.MILVUS,
        title="向量数据库类型",
        description="使用的向量数据库类型，如faiss, chroma, milvus"
    )
    is_public: bool = Field(
        default=True,
        title="是否公开",
        description="知识库是否公开可见"
    )

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError('标签数量不能超过10个')
        return v


class KnowledgeBaseUpdate(BaseModel):
    id: int = Field(
        None,
        title="知识库ID",
        description="知识库ID"
    )
    name: Optional[str] = Field(
        None,
        title="知识库名称",
        max_length=50,
        description="知识库名称"
    )
    description: Optional[str] = Field(
        None,
        title="知识库描述",
        max_length=500,
        description="知识库的详细描述"
    )
    tags: Optional[List[str]] = Field(
        None,  # 移除默认值
        title="知识库标签",
        description="知识库的标签列表"
    )
    chunk_size: Optional[int] = Field(
        None,
        title="切片大小",
        description="文档切片的大小"
    )
    chunk_overlap: Optional[int] = Field(
        None,
        title="切片重叠",
        description="文档切片的重叠大小"
    )
    vector_db_type: Optional[VectorDatabaseType] = Field(
        None,
        title="向量数据库类型",
        description="使用的向量数据库类型，如FAISS或Chroma"
    )
    is_public: Optional[bool] = Field(
        None,
        title="是否公开",
        description="知识库是否公开"
    )

    @field_validator('tags')
    def validate_tags(cls, v):
        if v is not None and len(v) > 10:
            raise ValueError('标签数量不能超过10个')
        return v


class KnowledgeStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        title="知识库状态",
        description="知识库状态"
    )
    id: int = Field(
        ...,
        title="知识库ID",
        description="知识库ID"
    )
