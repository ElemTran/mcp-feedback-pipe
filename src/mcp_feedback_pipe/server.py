"""
MCP反馈通道服务器 v3.0
基于Web的现代化反馈收集系统，支持SSH环境
"""

import sys
import os
from typing import List

# 添加src目录到路径以支持直接执行
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image as MCPImage

# 导入修复：支持相对导入和绝对导入
try:
    from .server_manager import ServerManager
    from .utils import get_image_info
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from mcp_feedback_pipe.server_manager import ServerManager
    from mcp_feedback_pipe.utils import get_image_info


# 创建MCP服务器
mcp = FastMCP(
    "MCP反馈通道 v3.0",
    dependencies=["flask", "pillow"]
)

# 全局服务器管理器
server_manager = ServerManager()


@mcp.tool()
def collect_feedback(work_summary: str = "", timeout_seconds: int = 300, suggest: List[str] = None) -> List:
    """
    收集用户反馈的交互式工具（Web版本）
    
    启动Web界面，AI可以汇报完成的工作，用户可以提供文字和/或图片反馈。
    完美支持SSH远程环境。
    
    Args:
        work_summary: AI完成的工作内容汇报
        timeout_seconds: 对话框超时时间（秒），默认300秒（5分钟）
        suggest: 建议选项列表，格式如：["选项1", "选项2", "选项3"]
        
    Returns:
        包含用户反馈内容的列表，可能包含文本和图片
    """
    try:
        # 将建议列表转换为JSON字符串
        suggest_json = ""
        if suggest and isinstance(suggest, list):
            import json
            suggest_json = json.dumps(suggest, ensure_ascii=False)
        
        # 启动Web服务器
        port = server_manager.start_server(work_summary, timeout_seconds, suggest_json)
        
        print(f"📱 反馈通道已启动: http://127.0.0.1:{port}")
        print(f"⏰ 等待用户反馈... (超时: {timeout_seconds}秒)")
        print("💡 SSH环境请配置端口转发后访问")
        
        # 等待用户反馈
        result = server_manager.wait_for_feedback(timeout_seconds)
        
        if result is None:
            raise Exception(f"操作超时（{timeout_seconds}秒），请重试")
        
        # 转换为MCP格式并返回
        return server_manager.feedback_handler.process_feedback_to_mcp(result)
        
    except ImportError as e:
        raise Exception(f"依赖缺失: {str(e)}")
    except Exception as e:
        raise Exception(f"启动反馈通道失败: {str(e)}")
    finally:
        # 清理资源
        server_manager.stop_server()


@mcp.tool()
def pick_image() -> MCPImage:
    """
    快速图片选择工具（Web版本）
    
    启动简化的Web界面，用户可以选择图片文件或从剪贴板粘贴图片。
    完美支持SSH远程环境。
    
    Returns:
        选择的图片数据
    """
    try:
        # 启动图片选择界面
        port = server_manager.start_server("请选择一张图片", 300)
        
        print(f"📷 图片选择器已启动: http://127.0.0.1:{port}")
        print("💡 支持文件选择、拖拽上传、剪贴板粘贴")
        
        result = server_manager.wait_for_feedback(300)
        
        if not result or not result.get('success') or not result.get('has_images'):
            raise Exception("未选择图片或操作被取消")
            
        # 返回第一张图片
        first_image = result['images'][0]
        return MCPImage(data=first_image['data'], format='png')
        
    except Exception as e:
        raise Exception(f"图片选择失败: {str(e)}")
    finally:
        # 清理资源
        server_manager.stop_server()


@mcp.tool()
def get_image_info_tool(image_path: str) -> str:
    """
    获取指定路径图片的详细信息
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        包含图片信息的字符串（格式、尺寸、大小等）
    """
    return get_image_info(image_path)


def main():
    """主入口点"""
    mcp.run()


if __name__ == "__main__":
    main() 