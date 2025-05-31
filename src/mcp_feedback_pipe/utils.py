"""
工具模块
包含图片处理和其他通用功能
"""

from pathlib import Path
from typing import Dict, Optional
import io

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def get_image_info(image_path: str) -> str:
    """
    获取指定路径图片的信息（尺寸、格式等）
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        包含图片信息的字符串
    """
    if not PIL_AVAILABLE:
        return "错误：Pillow库未安装，无法获取图片信息"
    
    try:
        path = Path(image_path)
        if not path.exists():
            return f"文件不存在: {image_path}"
            
        with Image.open(path) as img:
            info = {
                "文件名": path.name,
                "格式": img.format,
                "尺寸": f"{img.width} x {img.height}",
                "模式": img.mode,
                "文件大小": f"{path.stat().st_size / 1024:.1f} KB"
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
    if not PIL_AVAILABLE:
        return False
        
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            img.verify()
        return True
    except Exception:
        return False


def format_feedback_summary(text_feedback: Optional[str], 
                          image_count: int, 
                          timestamp: str) -> str:
    """
    格式化反馈摘要
    
    Args:
        text_feedback: 文字反馈内容
        image_count: 图片数量
        timestamp: 时间戳
        
    Returns:
        格式化的反馈摘要
    """
    parts = []
    
    if text_feedback:
        parts.append(f"📝 文字反馈: {text_feedback[:100]}{'...' if len(text_feedback) > 100 else ''}")
    
    if image_count > 0:
        parts.append(f"🖼️ 图片数量: {image_count}张")
    
    parts.append(f"⏰ 提交时间: {timestamp}")
    
    return "\n".join(parts) 