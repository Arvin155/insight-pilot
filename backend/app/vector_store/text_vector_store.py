from typing import List
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_milvus import Milvus
from loguru import logger

from app.core.config import settings
from app.llm.model_client import get_embeddings


class TextVectorStore:
    """
    文本向量存储类，支持多种向量数据库
    """

    def __init__(self, store_type: str, collection_name: str):
        """
        初始化文本向量存储

        Args:
            store_type: 向量数据库类型 ("milvus" 或其他)
            collection_name: 集合名称
        """
        logger.info(f"初始化TextVectorStore，类型: {store_type}, 集合: {collection_name}")
        self.embeddings = get_embeddings()
        self.store_type = store_type
        self.collection_name = collection_name
        logger.debug("TextVectorStore初始化完成")

    def get_vector_store(self):
        """
        获取指定类型的向量数据库实例

        Returns:
            向量数据库实例
        """
        logger.debug(f"获取向量数据库实例，类型: {self.store_type}")
        if self.store_type.lower() == "milvus":
            logger.debug("使用Milvus向量数据库")
            return self._get_milvus_store()
        else:
            logger.debug("使用Chroma向量数据库")
            return self._get_chroma_store()

    def _get_chroma_store(self):
        """
        获取Chroma向量数据库实例

        Returns:
            Chroma向量数据库实例
        """
        logger.debug(f"创建Chroma存储，集合名: {self.collection_name}, 路径: {settings.chroma_file_path}")
        vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_file_path,
        )
        logger.info("Chroma向量数据库实例创建完成")
        return vector_store

    def _get_milvus_store(self):
        """
        获取Milvus向量数据库实例

        Milvus配置说明：
        - consistency_level="Strong" 确保数据一致性
        - index_params 定义索引类型和度量方式

        Returns:
            Milvus向量数据库实例
        """
        logger.debug(f"创建Milvus存储，集合名: {self.collection_name}, 连接: {settings.milvus_client}")
        logger.debug("Milvus配置: index_type=FLAT, metric_type=L2, consistency_level=Strong")
        vectorstore = Milvus(
            embedding_function=self.embeddings,
            collection_name=self.collection_name,
            connection_args={"uri": settings.milvus_client},
            index_params={"index_type": "FLAT", "metric_type": "L2"},
            consistency_level="Strong",
        )
        logger.info("Milvus向量数据库实例创建完成")
        return vectorstore

    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        向向量数据库添加文档

        Args:
            documents: 要添加的文档列表

        Returns:
            插入的文档ID列表
        """
        logger.info(f"向向量数据库添加文档，数量: {len(documents)}")
        document_ids = [str(uuid4()) for _ in documents]
        logger.debug(f"生成文档IDs: {document_ids}")

        vector_store = self.get_vector_store()
        logger.debug("调用向量数据库添加文档方法")
        inserted_ids = vector_store.add_documents(documents, ids=document_ids)
        logger.info(f"文档添加完成，实际插入数量: {len(inserted_ids)}")
        return inserted_ids

    def delete_documents(self, document_ids: List[str]) -> bool:
        """
        从向量数据库删除文档

        Args:
            document_ids: 要删除的文档ID列表

        Returns:
            删除操作是否成功
        """
        logger.info(f"从向量数据库删除文档，数量: {len(document_ids)}")
        logger.debug(f"待删除文档IDs: {document_ids}")

        vector_store = self.get_vector_store()
        logger.debug("调用向量数据库删除方法")
        result = vector_store.delete(ids=document_ids)
        logger.info(f"文档删除操作完成，结果: {result}")
        return result

    def delete_collection(self) -> None:
        """
        删除当前集合
        """
        logger.info(f"删除集合: {self.collection_name}")
        vector_store = self.get_vector_store()

        if self.store_type.lower() == "milvus":
            # Milvus 删除集合的方法
            logger.debug("调用Milvus删除集合方法")
            vector_store.client.drop_collection(self.collection_name)
            logger.info("Milvus集合删除成功")
        else:
            # Chroma 删除集合的方法
            logger.debug("调用Chroma删除集合方法")
            vector_store.delete_collection()
            logger.info("Chroma集合删除成功")
