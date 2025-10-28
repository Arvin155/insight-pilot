import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
from sqlmodel import Session

from app.core.database import get_session
from app.crud.docs import DocsCRUD
from app.crud.knowledge import KnowledgeBaseDB
from app.models.knowledge import KnowledgeBaseStatus
from app.schemas.knowledge import KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeStatusUpdate

# 创建路由实例，设置前缀和标签
router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/create_knowledge", status_code=status.HTTP_201_CREATED)
def create_knowledge_base(req: KnowledgeBaseCreate, db: Session = Depends(get_session)):
    """
    创建新的知识库

    Args:
        req (KnowledgeBaseCreate): 包含创建知识库所需信息的请求体
        db (Session): 数据库会话

    Returns:
        JSONResponse: 返回创建结果和知识库ID

    Raises:
        HTTPException: 当知识库已存在或创建过程中出现错误时抛出异常
    """
    logger.info(f"开始创建知识库: {req.name}")
    logger.debug(f"请求参数: name={req.name}, user_id={req.user_id}")

    try:
        # 初始化数据库操作对象
        kb_db = KnowledgeBaseDB(db)

        # 检查是否已存在同名知识库
        logger.debug(f"检查知识库是否存在: {req.name}")
        existing_kb = kb_db.get_knowledge_base_by_name(req.name)
        if existing_kb:
            warning_msg = f"知识库 {req.name} 已存在"
            logger.warning(warning_msg)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=warning_msg
            )

        # 创建新知识库
        logger.info(f"正在创建新知识库: {req.name}")
        db_knowledge_base = kb_db.create_knowledge_base(
            name=req.name,
            uuid=str(uuid.uuid4()),
            description=req.description,
            vector_db_type=req.vector_db_type,
            user_id=req.user_id,
            chunk_size=req.chunk_size,
            tags=req.tags,
            chunk_overlap=req.chunk_overlap,
            is_public=req.is_public
        )

        logger.success(f"知识库创建成功: {req.name}, ID: {db_knowledge_base.id}")

        return JSONResponse(
            content={
                "code": status.HTTP_200_OK,
                "msg": "知识库创建成功",
                "data": db_knowledge_base.id
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        error_msg = f"创建知识库失败: {str(e)}"
        logger.error("{}", error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.get("/list_knowledge", status_code=status.HTTP_200_OK)
def list_knowledge_bases(user_id: int, db: Session = Depends(get_session)):
    """
    获取指定用户的全部知识库列表，包括每个知识库的文档数量和分块总数

    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话

    Returns:
        JSONResponse: 返回知识库列表数据，包含文档数量和分块总数

    Raises:
        HTTPException: 当查询过程中出现错误时抛出异常
    """
    logger.info(f"获取用户知识库列表: user_id={user_id}")

    try:
        # 初始化数据库操作对象
        kb_db = KnowledgeBaseDB(db)
        docs_crud = DocsCRUD(db)

        # 查询用户的所有知识库
        logger.debug(f"查询用户 {user_id} 的知识库")
        knowledge_bases = kb_db.list_knowledge_bases_by_user(user_id)
        logger.debug(f"查询到 {len(knowledge_bases)} 个知识库")

        # 构造返回数据
        result_data = []
        for kb in knowledge_bases:
            # 获取该知识库下的文档数量和分块总数
            doc_stats = docs_crud.get_knowledge_base_document_stats(kb.id)

            result_data.append({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "tags": kb.tags,
                "chunk_size": kb.chunk_size,
                "chunk_overlap": kb.chunk_overlap,
                "vector_db_type": kb.vector_db_type.value,
                "status": kb.status.value,
                "query_count":kb.query_count,
                "document_count": doc_stats["document_count"],
                "chunk_total": doc_stats["chunk_total"],
                "created_at": kb.created_time.isoformat() if kb.created_time else None,
                "updated_at": kb.updated_time.isoformat() if kb.updated_time else None
            })

        logger.success(f"成功获取用户 {user_id} 的知识库列表，共 {len(result_data)} 条记录")

        return JSONResponse(
            content={
                "code": status.HTTP_200_OK,
                "msg": "查询成功",
                "data": result_data
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        error_msg = f"查询知识库列表失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )



@router.put("/update_knowledge", status_code=status.HTTP_200_OK)
def update_knowledge_base(
        req: KnowledgeBaseUpdate,
        db: Session = Depends(get_session)
):
    """
    更新知识库信息

    Args:
        req (KnowledgeBaseUpdate): 包含更新信息的请求体
        db (Session): 数据库会话

    Returns:
        JSONResponse: 返回更新结果

    Raises:
        HTTPException: 当知识库不存在或更新过程中出现错误时抛出异常
    """
    logger.info(f"开始更新知识库: id={req.id}, name={req.name}")
    logger.debug(f"更新参数: {req.dict()}")

    try:
        # 初始化数据库操作对象
        kb_db = KnowledgeBaseDB(db)

        # 检查要更新的知识库是否存在
        logger.debug(f"检查知识库是否存在: id={req.id}")
        existing_kb = kb_db.get_knowledge_base_by_id(req.id)

        if not existing_kb:
            error_msg = f"知识库 ID {req.id} 不存在"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )

        # 检查是否有同名的知识库（排除自己）
        logger.debug(f"检查是否存在同名知识库: {req.name}")
        duplicate_kb = kb_db.get_knowledge_base_by_name(req.name)
        if duplicate_kb and duplicate_kb.id != req.id:
            warning_msg = f"知识库名称 {req.name} 已存在"
            logger.warning(warning_msg)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=warning_msg
            )

        # 执行更新操作
        logger.info(f"正在更新知识库: id={req.id}")
        kb_db.update_knowledge_base(
            knowledge_id=req.id,
            name=req.name,
            description=req.description,
            vector_db_type=req.vector_db_type,
            chunk_size=req.chunk_size,
            tags=req.tags,
            chunk_overlap=req.chunk_overlap,
            is_public=req.is_public
        )

        logger.success(f"知识库更新成功: id={req.id}")

        return JSONResponse(
            content={
                "code": status.HTTP_200_OK,
                "msg": "知识库更新成功",
                "data": None
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        error_msg = f"更新知识库失败: {str(e)}"
        logger.error("{}", error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )


@router.put("/update_status", status_code=status.HTTP_200_OK)
def update_knowledge_base_status(
        req: KnowledgeStatusUpdate,
        db: Session = Depends(get_session)
):
    """
    更新知识库状态

    Args:
        req (KnowledgeStatusUpdate): 包含状态更新信息的请求体
        db (Session): 数据库会话

    Returns:
        JSONResponse: 返回状态更新结果

    Raises:
        HTTPException: 当知识库不存在或更新过程中出现错误时抛出异常
    """
    logger.info(f"更新知识库状态: id={req.id}, status={req.status}")

    try:
        # 初始化数据库操作对象
        kb_db = KnowledgeBaseDB(db)

        # 检查知识库是否存在
        logger.debug(f"检查知识库是否存在: id={req.id}")
        existing_kb = kb_db.get_knowledge_base_by_id(req.id)

        if not existing_kb:
            error_msg = f"知识库 ID {req.id} 不存在"
            logger.error(error_msg)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )

        # 更新知识库状态
        logger.info(f"正在更新知识库状态: id={req.id}, status={req.status}")
        kb_db.update_knowledge_base_status(
            knowledge_id=req.id,
            status=KnowledgeBaseStatus(req.status).value
        )

        logger.success(f"知识库状态更新成功: id={req.id}")

        return JSONResponse(
            content={
                "code": status.HTTP_200_OK,
                "msg": "知识库状态更新成功",
                "data": None
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        db.rollback()
        error_msg = f"更新知识库状态失败: {str(e)}"
        logger.error("{}", error_msg, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
