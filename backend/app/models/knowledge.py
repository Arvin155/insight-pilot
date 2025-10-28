from enum import Enum
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, JSON, Enum as SQLEnum
from sqlmodel import Field, Relationship

from app.models.base import BaseSQLModel


class VectorDatabaseType(Enum):
    CHROMA = "chroma"
    MILVUS = "milvus"


class KnowledgeBaseStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class KnowledgeBase(BaseSQLModel, table=True):
    __tablename__ = "knowledge_bases"

    name: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="知识库名称"
    )
    uuid: str = Field(
        sa_column=Column(String(36), nullable=False),
        description="知识库UUID，全局唯一标识符"
    )

    description: Optional[str] = Field(
        sa_column=Column(Text),
        description="知识库描述"
    )

    tags: List[str] = Field(
        default=[],
        sa_column=Column(JSON),
        description="知识库标签"
    )

    owner_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id")),
        description="知识库拥有者ID"
    )

    # 切片配置
    chunk_size: int = Field(
        default=1024,
        sa_column=Column(Integer),
        description="切片大小"
    )

    chunk_overlap: int = Field(
        default=20,
        sa_column=Column(Integer),
        description="切片重叠"
    )

    # 使用的向量数据库类型
    vector_db_type: Optional[VectorDatabaseType] = Field(
        sa_column=Column(
            SQLEnum(VectorDatabaseType, name="vectordatabasetype"),
        ),
        description="使用的向量数据库类型，如FAISS或Chroma"
    )

    status: KnowledgeBaseStatus = Field(
        default=KnowledgeBaseStatus.ACTIVE,
        sa_column=Column(
            SQLEnum(KnowledgeBaseStatus, name="knowledgebasestatus"),
            nullable=False,
        ),
        description="知识库状态"
    )

    # 查询次数
    query_count: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False),
        description="知识库被查询的次数统计"
    )

    is_public: bool = Field(
        default=True,
        sa_column=Column(Boolean),
        description="知识库是否公开"
    )

    # 软删除标记，布尔类型，默认值为False，不允许为空，并建立索引
    is_deleted: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False),
        description="软删除标记，布尔类型，默认值为False"
    )

    # 建议添加到 KnowledgeBase 类中
    documents: List["KnowledgeDocument"] = Relationship(back_populates="knowledge_base")


class KnowledgeDocument(BaseSQLModel, table=True):
    __tablename__ = 'knowledge_documents'

    # 文档名称
    name: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="文档名称"
    )
    # 文件路径或URL
    file_path: str = Field(
        sa_column=Column(Text, nullable=False),
        description="文档文件路径或URL地址"
    )

    # 文件类型
    file_type: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="文档文件类型，如PDF、TXT等"
    )

    # 文件大小
    file_size: str = Field(
        sa_column=Column(String(50), nullable=False),
        description="文档文件大小"
    )

    # 向量路径
    vector_path: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="文档向量存储路径"
    )

    # 分块数量
    chunk_count: int = Field(
        default=0,
        sa_column=Column(Integer, nullable=False),
        description="文档被分块的数量"
    )

    # 所属知识库ID（外键）
    knowledge_base_id: int = Field(
        sa_column=Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False),
        description="所属知识库ID，外键关联"
    )

    # 关联的知识库
    knowledge_base: "KnowledgeBase" = Relationship(back_populates="documents")

    # 知识块
    chunks: List["KnowledgeChunk"] = Relationship(back_populates="document")


class KnowledgeChunk(BaseSQLModel, table=True):
    """
    知识块表
    将文档切分为小块存储，便于检索和RAG使用
    """
    __tablename__ = 'knowledge_chunks'

    chunk_id: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Chroma/Milvus生成的唯一ID"
    )
    # 知识块内容
    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="知识块内容文本"
    )
    page_label: str = Field(
        sa_column=Column(String(255), nullable=False),
        description="文档页码标签"
    )
    chunk_index: int = Field(
        sa_column=Column(Integer, nullable=False),
        description="块索引，从0开始"
    )

    document_metadata: str = Field(
        sa_column=Column(Text, nullable=False),
        description="元数据，可以存储为JSON字符串或二进制数据"
    )

    # 文档ID（外键）
    document_id: int = Field(
        sa_column=Column(Integer, ForeignKey("knowledge_documents.id"), nullable=False),
        description="所属文档ID，外键关联"
    )

    # 关联的文档
    document: "KnowledgeDocument" = Relationship(back_populates="chunks")
