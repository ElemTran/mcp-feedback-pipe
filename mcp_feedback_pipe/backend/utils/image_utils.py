"""
图片处理工具模块
提供图片信息获取、验证、格式检查等功能
"""

from pathlib import Path
from typing import Dict
import io

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from backend.security.csrf_handler import SecurityConfig


def get_image_info(image_path: str) -> str:
    """
    获取指定路径图片的信息（尺寸、格式等）

    Args:
        image_path: 图片文件路径

    Returns:
        包含图片信息的字符串
    """
    try:
        path = Path(image_path)
        if not path.exists():
            return f"文件不存在: {image_path}"

        if not PIL_AVAILABLE:
            return "错误：Pillow库未安装，无法获取图片信息"

        with Image.open(path) as img:
            info = {
                "文件名": path.name,
                "格式": img.format,
                "尺寸": f"{img.width} x {img.height}",
                "模式": img.mode,
                "文件大小": f"{path.stat().st_size / 1024:.1f} KB",
            }

        return "\n".join([f"{k}: {v}" for k, v in info.items()])

    except Exception as e:
        return f"获取图片信息失败: {str(e)}"


def validate_image_data(image_data: bytes) -> bool:
    """
    验证图片数据是否有效

    Args:
        image_data: 图片二进制数据

    Returns:
        是否为有效图片数据
    """
    if not image_data:
        return False

    # 如果PIL可用，进行更深入的验证
    if PIL_AVAILABLE:
        try:
            with Image.open(io.BytesIO(image_data)) as img:
                img.verify()
            return True
        except Exception:
            return False

    # 如果PIL不可用，使用文件头魔数验证
    return _check_image_signature(image_data)


def _check_image_signature(data: bytes) -> bool:
    """
    检查图片数据的文件头魔数

    Args:
        data: 图片二进制数据

    Returns:
        是否为支持的图片格式
    """
    # 检查文件头魔数
    image_signatures = {
        b"\x89PNG\r\n\x1a\n": "PNG",
        b"\xff\xd8\xff": "JPEG",
        b"GIF87a": "GIF87a",
        b"GIF89a": "GIF89a",
        b"BM": "BMP",
        b"RIFF": "WEBP",  # 需要进一步检查WEBP格式
    }

    for signature, format_name in image_signatures.items():
        if data.startswith(signature):
            if format_name == "WEBP":
                # WEBP需要额外验证
                return len(data) > 12 and data[8:12] == b"WEBP"
            return True

    return False


def is_allowed_file(filename: str) -> bool:
    """
    检查文件扩展名是否允许

    Args:
        filename: 文件名

    Returns:
        文件扩展名是否在允许列表中
    """
    if not filename:
        return False
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in SecurityConfig.ALLOWED_EXTENSIONS
    )


def get_image_format_info() -> Dict[str, str]:
    """
    获取支持的图片格式信息

    Returns:
        支持的图片格式字典
    """
    return {
        "PNG": "Portable Network Graphics",
        "JPEG": "Joint Photographic Experts Group",
        "GIF": "Graphics Interchange Format",
        "BMP": "Bitmap Image File",
        "WEBP": "WebP Image Format",
    }


def get_allowed_extensions() -> list:
    """
    获取允许的文件扩展名列表

    Returns:
        允许的文件扩展名列表
    """
    return list(SecurityConfig.ALLOWED_EXTENSIONS)
