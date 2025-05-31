#!/usr/bin/env python3
"""
版本管理工具
自动更新项目中所有需要版本号的文件
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Tuple, Optional

# 添加src目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

try:
    from mcp_feedback_pipe.version import __version__, __version_info__
except ImportError:
    print("❌ 无法导入版本信息，请确保项目结构正确")
    sys.exit(1)


class VersionManager:
    """版本管理器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.current_version = __version__
        self.current_version_info = __version_info__
        
        # 需要更新版本号的文件列表
        self.version_files = {
            "pyproject.toml": self._update_pyproject_toml,
            "src/mcp_feedback_pipe/version.py": self._update_version_py,
            "src/mcp_feedback_pipe/__init__.py": self._update_init_py,
        }
    
    def parse_version(self, version_str: str) -> Tuple[int, int, int]:
        """解析版本字符串为元组"""
        try:
            parts = version_str.split('.')
            if len(parts) != 3:
                raise ValueError("版本号必须是 x.y.z 格式")
            return tuple(int(part) for part in parts)
        except ValueError as e:
            raise ValueError(f"无效的版本号格式: {version_str}. {e}")
    
    def version_to_string(self, version_tuple: Tuple[int, int, int]) -> str:
        """将版本元组转换为字符串"""
        return f"{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"
    
    def increment_version(self, increment_type: str = "patch") -> str:
        """递增版本号"""
        major, minor, patch = self.current_version_info
        
        if increment_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif increment_type == "minor":
            minor += 1
            patch = 0
        elif increment_type == "patch":
            patch += 1
        else:
            raise ValueError("increment_type 必须是 'major', 'minor', 或 'patch'")
        
        return self.version_to_string((major, minor, patch))
    
    def _update_pyproject_toml(self, new_version: str) -> bool:
        """更新 pyproject.toml 中的版本号"""
        file_path = self.project_root / "pyproject.toml"
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        try:
            content = file_path.read_text(encoding='utf-8')
            # 使用正则表达式替换版本号
            pattern = r'version\s*=\s*"[^"]*"'
            replacement = f'version = "{new_version}"'
            new_content = re.sub(pattern, replacement, content)
            
            if new_content != content:
                file_path.write_text(new_content, encoding='utf-8')
                print(f"✅ 已更新 pyproject.toml: {new_version}")
                return True
            else:
                print(f"⚠️  pyproject.toml 中未找到版本号模式")
                return False
        except Exception as e:
            print(f"❌ 更新 pyproject.toml 失败: {e}")
            return False
    
    def _update_version_py(self, new_version: str) -> bool:
        """更新 version.py 中的版本号"""
        file_path = self.project_root / "src/mcp_feedback_pipe/version.py"
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        try:
            version_tuple = self.parse_version(new_version)
            content = file_path.read_text(encoding='utf-8')
            
            # 更新 __version__
            content = re.sub(
                r'__version__\s*=\s*"[^"]*"',
                f'__version__ = "{new_version}"',
                content
            )
            
            # 更新 __version_info__
            content = re.sub(
                r'__version_info__\s*=\s*\([^)]*\)',
                f'__version_info__ = {version_tuple}',
                content
            )
            
            # 更新版本历史（添加新版本到顶部）
            history_pattern = r'(VERSION_HISTORY\s*=\s*\{)\s*'
            if re.search(history_pattern, content):
                # 获取当前时间作为版本描述
                import datetime
                today = datetime.date.today().strftime("%Y-%m-%d")
                new_entry = f'    "{new_version}": "版本更新 - {today}",'
                
                content = re.sub(
                    history_pattern,
                    f'\\1\n{new_entry}\n    ',
                    content
                )
            
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ 已更新 version.py: {new_version}")
            return True
        except Exception as e:
            print(f"❌ 更新 version.py 失败: {e}")
            return False
    
    def _update_init_py(self, new_version: str) -> bool:
        """检查 __init__.py 是否正确导入版本信息"""
        file_path = self.project_root / "src/mcp_feedback_pipe/__init__.py"
        if not file_path.exists():
            print(f"❌ 文件不存在: {file_path}")
            return False
        
        try:
            content = file_path.read_text(encoding='utf-8')
            # 检查是否有正确的导入语句
            if "from .version import __version__" in content:
                print(f"✅ __init__.py 版本导入正确")
                return True
            else:
                print(f"⚠️  __init__.py 可能需要手动检查版本导入")
                return True  # 不阻止流程
        except Exception as e:
            print(f"❌ 检查 __init__.py 失败: {e}")
            return False
    
    def update_all_versions(self, new_version: str) -> bool:
        """更新所有文件中的版本号"""
        print(f"🔄 开始更新版本号: {self.current_version} → {new_version}")
        
        # 验证新版本格式
        try:
            self.parse_version(new_version)
        except ValueError as e:
            print(f"❌ {e}")
            return False
        
        success_count = 0
        total_count = len(self.version_files)
        
        for file_name, update_func in self.version_files.items():
            if update_func(new_version):
                success_count += 1
            else:
                print(f"❌ 更新失败: {file_name}")
        
        if success_count == total_count:
            print(f"✅ 所有文件版本号更新成功! ({success_count}/{total_count})")
            return True
        else:
            print(f"⚠️  部分文件更新失败 ({success_count}/{total_count})")
            return False
    
    def get_version_info(self) -> dict:
        """获取当前版本信息"""
        return {
            "current_version": self.current_version,
            "current_version_info": self.current_version_info,
            "next_patch": self.increment_version("patch"),
            "next_minor": self.increment_version("minor"),
            "next_major": self.increment_version("major"),
        }


def main():
    """主函数"""
    print("🎯 MCP反馈通道 - 版本管理工具")
    print("=" * 50)
    
    # 初始化版本管理器
    vm = VersionManager(project_root)
    
    # 显示当前版本信息
    info = vm.get_version_info()
    print(f"📦 当前版本: {info['current_version']}")
    print(f"🔢 版本信息: {info['current_version_info']}")
    print()
    
    # 显示可选的版本递增选项
    print("📈 可选的版本递增:")
    print(f"  1. Patch (补丁): {info['next_patch']}")
    print(f"  2. Minor (次要): {info['next_minor']}")
    print(f"  3. Major (主要): {info['next_major']}")
    print("  4. 自定义版本号")
    print()
    
    # 获取用户选择
    try:
        choice = input("请选择版本更新方式 (1-4): ").strip()
        
        if choice == "1":
            new_version = info['next_patch']
        elif choice == "2":
            new_version = info['next_minor']
        elif choice == "3":
            new_version = info['next_major']
        elif choice == "4":
            new_version = input("请输入新版本号 (格式: x.y.z): ").strip()
        else:
            print("❌ 无效选择")
            return 1
        
        # 确认更新
        print(f"\n🔄 准备更新版本: {info['current_version']} → {new_version}")
        confirm = input("确认更新? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            if vm.update_all_versions(new_version):
                print(f"\n🎉 版本更新完成! 新版本: {new_version}")
                print("💡 提示: 记得运行构建和发布脚本")
                return 0
            else:
                print("\n❌ 版本更新失败")
                return 1
        else:
            print("❌ 用户取消操作")
            return 1
            
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        return 1
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 