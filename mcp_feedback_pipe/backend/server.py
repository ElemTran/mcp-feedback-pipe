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
from backend.utils.custom_exceptions import FeedbackTimeoutError, ImageSelectionError
from backend.version import __version__
from backend.config import get_server_config


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


# =============================================================================
# MCP资源定义 - Resources
# 将服务器状态信息作为标准MCP资源暴露
# =============================================================================

@mcp.resource("mcp://feedback-server/status")
def get_server_status_resource() -> str:
    """
    MCP标准资源：服务器池状态信息
    
    提供持久化的服务器池状态，支持：
    - 跨会话访问
    - 多客户端共享 
    - 离线查询
    - 状态验证
    
    Returns:
        JSON格式的服务器状态信息
    """
    try:
        from backend.server_pool import get_server_pool, load_server_status_from_file
        from backend.port_info import get_detailed_port_info
        import json
        import time
        
        # 1. 从持久化文件获取状态
        saved_status = load_server_status_from_file()
        
        # 2. 获取实时端口信息
        detailed_info = get_detailed_port_info()
        
        # 3. 尝试获取当前服务器池状态（如果可用）
        try:
            server_pool = get_server_pool()
            current_status = server_pool.get_pool_status()
        except:
            current_status = None
        
        # 4. 构建标准MCP资源格式
        resource_data = {
            "mcp_resource": {
                "uri": "mcp://feedback-server/status",
                "name": "服务器池状态",
                "description": "MCP反馈服务器池的完整状态信息",
                "mimeType": "application/json",
                "generated_at": time.time(),
                "generated_at_readable": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "persistence": {
                "enabled": saved_status is not None,
                "last_saved": saved_status.get('last_updated_readable') if saved_status else None,
                "file_path": ".mcp_server_pool_status.json",
                "auto_save": True
            },
            "data_sources": {
                "persistent": {
                    "available": saved_status is not None,
                    "servers_count": len(saved_status.get('servers', [])) if saved_status else 0,
                    "ports": saved_status.get('ports_in_use', []) if saved_status else []
                },
                "runtime": {
                    "available": current_status is not None,
                    "servers_count": current_status.get('total_servers', 0) if current_status else 0,
                    "active_count": current_status.get('active_servers', 0) if current_status else 0,
                    "ports": detailed_info.get('running_ports', [])
                }
            },
            "servers": [],
            "ssh_commands": [],
            "access_urls": []
        }
        
        # 5. 合并服务器信息
        all_servers = []
        verified_ports = detailed_info.get('running_ports', [])
        
        # 从持久化数据获取服务器
        if saved_status and saved_status.get('servers'):
            for server in saved_status['servers']:
                server_info = {
                    "session_id": server.get('session_id'),
                    "port": server.get('port'),
                    "work_summary": server.get('work_summary'),
                    "timeout_seconds": server.get('timeout_seconds'),
                    "status": server.get('status'),
                    "data_source": "persistent",
                    "verified_running": server.get('port') in verified_ports if server.get('port') else False,
                    "url": f"http://127.0.0.1:{server.get('port')}" if server.get('port') else None,
                    "created_at": server.get('created_at'),
                    "uptime": server.get('uptime'),
                    "idle_time": server.get('idle_time')
                }
                
                # 如果服务器仍在运行，添加到访问URL列表
                if server_info['verified_running']:
                    resource_data['access_urls'].append(server_info['url'])
                
                all_servers.append(server_info)
        
        # 从运行时数据补充服务器
        if current_status and current_status.get('servers'):
            for server in current_status['servers']:
                # 检查是否已经在持久化数据中
                existing = next((s for s in all_servers if s['session_id'] == server.get('session_id')), None)
                
                if existing:
                    # 更新运行时数据
                    existing.update({
                        "data_source": "persistent+runtime",
                        "verified_running": True,
                        "uptime": server.get('uptime'),
                        "idle_time": server.get('idle_time')
                    })
                else:
                    # 新的运行时服务器
                    server_info = {
                        "session_id": server.get('session_id'),
                        "port": server.get('port'),
                        "work_summary": server.get('work_summary'),
                        "timeout_seconds": server.get('timeout_seconds'),
                        "status": server.get('status'),
                        "data_source": "runtime",
                        "verified_running": True,
                        "url": server.get('url'),
                        "uptime": server.get('uptime'),
                        "idle_time": server.get('idle_time')
                    }
                    
                    if server_info['url']:
                        resource_data['access_urls'].append(server_info['url'])
                    
                    all_servers.append(server_info)
        
        resource_data['servers'] = all_servers
        
        # 6. 生成SSH转发命令
        running_ports = [s['port'] for s in all_servers if s['verified_running'] and s['port']]
        base_port = 8888
        
        for i, port in enumerate(sorted(running_ports)):
            local_port = base_port + i
            resource_data['ssh_commands'].append({
                "remote_port": port,
                "local_port": local_port,
                "command": f"ssh -L {local_port}:127.0.0.1:{port} your_user@your_server",
                "access_url": f"http://127.0.0.1:{local_port}/"
            })
        
        # 7. 添加资源元数据
        resource_data['statistics'] = {
            "total_known_servers": len(all_servers),
            "running_servers": len([s for s in all_servers if s['verified_running']]),
            "persistent_servers": len([s for s in all_servers if 'persistent' in s['data_source']]),
            "runtime_only_servers": len([s for s in all_servers if s['data_source'] == 'runtime']),
            "accessible_urls_count": len(resource_data['access_urls']),
            "ssh_commands_count": len(resource_data['ssh_commands'])
        }
        
        return json.dumps(resource_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        import traceback
        error_data = {
            "mcp_resource": {
                "uri": "mcp://feedback-server/status",
                "name": "服务器池状态",
                "error": True,
                "generated_at": time.time()
            },
            "error": {
                "message": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        }
        return json.dumps(error_data, ensure_ascii=False, indent=2)


@mcp.resource("mcp://feedback-server/ports")
def get_ports_resource() -> str:
    """
    MCP标准资源：活跃端口信息
    
    轻量级资源，仅提供当前运行的端口信息
    
    Returns:
        JSON格式的端口信息
    """
    try:
        from backend.port_info import get_mcp_server_ports
        import time
        import json
        
        running_ports = get_mcp_server_ports()
        
        resource_data = {
            "mcp_resource": {
                "uri": "mcp://feedback-server/ports",
                "name": "活跃端口列表", 
                "description": "当前运行的MCP反馈服务器端口",
                "mimeType": "application/json",
                "generated_at": time.time(),
                "generated_at_readable": time.strftime('%Y-%m-%d %H:%M:%S')
            },
            "ports": running_ports,
            "count": len(running_ports),
            "urls": [f"http://127.0.0.1:{port}" for port in running_ports],
            "ssh_commands": []
        }
        
        # 生成SSH转发命令
        base_port = 8888
        for i, port in enumerate(sorted(running_ports)):
            local_port = base_port + i
            resource_data['ssh_commands'].append({
                "remote_port": port,
                "local_port": local_port,
                "command": f"ssh -L {local_port}:127.0.0.1:{port} your_user@your_server"
            })
        
        return json.dumps(resource_data, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_data = {
            "mcp_resource": {
                "uri": "mcp://feedback-server/ports",
                "error": True,
                "generated_at": time.time()
            },
            "error": {
                "message": str(e),
                "type": type(e).__name__
            }
        }
        return json.dumps(error_data, ensure_ascii=False, indent=2)


@mcp.resource("mcp://feedback-server/config/{config_type}")
def get_config_resource(config_type: str) -> str:
    """
    MCP动态资源模板：配置信息
    
    根据config_type参数提供不同类型的配置信息：
    - server: 服务器配置
    - ssh: SSH转发配置
    - backup: 备份配置
    
    Args:
        config_type: 配置类型 (server|ssh|backup)
        
    Returns:
        JSON格式的配置信息
    """
    try:
        import time
        import json
        from backend.config import get_server_config
        from backend.server_pool import load_server_status_from_file
        
        base_resource = {
            "mcp_resource": {
                "uri": f"mcp://feedback-server/config/{config_type}",
                "name": f"{config_type.upper()}配置",
                "mimeType": "application/json",
                "generated_at": time.time(),
                "generated_at_readable": time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        if config_type == "server":
            # 服务器配置
            server_config = get_server_config()
            base_resource.update({
                "config": {
                    "preferred_port": getattr(server_config, 'preferred_port', 8765),
                    "port_range": getattr(server_config, 'port_range', (8765, 8865)),
                    "default_timeout": getattr(server_config, 'default_timeout', 300),
                    "idle_timeout": getattr(server_config, 'idle_timeout', 1800),
                    "cleanup_interval": getattr(server_config, 'cleanup_interval', 60),
                    "browser_grace_period": getattr(server_config, 'browser_grace_period', 15),
                    "recommended_local_forward_port": getattr(server_config, 'recommended_local_forward_port', 8888)
                },
                "description": "MCP反馈服务器的核心配置参数"
            })
            
        elif config_type == "ssh":
            # SSH转发配置
            saved_status = load_server_status_from_file()
            ssh_configs = []
            
            if saved_status and saved_status.get('servers'):
                base_port = 8888
                for i, server in enumerate(saved_status['servers']):
                    if server.get('port'):
                        local_port = base_port + i
                        ssh_configs.append({
                            "session_id": server.get('session_id'),
                            "remote_port": server.get('port'),
                            "local_port": local_port,
                            "command": f"ssh -L {local_port}:127.0.0.1:{server.get('port')} your_user@your_server",
                            "access_url": f"http://127.0.0.1:{local_port}/",
                            "work_summary": server.get('work_summary', '')
                        })
            
            base_resource.update({
                "ssh_forwards": ssh_configs,
                "count": len(ssh_configs),
                "description": "SSH端口转发配置，用于从本地访问远程服务器"
            })
            
        elif config_type == "backup":
            # 备份配置
            import os
            import glob
            
            # 查找备份文件
            backup_files = glob.glob("mcp_status_backup_*.json")
            export_files = glob.glob("mcp_config_export_*.json")
            
            backup_info = []
            for backup_file in backup_files:
                stat = os.stat(backup_file)
                backup_info.append({
                    "filename": backup_file,
                    "size": stat.st_size,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)),
                    "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                    "type": "backup"
                })
            
            for export_file in export_files:
                stat = os.stat(export_file)
                backup_info.append({
                    "filename": export_file,
                    "size": stat.st_size,
                    "created": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)),
                    "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                    "type": "export"
                })
            
            base_resource.update({
                "backup_files": backup_info,
                "status_file": {
                    "path": ".mcp_server_pool_status.json",
                    "exists": os.path.exists(".mcp_server_pool_status.json")
                },
                "description": "备份和导出文件的管理信息"
            })
            
        else:
            base_resource.update({
                "error": f"未知的配置类型: {config_type}",
                "supported_types": ["server", "ssh", "backup"]
            })
        
        return json.dumps(base_resource, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_data = {
            "mcp_resource": {
                "uri": f"mcp://feedback-server/config/{config_type}",
                "error": True,
                "generated_at": time.time()
            },
            "error": {
                "message": str(e),
                "type": type(e).__name__
            }
        }
        return json.dumps(error_data, ensure_ascii=False, indent=2)


# =============================================================================
# MCP工具定义 - Tools
# =============================================================================

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

        server_config = get_server_config()
        # 8888 是 recommended_local_forward_port 的临时默认值，最终将由 config.py 定义
        recommended_local_port = getattr(server_config, 'recommended_local_forward_port', 8888)

        print(f"✅ 服务已在远程服务器的 127.0.0.1:{port} 启动。")
        print(f"💡 要从您的本地机器访问，请设置SSH端口转发。")
        print(f"   如果您尚未配置，可以在您的本地终端运行类似以下命令：")
        print(f"   ssh -L {recommended_local_port}:127.0.0.1:{port} your_user@your_remote_server_ip")
        print(f"   (请将 'your_user@your_remote_server_ip' 替换为您的实际SSH登录信息)")
        print(f"➡️ 设置转发后，请在您本地的浏览器中打开: http://127.0.0.1:{recommended_local_port}/")
        print(f"⏰ 等待用户反馈... (远程服务超时: {timeout_seconds}秒)")

        # 等待用户反馈
        result = server_manager.wait_for_feedback(timeout_seconds)

        if result is None:
            raise FeedbackTimeoutError(timeout_seconds)

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
        server_config = get_server_config()
        image_timeout = server_config.image_picker_timeout
        
        # 启动图片选择界面
        port = server_manager.start_server("请选择一张图片", image_timeout)

        # 8888 是 recommended_local_forward_port 的临时默认值，最终将由 config.py 定义
        recommended_local_port = getattr(server_config, 'recommended_local_forward_port', 8888)

        print(f"📷 图片选择器已在远程服务器的 127.0.0.1:{port} 启动。")
        print(f"💡 要从您的本地机器访问，请设置SSH端口转发。")
        print(f"   如果您尚未配置，可以在您的本地终端运行类似以下命令：")
        print(f"   ssh -L {recommended_local_port}:127.0.0.1:{port} your_user@your_remote_server_ip")
        print(f"   (请将 'your_user@your_remote_server_ip' 替换为您的实际SSH登录信息)")
        print(f"➡️ 设置转发后，请在您本地的浏览器中打开: http://127.0.0.1:{recommended_local_port}/")
        print(f"💡 支持文件选择、拖拽上传、剪贴板粘贴")
        print(f"⏰ 等待用户选择... (远程服务超时: {image_timeout}秒)")

        result = server_manager.wait_for_feedback(image_timeout)

        if not result or not result.get("success") or not result.get("has_images"):
            raise ImageSelectionError()

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


@mcp.tool()
def create_server_pool(server_configs: List[dict]) -> str:
    """
    创建多个并发的反馈服务器池
    
    Args:
        server_configs: 服务器配置列表，每个配置包含：
            - session_id: 会话ID (必需)
            - work_summary: 工作汇报 (可选)
            - timeout_seconds: 超时时间 (可选，默认300)
            - suggest: 建议选项 (可选)
    
    Returns:
        创建结果的详细信息
    """
    try:
        from backend.server_pool import get_server_pool
        server_pool = get_server_pool()
        
        results = []
        failed_servers = []
        
        for config in server_configs:
            if not isinstance(config, dict) or 'session_id' not in config:
                failed_servers.append({
                    'config': config,
                    'error': '配置格式错误，必须包含session_id字段'
                })
                continue
            
            session_id = config['session_id']
            work_summary = config.get('work_summary', f'反馈收集任务 - {session_id}')
            timeout_seconds = config.get('timeout_seconds', 300)
            suggest = config.get('suggest', '')
            
            try:
                # 在服务器池中启动服务器
                server_manager, port = server_pool.start_server_in_pool(
                    session_id=session_id,
                    work_summary=work_summary,
                    timeout_seconds=timeout_seconds,
                    suggest=suggest
                )
                
                results.append({
                    'session_id': session_id,
                    'port': port,
                    'url': f'http://127.0.0.1:{port}',
                    'status': 'success',
                    'work_summary': work_summary,
                    'timeout_seconds': timeout_seconds
                })
                
            except Exception as e:
                failed_servers.append({
                    'session_id': session_id,
                    'error': str(e)
                })
        
        # 生成结果报告
        report_lines = []
        
        if results:
            report_lines.extend([
                f"✅ 成功创建 {len(results)} 个服务器:",
                ""
            ])
            
            server_config = get_server_config()
            base_local_port = getattr(server_config, 'recommended_local_forward_port', 8888)
            
            for i, result in enumerate(results):
                local_port = base_local_port + i
                report_lines.extend([
                    f"  🟢 {result['session_id']}",
                    f"    端口: {result['port']}",
                    f"    任务: {result['work_summary']}",
                    f"    超时: {result['timeout_seconds']}秒", 
                    f"    远程地址: {result['url']}",
                    f"    SSH转发: ssh -L {local_port}:127.0.0.1:{result['port']} your_user@your_server",
                    f"    本地访问: http://127.0.0.1:{local_port}/",
                    ""
                ])
        
        if failed_servers:
            report_lines.extend([
                f"❌ 失败的服务器 ({len(failed_servers)} 个):",
                ""
            ])
            
            for failed in failed_servers:
                session_id = failed.get('session_id', '未知')
                error = failed.get('error', '未知错误')
                report_lines.extend([
                    f"  🔴 {session_id}",
                    f"    错误: {error}",
                    ""
                ])
        
        if not results and not failed_servers:
            return "⚠️ 未提供服务器配置"
        
        # 添加使用说明
        if results:
            report_lines.extend([
                "💡 使用说明:",
                "  1. 在本地终端分别执行上述SSH转发命令",
                "  2. 每个服务器使用不同的本地端口避免冲突",
                "  3. 可以同时在多个浏览器标签页中访问不同的反馈界面",
                "  4. 使用 get_server_status 查看所有服务器状态"
            ])
        
        return "\n".join(report_lines)
        
    except Exception as e:
        return f"❌ 创建服务器池失败: {str(e)}"


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