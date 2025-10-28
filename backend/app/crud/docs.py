from typing import List, Tuple, Optional

from sqlalchemy.orm import Session

from app.models.knowledge import KnowledgeBase, KnowledgeDocument, KnowledgeChunk


class DocsCRUD:
    """
    文档CRUD操作类
    """

    def __init__(self, db: Session):
        self.db = db

    def get_knowledge_base_with_documents(self, knowledge_id: int) -> Optional[
        Tuple[KnowledgeBase, List[KnowledgeDocument]]]:
        """
        获取知识库及关联的文档列表

        Args:
            knowledge_id: 知识库ID

        Returns:
            包含知识库对象和文档列表的元组，如果知识库不存在则返回None
        """
        # 查询未被删除的知识库
        knowledge_base = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_id,
            KnowledgeBase.is_deleted == False
        ).first()

        if not knowledge_base:
            return None

        # 获取知识库下的所有文档
        documents = self.db.query(KnowledgeDocument).filter(
            KnowledgeDocument.knowledge_base_id == knowledge_id
        ).all()

        return knowledge_base, documents

    def create_document(self, data: dict) -> KnowledgeDocument:
        """
        创建文档记录

        Args:
            data: 包含文档信息的字典

        Returns:
            创建的文档对象
        """
        document = KnowledgeDocument(
            name=data.get('name'),
            file_path=data.get('file_path'),
            file_type=data.get('file_type'),
            file_size=data.get('file_size'),
            vector_path=data.get('vector_path'),
            chunk_count=data.get('chunk_count'),
            knowledge_base_id=data.get('knowledge_base_id'),
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def create_chunk(self, data: dict) -> KnowledgeChunk:
        """
        创建知识块记录

        Args:
            data: 包含知识块信息的字典

        Returns:
            创建的知识块对象
        """
        chunk = KnowledgeChunk(
            chunk_id=data.get('chunk_id'),
            content=data.get('content'),
            page_label=data.get('page_label'),
            chunk_index=data.get('chunk_index'),
            document_metadata=data.get('document_metadata'),
            document_id=data.get('document_id'),
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def update_document_chunk_counts(self, knowledge_id: int) -> bool:
        """
        更新知识库下所有文档的分块数量

        Args:
            knowledge_id: 知识库ID

        Returns:
            bool: 更新成功返回True，知识库不存在返回False
        """
        # 首先检查知识库是否存在且未被删除
        knowledge_base = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.id == knowledge_id,
            KnowledgeBase.is_deleted == False
        ).first()

        if not knowledge_base:
            return False

        # 获取知识库下的所有文档
        documents = self.db.query(KnowledgeDocument).filter(
            KnowledgeDocument.knowledge_base_id == knowledge_id
        ).all()

        # 为每个文档更新分块数量
        for document in documents:
            chunk_count = self.db.query(KnowledgeChunk).filter(
                KnowledgeChunk.document_id == document.id
            ).count()

            document.chunk_count = chunk_count

        self.db.commit()
        return True

    def get_document_by_id(self, document_id: int) -> Optional[KnowledgeDocument]:
        """
        根据ID获取文档

        Args:
            document_id: 文档ID

        Returns:
            文档对象，如果不存在返回None
        """
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()

    def get_chunks_by_document_id(self, document_id: int) -> List[KnowledgeChunk]:
        """
        根据文档ID获取所有知识块

        Args:
            document_id: 文档ID

        Returns:
            知识块列表
        """
        return self.db.query(KnowledgeChunk).filter(KnowledgeChunk.document_id == document_id).all()

    def delete_document(self, document_id: int) -> None:
        """
        删除指定文档

        Args:
            document_id: 文档ID
        """
        document = self.get_document_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.commit()

    def delete_chunks_by_document_id(self, document_id: int) -> None:
        """
        删除指定文档的所有chunks

        Args:
            document_id: 文档ID
        """
        chunks = self.get_chunks_by_document_id(document_id)
        for chunk in chunks:
            self.db.delete(chunk)
        self.db.commit()

    def get_documents_by_knowledge_id(self, knowledge_id: int) -> List[KnowledgeDocument]:
        """
        获取知识库中的所有文档

        Args:
            knowledge_id: 知识库ID

        Returns:
            文档列表
        """
        return self.db.query(KnowledgeDocument).filter(KnowledgeDocument.knowledge_base_id == knowledge_id).all()

    def get_knowledge_base_document_stats(self, knowledge_base_id: int) -> dict:
        """
        获取指定知识库的文档数量和分块总数

        Args:
            knowledge_base_id (int): 知识库ID

        Returns:
            dict: 包含document_count和chunk_total的字典
        """
        from app.models.knowledge import KnowledgeDocument
        from sqlalchemy import func

        # 计算文档数量
        document_count = self.db.query(func.count(KnowledgeDocument.id)).filter(
            KnowledgeDocument.knowledge_base_id == knowledge_base_id
        ).scalar()

        # 计算分块总数
        chunk_total = self.db.query(func.sum(KnowledgeDocument.chunk_count)).filter(
            KnowledgeDocument.knowledge_base_id == knowledge_base_id
        ).scalar() or 0

        return {
            "document_count": int(document_count),
            "chunk_total": int(chunk_total)
        }
