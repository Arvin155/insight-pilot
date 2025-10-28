import os
from typing import List

from fastapi import APIRouter, Depends, status, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from loguru import logger
from sqlmodel import Session

from app.core.database import get_session
from app.crud.docs import DocsCRUD
from app.crud.knowledge import KnowledgeBaseDB
from app.services.rag.document_processing_service import DocumentProcessingService

router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("/document_list", status_code=status.HTTP_200_OK)
def document_list(
        knowledge_id: int,
        db: Session = Depends(get_session),
):
    """
    查询知识库下的文档列表

    Args:
        knowledge_id (int): 知识库ID
        db (Session): 数据库会话

    Returns:
        JSONResponse: 包含知识库名称和文档列表的响应
    """
    logger.info(f"开始查询知识库 {knowledge_id} 的文档列表")

    # 使用CRUD层处理数据库操作
    docs_crud = DocsCRUD(db)
    knowledge_base, documents = docs_crud.get_knowledge_base_with_documents(knowledge_id)

    # 检查知识库是否存在
    if not knowledge_base:
        logger.warning(f"知识库 {knowledge_id} 未找到")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库未发现"
        )

    # 格式化文档数据
    document_list = [
        {
            "id": doc.id,
            "name": doc.name,
            "file_path": doc.file_path,
            "file_type": doc.file_type,
            "file_size": doc.file_size,
            "chunk_count": doc.chunk_count,
            "created_at": doc.created_time.isoformat(),
            "updated_at": doc.updated_time.isoformat()
        }
        for doc in documents
    ]

    logger.info(f"成功获取知识库 {knowledge_id} 的文档列表，共 {len(document_list)} 个文档")
    return JSONResponse(
        content={
            "code": status.HTTP_200_OK,
            "msg": "文档列表获取成功",
            "data": {
                "knowledge_name": knowledge_base.name,
                "documents": document_list
            }
        },
        status_code=status.HTTP_200_OK
    )


@router.post("/upload_documents", status_code=status.HTTP_201_CREATED)
async def add_documents_to_knowledge_base(
        kb_id: int,
        files: List[UploadFile] = File(...),
        db: Session = Depends(get_session)
):
    """
    向知识库中添加文档

    Args:
        kb_id (int): 知识库ID
        files (List[UploadFile]): 上传的文件列表
        db (Session): 数据库会话

    Returns:
        JSONResponse: 表示上传结果的响应
    """
    logger.info(f"开始向知识库 {kb_id} 添加 {len(files)} 个文档")

    kb_db = KnowledgeBaseDB(db)
    knowledge_bases = kb_db.get_knowledge_base_by_id(kb_id)

    # 检查知识库是否存在
    if not knowledge_bases:
        logger.warning(f"尝试向不存在的知识库 {kb_id} 添加文档")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="知识库未找到"
        )

    document_processing_service = DocumentProcessingService(db_session=db)
    vector_store_type = knowledge_bases.vector_db_type.value if knowledge_bases.vector_db_type else "default_type"

    # 准备文档处理参数
    process_params = {
        "knowledge_id": knowledge_bases.id,
        "files": files,
        "kb_uuid": knowledge_bases.uuid,
        "chunk_size": knowledge_bases.chunk_size,
        "chunk_overlap": knowledge_bases.chunk_overlap,
        "vector_store_type": vector_store_type,
        "tags": knowledge_bases.tags
    }

    logger.info(f"开始处理文档，参数: knowledge_id={knowledge_bases.id}, "
                f"chunk_size={knowledge_bases.chunk_size}, chunk_overlap={knowledge_bases.chunk_overlap}")

    await document_processing_service.process_documents(processing_params=process_params)

    logger.info(f"成功向知识库 {kb_id} 添加文档")

    return JSONResponse(
        content={
            "code": status.HTTP_200_OK,
            "message": "知识库文档上传成功",
            "data": None
        },
        status_code=status.HTTP_200_OK
    )


@router.get("/chunks/{document_id}", status_code=status.HTTP_200_OK)
def get_document_chunks(
        document_id: int,
        db: Session = Depends(get_session),
):
    """
    获取指定文档的所有知识块列表

    Args:
        document_id (int): 文档ID
        db (Session): 数据库会话

    Returns:
        JSONResponse: 包含文档名称和知识块列表的响应
    """
    logger.info(f"开始获取文档 {document_id} 的知识块列表")

    # 使用CRUD层处理数据库操作
    docs_crud = DocsCRUD(db)
    document = docs_crud.get_document_by_id(document_id)

    # 检查文档是否存在
    if not document:
        logger.warning(f"尝试获取不存在的文档 {document_id} 的知识块")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档未找到"
        )

    # 获取文档的所有知识块
    chunks = docs_crud.get_chunks_by_document_id(document_id)

    # 格式化知识块数据
    chunk_list = [
        {
            "id": chunk.id,
            "chunk_id": chunk.chunk_id,
            "content": chunk.content,
            "page_label": chunk.page_label,
            "chunk_index": chunk.chunk_index,
            "document_metadata": chunk.document_metadata,
            "created_at": chunk.created_time.isoformat() if chunk.created_time else None,
            "updated_at": chunk.updated_time.isoformat() if chunk.updated_time else None
        }
        for chunk in chunks
    ]

    logger.info(f"成功获取文档 {document_id} 的知识块列表，共 {len(chunk_list)} 个知识块")

    return JSONResponse(
        content={
            "code": status.HTTP_200_OK,
            "msg": "知识块列表获取成功",
            "data": {
                "document_name": document.name,
                "chunks": chunk_list
            }
        },
        status_code=status.HTTP_200_OK
    )


@router.delete("/delete_document/{document_id}", status_code=status.HTTP_200_OK)
def delete_document(
        document_id: int,
        db: Session = Depends(get_session),
):
    """
    删除指定文档及其相关知识块

    Args:
        document_id (int): 文档ID
        db (Session): 数据库会话

    Returns:
        JSONResponse: 表示删除结果的响应
    """
    logger.info(f"开始删除文档 {document_id}")

    try:
        # 使用CRUD层处理数据库操作
        docs_crud = DocsCRUD(db)
        document = docs_crud.get_document_by_id(document_id)

        # 检查文档是否存在
        if not document:
            logger.warning(f"尝试删除不存在的文档 {document_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档未找到"
            )

        document_processing_service = DocumentProcessingService(db_session=db)
        logger.info(f"从向量存储中删除文档 {document_id}")
        document_processing_service.delete_document(document_id=document_id, knowledge_id=document.knowledge_base_id)

        # 先删除相关知识块，再删除文档
        logger.info(f"删除文档 {document_id} 相关的知识块")
        docs_crud.delete_chunks_by_document_id(document_id)
        logger.info(f"删除文档 {document_id}")
        docs_crud.delete_document(document_id)

        logger.info(f"成功删除文档 {document_id}")
        return JSONResponse(
            content={
                "code": status.HTTP_200_OK,
                "msg": "文档删除成功",
                "data": None
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        # 处理删除过程中的错误
        db.rollback()
        logger.error(f"文档 {document_id} 删除失败，已回滚事务 - 错误信息: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档删除失败: {str(e)}"
        )


@router.get("/download/{document_id}", status_code=status.HTTP_200_OK)
def download_document(
        document_id: int,
        db: Session = Depends(get_session),
):
    """
    下载指定ID的文档

    Args:
        document_id (int): 文档ID
        db (Session): 数据库会话

    Returns:
        FileResponse: 包含文件内容的响应
    """
    logger.info(f"开始下载文档 {document_id}")

    # 使用CRUD层处理数据库操作
    docs_crud = DocsCRUD(db)
    document = docs_crud.get_document_by_id(document_id)

    # 检查文档是否存在
    if not document:
        logger.warning(f"尝试下载不存在的文档 {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文档未找到"
        )

    # 检查文件是否存在
    if not document.file_path or not os.path.exists(document.file_path):
        logger.warning(f"文档 {document_id} 对应的物理文件不存在: {document.file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件未找到"
        )

    logger.info(f"成功准备文档 {document_id} 下载: {document.file_path}")
    # 返回文件响应
    return FileResponse(
        path=document.file_path,
        filename=document.name,
        media_type='application/octet-stream'
    )