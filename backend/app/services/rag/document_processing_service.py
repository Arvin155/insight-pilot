import json
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any

from fastapi import UploadFile
from langchain_core.documents import Document as LangchainDocument
from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from loguru import logger

from app.core.config import settings
from app.crud.docs import DocsCRUD
from app.utils.file_utils import sanitize_filename, get_file_info
from app.utils.metadata_enricher import process_pdf_documents
from app.vector_store.text_vector_store import TextVectorStore


class DocumentProcessingService:
    """
    文档处理服务类，负责文档的上传、处理、存储和删除操作
    """

    def __init__(self, db_session):
        """
        初始化文档处理服务

        Args:
            db_session: 数据库会话对象
        """
        self.db_session = db_session
        self.settings = settings
        self.upload_directory = Path(self.settings.knowledge_file_path)
        self.upload_directory.mkdir(parents=True, exist_ok=True)
        self.docs_crud = DocsCRUD(db=db_session)
        self.file_chunk_size = 1024 * 1024  # 1MB
        logger.info(f"DocumentProcessingService initialized with upload directory: {self.upload_directory}")

    async def process_documents(self, processing_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理上传的文档，包括保存、分割、向量化和存储到数据库

        Args:
            processing_params: 处理参数字典，包含文件列表、知识库ID等信息

        Returns:
            处理结果字典

        Raises:
            Exception: 处理过程中发生的任何异常
        """
        try:
            logger.info(f"开始处理文档，知识库ID: {processing_params.get('knowledge_id')}")
            collection_name = f'kb_{processing_params.get("knowledge_id")}'

            logger.debug("开始保存上传的文件")
            saved_file_paths = await self._save_uploaded_files(
                files=processing_params.get("files"),
                kb_uuid=processing_params.get("kb_uuid")
            )
            logger.info(f"成功保存 {len(saved_file_paths)} 个文件")

            # 逐个处理每个文件
            for idx, file_path in enumerate(saved_file_paths):
                logger.info(f"开始处理第 {idx+1}/{len(saved_file_paths)} 个文件: {file_path}")
                await self._process_single_file(
                    file_path=file_path,
                    knowledge_id=processing_params.get("knowledge_id"),
                    kb_uuid=processing_params.get("kb_uuid"),
                    chunk_size=processing_params.get("chunk_size"),
                    chunk_overlap=processing_params.get("chunk_overlap"),
                    tags=processing_params.get("tags"),
                    collection_name=collection_name,
                    vector_store_type=processing_params.get("vector_store_type")
                )
                logger.info(f"完成处理文件: {file_path}")

            logger.debug("更新知识库统计信息")
            self._update_knowledge_base_statistics(knowledge_id=processing_params.get("knowledge_id"))

            result = {
                "status": "success",
                "message": f"成功处理 {len(processing_params.get('files'))} 个文件并存储到向量数据库",
            }
            logger.info(result["message"])
            return result

        except Exception as error:
            logger.error(f"处理文档时出错: {str(error)}")
            raise

    async def _process_single_file(
            self,
            file_path: str,
            knowledge_id: int,
            kb_uuid: str,
            chunk_size: int,
            chunk_overlap: int,
            tags: List[str],
            collection_name: str,
            vector_store_type: str
    ) -> None:
        """
        处理单个文件的完整流程

        Args:
            file_path: 文件路径
            knowledge_id: 知识库ID
            kb_uuid: 知识库UUID
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
            tags: 标签列表
            collection_name: 集合名称
            vector_store_type: 向量存储类型
        """
        logger.info(f"开始处理单个文件: {file_path}")

        # 创建文档记录
        logger.debug("创建文档记录")
        document_id = await self._create_document_record(
            knowledge_id=knowledge_id,
            file_path=file_path,
            collection_name=collection_name
        )
        logger.info(f"文档记录创建成功，文档ID: {document_id}")

        # 加载并分割文档
        logger.debug("加载并分割文档")
        processed_documents = await self._load_and_split_document(
            file_path=file_path,
            kb_uuid=kb_uuid,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            tags=tags
        )
        logger.info(f"文档分割完成，共生成 {len(processed_documents)} 个文档块")

        # 存储到向量数据库
        logger.debug("存储文档到向量数据库")
        inserted_document_ids = await self._store_documents_to_vector_db(
            collection_name=collection_name,
            store_type=vector_store_type,
            document_list=processed_documents
        )
        logger.info(f"文档存储完成，插入 {len(inserted_document_ids)} 个文档")

        # 创建知识块记录
        logger.debug("创建知识块记录")
        await self._create_chunk_records(
            document_id=document_id,
            documents=processed_documents,
            document_ids=inserted_document_ids
        )
        logger.info("知识块记录创建完成")

    async def _save_uploaded_files(self, files: List[UploadFile], kb_uuid: str) -> List[str]:
        """
        保存上传的文件到指定知识库目录

        Args:
            files: 上传的文件列表
            kb_uuid: 知识库UUID

        Returns:
            保存成功的文件路径列表

        Raises:
            Exception: 文件保存过程中发生的任何异常
        """
        logger.info(f"开始保存上传的文件到知识库 {kb_uuid}")
        knowledge_base_directory = self.upload_directory / str(kb_uuid)
        knowledge_base_directory.mkdir(exist_ok=True)
        logger.debug(f"知识库目录: {knowledge_base_directory}")

        saved_file_paths = []

        for idx, file in enumerate(files):
            try:
                logger.debug(f"处理第 {idx+1}/{len(files)} 个文件")

                # 验证文件名有效性
                if not file.filename:
                    logger.error("上传的文件没有文件名")
                    raise ValueError("上传的文件没有文件名")

                safe_filename = sanitize_filename(file.filename)
                base_name, file_extension = os.path.splitext(safe_filename)
                logger.debug(f"原始文件名: {file.filename}, 安全文件名: {safe_filename}")

                # 处理文件名冲突
                counter = 1
                original_filename = safe_filename
                while (knowledge_base_directory / safe_filename).exists():
                    safe_filename = f"{base_name} -{counter}{file_extension}"
                    counter += 1
                    logger.debug(f"文件名冲突，重命名为: {safe_filename}")

                file_path = knowledge_base_directory / safe_filename
                logger.info(f"文件将保存到: {file_path}")

                # 写入文件内容
                with open(file_path, "wb") as file_buffer:
                    bytes_written = 0
                    while content := await file.read(self.file_chunk_size):
                        file_buffer.write(content)
                        bytes_written += len(content)
                    logger.debug(f"文件写入完成，总大小: {bytes_written} 字节")

                saved_file_paths.append(str(file_path.resolve()))
                logger.info(f"文件保存成功: {file_path}")

            except Exception as error:
                logger.error(f"保存文件 {file.filename} 时出错: {str(error)}")
                # 清理失败的文件
                if 'file_path' in locals() and file_path.exists():
                    os.remove(file_path)
                    logger.info(f"已清理失败的文件: {file_path}")
                raise error

        logger.info(f"所有文件保存完成，共保存 {len(saved_file_paths)} 个文件")
        return saved_file_paths

    async def _load_and_split_document(
            self,
            file_path: str,
            kb_uuid: str,
            chunk_size: int,
            chunk_overlap: int,
            tags: List[str]
    ) -> List[LangchainDocument]:
        """
        使用LlamaIndex加载并分割文档

        Args:
            file_path: 文件路径
            kb_uuid: 知识库UUID
            chunk_size: 分块大小
            chunk_overlap: 分块重叠大小
            tags: 标签列表

        Returns:
            分割后的文档列表

        Raises:
            FileNotFoundError: 文件未找到
            Exception: 加载和分割过程中发生的任何异常
        """
        logger.info(f"开始加载并分割文档: {file_path}")
        try:
            logger.debug(f"创建SimpleDirectoryReader，文件路径: {file_path}")
            reader = SimpleDirectoryReader(
                input_files=[file_path],
                raise_on_error=True
            )

            # 加载原始文档
            logger.debug("开始加载原始文档")
            raw_documents = reader.load_data()
            logger.info(f"文档加载完成，共加载 {len(raw_documents)} 个文档")

            # 分割文档
            logger.debug("开始分割文档")
            split_documents = []
            splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            logger.debug(f"使用分割器，chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

            # 将单个文档分割成多个块
            logger.debug("从文档中获取节点")
            split_nodes = splitter.get_nodes_from_documents(raw_documents)
            logger.info(f"文档分割完成，共生成 {len(split_nodes)} 个节点")

            # 将分割后的节点转换回文档对象
            logger.debug("将节点转换为文档对象")
            for idx, node in enumerate(split_nodes):
                split_doc = Document(
                    text=node.text,
                    metadata=node.metadata
                )
                split_documents.append(split_doc)
            logger.info(f"节点转换完成，共转换 {len(split_documents)} 个文档")

            # 对分割后的文档进行元数据增强
            logger.debug("对文档进行元数据增强")
            enhanced_documents = process_pdf_documents(
                documents=split_documents,
                kb_uuid=kb_uuid,
                tags=tags
            )
            logger.info("文档元数据增强完成")

            return enhanced_documents

        except FileNotFoundError:
            logger.error(f"文件未找到: {file_path}")
            raise
        except Exception as error:
            logger.error(f"使用 LlamaIndex 加载并分割文档时出错: {str(error)}")
            raise Exception(f"加载并分割文档失败: {str(error)}") from error

    async def _create_document_record(
            self,
            knowledge_id: int,
            file_path: str,
            collection_name: str
    ) -> int:
        """
        在数据库中创建文档记录

        Args:
            knowledge_id: 知识库ID
            file_path: 文件路径
            collection_name: 集合名称

        Returns:
            创建的文档ID
        """
        logger.info(f"创建文档记录，文件路径: {file_path}")
        file_info = get_file_info(file_path)
        logger.debug(f"文件信息: {file_info}")

        document_data = {
            "name": file_info.get("file_name"),
            "file_path": file_path,
            "file_type": file_info.get("file_type"),
            "file_size": file_info.get("file_size"),
            "vector_path": collection_name,
            "chunk_count": 0,
            "knowledge_base_id": knowledge_id,
        }
        logger.debug(f"文档数据: {document_data}")

        document = self.docs_crud.create_document(data=document_data)
        logger.info(f"文档记录创建成功，文档ID: {document.id}")
        return document.id

    async def _create_chunk_records(
            self,
            document_id: int,
            documents: List[LangchainDocument],
            document_ids: List[str]
    ) -> None:
        """
        在数据库中创建知识块记录

        Args:
            document_id: 文档ID
            documents: 文档列表
            document_ids: 文档ID列表
        """
        logger.info(f"创建知识块记录，文档ID: {document_id}")
        for idx, (document, doc_id) in enumerate(zip(documents, document_ids)):
            logger.debug(f"创建第 {idx+1}/{len(documents)} 个知识块记录")
            chunk_data = {
                "chunk_id": doc_id,
                "content": document.page_content,
                "page_label": document.metadata.get("page_label"),
                "chunk_index": document.metadata.get("chunk_index"),
                "document_metadata": json.dumps(document.metadata, ensure_ascii=False),
                "document_id": document_id,
            }
            logger.debug(f"知识块数据: {chunk_data}")
            self.docs_crud.create_chunk(data=chunk_data)
        logger.info(f"知识块记录创建完成，共创建 {len(documents)} 个记录")

    @staticmethod
    async def _store_documents_to_vector_db(
            collection_name: str,
            store_type: str,
            document_list: List[Document]
    ) -> List[str]:
        """
        将文档存储到向量数据库

        Args:
            collection_name: 集合名称
            store_type: 存储类型
            document_list: 文档列表

        Returns:
            插入的文档ID列表
        """
        logger.info(f"将文档存储到向量数据库，集合名称: {collection_name}")
        logger.debug(f"存储类型: {store_type}, 文档数量: {len(document_list)}")

        text_vector_store = TextVectorStore(
            collection_name=collection_name,
            store_type=store_type
        )
        logger.debug("调用TextVectorStore.add_documents方法")
        inserted_ids = text_vector_store.add_documents(documents=document_list)
        logger.info(f"文档存储完成，插入 {len(inserted_ids)} 个文档")
        return inserted_ids

    def _update_knowledge_base_statistics(self, knowledge_id: int) -> None:
        """
        更新知识库的统计信息

        Args:
            knowledge_id: 知识库ID
        """
        logger.info(f"更新知识库统计信息，知识库ID: {knowledge_id}")
        self.docs_crud.update_document_chunk_counts(knowledge_id=knowledge_id)
        logger.debug("知识库统计信息更新完成")

    def delete_document(self, document_id: int, knowledge_id: int) -> Dict[str, Any]:
        """
        删除指定文档的所有相关信息

        Args:
            document_id: 文档ID
            knowledge_id: 知识库ID

        Returns:
            删除结果字典

        Raises:
            Exception: 删除过程中发生的任何异常
        """
        try:
            logger.info(f"开始删除文档，文档ID: {document_id}, 知识库ID: {knowledge_id}")

            # 从数据库获取文档信息
            logger.debug("获取文档信息")
            document = self.docs_crud.get_document_by_id(document_id)
            if not document:
                logger.error(f"未找到ID为 {document_id} 的文档")
                raise ValueError(f"未找到ID为 {document_id} 的文档")

            # 构建集合名称
            collection_name = f'kb_{knowledge_id}'
            logger.debug(f"集合名称: {collection_name}")

            # 从向量数据库中删除文档chunks
            logger.debug("获取文档的所有chunks")
            chunks = self.docs_crud.get_chunks_by_document_id(document_id)
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            logger.info(f"找到 {len(chunk_ids)} 个chunks需要删除")

            if chunk_ids:
                text_vector_store = TextVectorStore(
                    collection_name=collection_name,
                    store_type='milvus'
                )
                logger.info(f"准备删除 {len(chunk_ids)} 个 chunks")
                result = text_vector_store.delete_documents(document_ids=chunk_ids)
                logger.info(f"删除结果: {result}")

            # 删除本地文件
            logger.debug("删除本地文件")
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"本地文件删除成功: {file_path}")
            else:
                logger.warning(f"本地文件不存在: {file_path}")

            # 从SQL数据库中删除chunks和document记录
            logger.debug("从数据库中删除chunks和document记录")
            self.docs_crud.delete_chunks_by_document_id(document_id)
            self.docs_crud.delete_document(document_id)
            logger.info("数据库记录删除成功")

            # 更新知识库统计信息
            logger.debug("更新知识库统计信息")
            self.docs_crud.update_document_chunk_counts(knowledge_id=document.knowledge_base_id)
            logger.info("知识库统计信息更新完成")

            result = {
                "status": "success",
                "message": f"成功删除文档 {document.name}"
            }
            logger.info(result["message"])
            return result

        except Exception as error:
            logger.error(f"删除文档时出错: {str(error)}")
            raise

    async def delete_knowledge_base(self, kb_uuid: str, knowledge_id: int) -> Dict[str, Any]:
        """
        删除整个知识库及其所有相关数据

        Args:
            kb_uuid: 知识库UUID
            knowledge_id: 知识库ID

        Returns:
            删除结果字典

        Raises:
            Exception: 删除过程中发生的任何异常
        """
        try:
            logger.info(f"开始删除知识库，UUID: {kb_uuid}, ID: {knowledge_id}")

            # 获取知识库中的所有文档
            logger.debug("获取知识库中的所有文档")
            documents = self.docs_crud.get_documents_by_knowledge_id(knowledge_id)
            logger.info(f"找到 {len(documents)} 个文档需要删除")

            # 删除向量数据库中的整个集合
            logger.debug("删除向量数据库中的集合")
            collection_name = f'kb_{knowledge_id}'
            text_vector_store = TextVectorStore(
                collection_name=collection_name,
                store_type="milvus"
            )
            text_vector_store.delete_collection()
            logger.info("向量数据库集合删除成功")

            # 删除所有本地文件
            logger.debug("删除本地文件")
            kb_directory = self.upload_directory / str(kb_uuid)
            if kb_directory.exists():
                shutil.rmtree(kb_directory)
                logger.info(f"本地文件目录删除成功: {kb_directory}")
            else:
                logger.warning(f"本地文件目录不存在: {kb_directory}")

            # 从SQL数据库中删除所有相关记录
            logger.debug("从数据库中删除所有相关记录")
            for idx, document in enumerate(documents):
                logger.debug(f"删除第 {idx+1}/{len(documents)} 个文档记录")
                self.docs_crud.delete_chunks_by_document_id(document.id)
                self.docs_crud.delete_document(document.id)
            logger.info("数据库记录删除成功")

            result = {
                "status": "success",
                "message": f"成功删除知识库 {kb_uuid}"
            }
            logger.info(result["message"])
            return result

        except Exception as error:
            logger.error(f"删除知识库时出错: {str(error)}")
            raise
