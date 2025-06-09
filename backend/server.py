"""
MCP反馈通道服务器 v3.0
基于Web的现代化反馈收集系统，支持SSH环境
"""

import argparse
import base64
import codecs
import json
import sys
from typing import List

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.types import Image as MCPImage

# 使用绝对导入，以backend为顶级包
from backend.server_pool import get_managed_server, release_managed_server
from backend.utils.image_utils import get_image_info
from backend.version import __version__


# 编码配置：确保在Windows环境下正确处理Unicode字符
def _configure_encoding():
    """配置输入输出编码，避免Windows GBK编码问题"""
    if sys.platform.startswith("win"):
        # 设置stdout和stderr使用UTF-8编码
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            # 对于旧版本Python的兼容处理
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, errors="replace")


# 在模块加载时配置编码
_configure_encoding()

# NOTE: sys.path 修改已移除 - 各子包的 __init__.py 已完善，支持标准包导入
# 如果在特定环境下遇到导入问题，可能需要确保项目根目录在 PYTHONPATH 中

# 创建MCP服务器
mcp = FastMCP("MCP反馈通道 v3.0", dependencies=["flask", "pillow"])


@mcp.tool()
def collect_feedback(
    work_summary: str = "", timeout_seconds: int = 300, suggest: List[str] = None
) -> List:
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
    # 使用服务器池获取托管的服务器实例
    session_id = f"feedback_{id(work_summary)}_{timeout_seconds}"
    server_manager = get_managed_server(session_id)

    try:
        # 将建议列表转换为JSON字符串
        suggest_json = ""
        if suggest and isinstance(suggest, list):
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

        # 转换为MCP格式
        mcp_result = server_manager.feedback_handler.process_feedback_to_mcp(result)

        # 标记服务器可以被清理（但不立即清理）
        release_managed_server(session_id, immediate=False)

        return mcp_result

    except ImportError as e:
        release_managed_server(session_id, immediate=True)
        raise Exception(f"依赖缺失: {str(e)}")
    except Exception as e:
        release_managed_server(session_id, immediate=True)
        raise Exception(f"启动反馈通道失败: {str(e)}")


@mcp.tool()
def pick_image() -> MCPImage:
    """
    快速图片选择工具（Web版本）

    启动简化的Web界面，用户可以选择图片文件或从剪贴板粘贴图片。
    完美支持SSH远程环境。

    Returns:
        选择的图片数据
    """
    # 使用服务器池获取托管的服务器实例
    session_id = f"image_picker_{id('pick_image')}"
    server_manager = get_managed_server(session_id)

    try:
        # 启动图片选择界面
        port = server_manager.start_server("请选择一张图片", 300)

        print(f"📷 图片选择器已启动: http://127.0.0.1:{port}")
        print("💡 支持文件选择、拖拽上传、剪贴板粘贴")

        result = server_manager.wait_for_feedback(300)

        if not result or not result.get("success") or not result.get("has_images"):
            raise Exception("未选择图片或操作被取消")

        # 返回第一张图片
        first_image = result["images"][0]
        # 将Base64字符串解码为字节数据
        decoded_image_data = base64.b64decode(first_image["data"])
        mcp_image = MCPImage(data=decoded_image_data, format="png")

        # 标记服务器可以被清理（但不立即清理）
        release_managed_server(session_id, immediate=False)

        return mcp_image

    except Exception as e:
        release_managed_server(session_id, immediate=True)
        raise Exception(f"图片选择失败: {str(e)}")


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
    parser = argparse.ArgumentParser(
        description="MCP反馈通道 - 现代化Web反馈收集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  mcp-feedback-pipe                    # 启动MCP服务器
  mcp-feedback-pipe --version          # 显示版本信息
  mcp-feedback-pipe --help             # 显示帮助信息

更多信息请访问: https://github.com/ElemTran/mcp-feedback-pipe
        """,
    )

    parser.add_argument(
        "--version", "-v", action="version", version=f"mcp-feedback-pipe {__version__}"
    )

    # 解析参数（即使当前没有使用，保留以便将来扩展）
    parser.parse_args()

    # 启动MCP服务器
    mcp.run()


if __name__ == "__main__":
    main()
