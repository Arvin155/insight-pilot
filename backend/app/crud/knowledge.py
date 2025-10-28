from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeBase


class KnowledgeBaseDB:
    """
    知识库数据库操作封装类

    该类提供了对知识库进行增删改查等基本操作的封装，
    通过SQLAlchemy实现与数据库的交互。
    """

    def __init__(self, db: Session):
        """
        初始化KnowledgeBaseDB实例

        Args:
            db (Session): 数据库会话对象
        """
        self.db = db

    def get_knowledge_base_by_name(self, name: str) -> Optional[KnowledgeBase]:
        """
        根据名称获取知识库

        Args:
            name (str): 知识库名称

        Returns:
            Optional[KnowledgeBase]: 知识库对象，如果不存在则返回None
        """
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.name == name).first()

    def list_knowledge_bases_by_user(self, user_id: int):
        """
        根据用户ID获取知识库列表

        Args:
            user_id (int): 用户ID

        Returns:
            List[KnowledgeBase]: 用户拥有的知识库列表
        """
        return self.db.query(KnowledgeBase).filter(
            KnowledgeBase.owner_id == user_id
        ).all()

    def get_knowledge_base_by_id(self, kb_id: int) -> Optional[KnowledgeBase]:
        """
        根据ID获取知识库

        Args:
            kb_id (int): 知识库ID

        Returns:
            Optional[KnowledgeBase]: 知识库对象，如果不存在则返回None
        """
        return self.db.query(KnowledgeBase).filter(KnowledgeBase.id == kb_id).first()

    def create_knowledge_base(self, name: str, uuid: str, description: str, tags: List[str],
                              vector_db_type, user_id: int, chunk_size: int, chunk_overlap: int,
                              is_public: bool) -> KnowledgeBase:
        """
        创建知识库

        Args:
            name (str): 知识库名称
            uuid (str): 知识库唯一标识符
            description (str): 知识库描述
            tags (List[str]): 知识库标签列表
            vector_db_type: 向量数据库类型
            user_id (int): 所有者用户ID
            chunk_size (int): 分块大小
            chunk_overlap (int): 分块重叠大小
            is_public (bool): 是否公开

        Returns:
            KnowledgeBase: 创建的知识库对象
        """
        kb = KnowledgeBase(
            name=name,
            uuid=uuid,
            description=description,
            tags=tags,
            owner_id=user_id,
            vector_db_type=vector_db_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            query_count=0,
            is_public=is_public
        )
        self.db.add(kb)
        self.db.commit()
        self.db.refresh(kb)
        return kb

    def update_knowledge_base(self, knowledge_id: int, name: str, description: str, tags: List[str],
                              vector_db_type, chunk_size: int, chunk_overlap: int,
                              is_public: bool) -> KnowledgeBase:
        """
        更新知识库

        Args:
            knowledge_id (int): 知识库ID
            name (str): 新的知识库名称
            description (str): 新的知识库描述
            tags (List[str]): 新的标签列表
            vector_db_type: 新的向量数据库类型
            chunk_size (int): 新的分块大小
            chunk_overlap (int): 新的分块重叠大小
            is_public (bool): 新的公开状态

        Returns:
            KnowledgeBase: 更新后的知识库对象，如果不存在则返回None
        """
        kb = self.get_knowledge_base_by_id(knowledge_id)
        if kb:
            kb.name = name
            kb.description = description
            kb.tags = tags
            kb.vector_db_type = vector_db_type
            kb.chunk_size = chunk_size
            kb.chunk_overlap = chunk_overlap
            kb.is_public = is_public

            self.db.commit()
            self.db.refresh(kb)
        return kb

    def update_knowledge_base_status(self, knowledge_id: int, status: str):
        """
        更新知识库状态

        Args:
            knowledge_id (int): 知识库ID
            status (str): 新的状态值

        Returns:
            KnowledgeBase: 更新后的知识库对象，如果不存在则返回None
        """
        knowledge_base = self.db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_id).first()
        if knowledge_base:
            knowledge_base.status = status
            self.db.commit()
            self.db.refresh(knowledge_base)
        return knowledge_base
