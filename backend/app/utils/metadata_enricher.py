import json
import logging
from typing import List

from langchain_core.documents import Document as LangchainDocument
from llama_index.core import Document as LlamaDocument

from app.core.config import settings

# 默认排除的元数据字段列表
DEFAULT_EXCLUDE_FIELDS = [
    field.strip()
    for field in settings.metadata_exclude_fields.split(",")
    if field.strip()
]


def _enrich_document_metadata(
        document: LlamaDocument,
        kb_uuid: str,
        chunk_index: int,
        tags: List[str] = None
):
    """
    为单个文档增强元数据

    Args:
        document: 要增强的LlamaIndex文档
        kb_uuid: 知识库UUID
        chunk_index: 块索引
        tags: 标签列表
    """
    try:
        if document.metadata is None:
            document.metadata = {}

        # 提取原始元数据
        raw_file_name = document.metadata.get("file_name")
        raw_page_label = document.metadata.get("page_label")
        raw_creation_date = document.metadata.get("creation_date")

        # 新的元数据更新
        metadata_updates = {
            "doc_id": document.doc_id,
            "kb_uuid": kb_uuid,
            "source_file": raw_file_name or f"unknown_file_{document.doc_id[:8]}.pdf",
            "tags": json.dumps(tags or [], ensure_ascii=False),
            "page_label": raw_page_label,
            "creation_date": raw_creation_date,
            "chunk_index": chunk_index,
        }

        # 移除不需要的字段
        for field in DEFAULT_EXCLUDE_FIELDS:
            document.metadata.pop(field, None)

        document.metadata.update(metadata_updates)

    except Exception as error:
        logging.error(
            f"元数据增强失败: doc_id={document.doc_id}, kb_uuid={kb_uuid}, "
            f"chunk_index={chunk_index}, error={str(error)}"
        )
        raise


def _convert_llama_to_langchain_document(llama_document: LlamaDocument) -> LangchainDocument:
    """
    将LlamaIndex的Document转换为LangChain的Document

    Args:
        llama_document: LlamaIndex文档对象

    Returns:
        LangChain文档对象
    """
    return LangchainDocument(
        page_content=llama_document.text if hasattr(llama_document, 'text') else str(llama_document),
        metadata=llama_document.metadata or {}
    )


def process_pdf_documents(
        documents: List[LlamaDocument],
        kb_uuid: str,
        tags: List[str] = None,
) -> List[LangchainDocument]:
    """
    处理PDF文档列表，进行元数据增强并转换为LangChain格式

    Args:
        documents: LlamaIndex文档列表
        knowledge_base_uuid: 知识库UUID
        tags: 标签列表

    Returns:
        处理后的LangChain文档列表
    """
    try:
        processed_documents = []
        for chunk_index, document in enumerate(documents):
            # 增强元数据
            _enrich_document_metadata(
                document=document,
                kb_uuid=kb_uuid,
                tags=tags,
                chunk_index=chunk_index,
            )

            # 转换为LangChain文档类型
            langchain_document = _convert_llama_to_langchain_document(document)
            processed_documents.append(langchain_document)

        logging.info(f"元数据增强完成，共 {len(processed_documents)} 个文档。")
        return processed_documents

    except Exception as error:
        logging.error(f"处理文档列表失败: {str(error)}")
        raise