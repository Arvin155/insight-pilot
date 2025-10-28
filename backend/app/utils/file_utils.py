from pathlib import Path
from loguru import logger


def sanitize_filename(filename: str) -> str:
    """
    安全清洗文件名，防止路径遍历和非法字符攻击

    Args:
        filename: 原始文件名

    Returns:
        清洗后的安全文件名

    Raises:
        ValueError: 当文件名为空时
    """
    logger.debug(f"开始清洗文件名: {filename}")

    # 验证文件名有效性
    if not filename or filename.strip() == "":
        logger.error("文件名为空或仅包含空白字符")
        raise ValueError("文件名不能为空")

    # 移除路径分隔符（防止路径遍历攻击）
    safe_name = filename.replace('/', '_').replace('\\', '_')

    # 替换危险字符
    dangerous_chars = ['"', "'", '<', '>', '|', ':', '*', '?']
    for char in dangerous_chars:
        safe_name = safe_name.replace(char, '_')

    # 移除控制字符（仅保留 ASCII 32 及以上字符）
    safe_name = ''.join(char if ord(char) >= 32 else '_' for char in safe_name)

    # 处理空白字符
    safe_name = safe_name.strip(' ')

    # 移除结尾的点
    if safe_name.endswith('.'):
        safe_name = safe_name.rstrip('.')
        logger.debug(f"移除结尾点号后: {safe_name}")

    # 空文件名处理
    if not safe_name:
        safe_name = "uploaded_file"
        logger.warning("文件名处理后为空，使用默认文件名: uploaded_file")

    logger.info(f"文件名清洗完成: {safe_name}")
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """
    将字节大小格式化为人类可读的格式 (B, KB, MB, GB, TB)

    Args:
        size_bytes: 文件大小（字节）

    Returns:
        格式化后的文件大小字符串
    """
    logger.debug(f"格式化文件大小: {size_bytes} 字节")

    if size_bytes == 0:
        logger.debug("文件大小为0")
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    size = size_bytes

    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1

    formatted_size = int(size) if size.is_integer() else round(size, 1)
    result = f"{formatted_size} {units[index]}"
    logger.debug(f"文件大小格式化结果: {result}")
    return result


def get_file_info(file_path: str) -> dict:
    """
    获取文件类型和文件大小信息

    Args:
        file_path: 文件的绝对路径

    Returns:
        包含文件类型、文件大小和文件名的字典
    """
    logger.debug(f"获取文件信息: {file_path}")

    try:
        path = Path(file_path)

        # 获取文件名
        file_name = path.name
        logger.debug(f"文件名: {file_name}")

        # 获取文件扩展名作为文件类型
        file_type = str(path.suffix.lower()).strip(".")
        logger.debug(f"文件类型: {file_type}")

        # 获取文件大小
        file_size_bytes = path.stat().st_size
        file_size = format_file_size(file_size_bytes)
        logger.debug(f"文件大小: {file_size} ({file_size_bytes} 字节)")

        result = {
            "file_type": file_type,
            "file_size": file_size,
            "file_name": file_name
        }
        logger.info(f"文件信息获取完成: {result}")
        return result

    except Exception as e:
        logger.error(f"获取文件信息时出错: {file_path}, 错误: {str(e)}")
        raise
