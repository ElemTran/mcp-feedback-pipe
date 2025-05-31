#!/usr/bin/env python
"""
MCP反馈通道 - PyPI发布脚本
用于将项目发布到Python Package Index (PyPI)
"""

import os
import sys
import subprocess
import getpass
import json
from pathlib import Path

def mask_token(cmd):
    """脱敏token信息"""
    if "--token" in cmd:
        parts = cmd.split()
        for i, part in enumerate(parts):
            if part == "--token" and i + 1 < len(parts):
                token = parts[i + 1]
                if token.startswith("pypi-") and len(token) > 10:
                    # 只显示前缀和后4位，中间用*代替
                    masked = f"pypi-{'*' * (len(token) - 9)}{token[-4:]}"
                    parts[i + 1] = masked
                break
        return " ".join(parts)
    return cmd

def run_command(cmd, check=True, mask_sensitive=False):
    """运行命令并返回结果"""
    display_cmd = mask_token(cmd) if mask_sensitive else cmd
    print(f"🔧 执行: {display_cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {result.stderr}")
        sys.exit(1)
    return result

def check_dependencies():
    """检查发布依赖"""
    print("🔍 检查发布依赖...")
    
    # 检查uv
    result = run_command("uv --version", check=False)
    if result.returncode != 0:
        print("❌ uv未安装，正在安装...")
        run_command("pip install uv")
        print("✅ uv安装完成")
    else:
        print(f"✅ uv已安装: {result.stdout.strip()}")

def get_project_info():
    """获取项目信息"""
    print("📋 读取项目信息...")
    
    # 读取pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ 未找到pyproject.toml文件")
        sys.exit(1)
    
    with open(pyproject_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简单解析版本号（更健壮的方式应该用toml库）
    for line in content.split('\n'):
        if line.strip().startswith('version ='):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        print("❌ 未找到版本号")
        sys.exit(1)
    
    return {
        "name": "mcp-feedback-pipe",
        "version": version
    }

def build_package():
    """构建Python包"""
    print("🏗️ 构建Python包...")
    
    # 清理旧的构建文件
    run_command("rm -rf dist/", check=False)
    
    # 构建包
    run_command("uv build")
    
    # 检查构建结果
    dist_files = list(Path("dist").glob("*"))
    if len(dist_files) == 0:
        print("❌ 构建失败，没有生成分发文件")
        sys.exit(1)
    
    print("✅ 构建完成:")
    for file in dist_files:
        print(f"   📦 {file.name}")
    
    return dist_files

def get_testpypi_token():
    """获取TestPyPI API token"""
    print("\n🔑 TestPyPI认证配置")
    print("请访问 https://test.pypi.org/manage/account/token/ 创建TestPyPI API token")
    print("Token范围选择: 'Entire account' (首次发布) 或 'Scope to project' (后续)")
    
    token = getpass.getpass("请输入TestPyPI API token (格式: pypi-...): ")
    
    if not token.startswith("pypi-"):
        print("❌ Token格式错误，应该以 'pypi-' 开头")
        return get_testpypi_token()
    
    return token

def get_pypi_token():
    """获取PyPI API token"""
    print("\n🔑 PyPI认证配置")
    print("请访问 https://pypi.org/manage/account/token/ 创建PyPI API token")
    print("Token范围选择: 'Entire account' (首次发布) 或 'Scope to project' (后续)")
    
    token = getpass.getpass("请输入PyPI API token (格式: pypi-...): ")
    
    if not token.startswith("pypi-"):
        print("❌ Token格式错误，应该以 'pypi-' 开头")
        return get_pypi_token()
    
    return token

def publish_to_testpypi(token):
    """发布到TestPyPI（测试环境）"""
    print("🧪 发布到TestPyPI（测试环境）...")
    
    cmd = f'uv publish --token {token} --publish-url https://test.pypi.org/legacy/'
    result = run_command(cmd, check=False, mask_sensitive=True)
    
    if result.returncode == 0:
        print("✅ TestPyPI发布成功!")
        print("🔗 查看: https://test.pypi.org/project/mcp-feedback-pipe/")
        print("🧪 测试安装: pip install -i https://test.pypi.org/simple/ mcp-feedback-pipe")
        return True
    else:
        print(f"❌ TestPyPI发布失败: {result.stderr}")
        if "403 Forbidden" in result.stderr:
            print("💡 可能的解决方案:")
            print("   1. 确认您使用的是TestPyPI的token (https://test.pypi.org/manage/account/token/)")
            print("   2. 确认token权限正确（建议使用'Entire account'权限）")
            print("   3. 确认包名在TestPyPI上没有被占用")
        return False

def publish_to_pypi(token):
    """发布到正式PyPI"""
    print("🚀 发布到正式PyPI...")
    
    confirm = input("确认发布到正式PyPI？这将公开发布包 (y/N): ")
    if confirm.lower() != 'y':
        print("❌ 用户取消发布")
        return False
    
    cmd = f'uv publish --token {token}'
    result = run_command(cmd, check=False, mask_sensitive=True)
    
    if result.returncode == 0:
        print("🎉 正式PyPI发布成功!")
        print("🔗 查看: https://pypi.org/project/mcp-feedback-pipe/")
        return True
    else:
        print(f"❌ 正式PyPI发布失败: {result.stderr}")
        if "403 Forbidden" in result.stderr:
            print("💡 可能的解决方案:")
            print("   1. 确认您使用的是PyPI的token (https://pypi.org/manage/account/token/)")
            print("   2. 确认token权限正确（建议使用'Entire account'权限）")
            print("   3. 确认包名在PyPI上没有被占用")
        return False

def test_installation():
    """测试安装"""
    print("\n🧪 测试uvx安装...")
    
    # 清除可能的本地缓存
    run_command("uvx cache clean", check=False)
    
    # 测试从PyPI安装
    print("测试命令: uvx mcp-feedback-pipe")
    print("如果成功，应该启动MCP服务器")

def save_publish_config(project_info, success_testpypi, success_pypi):
    """保存发布配置"""
    config = {
        "project": project_info,
        "last_publish": {
            "testpypi": success_testpypi,
            "pypi": success_pypi,
            "timestamp": subprocess.check_output("date", shell=True, text=True).strip()
        }
    }
    
    config_path = Path(".publish_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"📝 发布配置已保存到 {config_path}")

def main():
    """主函数"""
    print("🎯 MCP反馈通道 - PyPI发布工具")
    print("=" * 50)
    
    # 检查是否在项目根目录
    if not Path("pyproject.toml").exists():
        print("❌ 请在项目根目录运行此脚本")
        sys.exit(1)
    
    try:
        # 1. 检查依赖
        check_dependencies()
        
        # 2. 获取项目信息
        project_info = get_project_info()
        print(f"📦 项目: {project_info['name']} v{project_info['version']}")
        
        # 3. 构建包
        dist_files = build_package()
        
        # 4. 选择发布方式
        print("\n📤 发布选项:")
        print("1. 仅发布到TestPyPI（推荐首次发布）")
        print("2. 发布到TestPyPI + 正式PyPI")
        print("3. 仅发布到正式PyPI")
        
        choice = input("请选择 (1-3): ").strip()
        
        success_testpypi = False
        success_pypi = False
        
        # 5. 根据选择获取相应token并发布
        if choice in ['1', '2']:
            testpypi_token = get_testpypi_token()
            success_testpypi = publish_to_testpypi(testpypi_token)
            
        if choice in ['2', '3'] and (choice == '3' or success_testpypi):
            pypi_token = get_pypi_token()
            success_pypi = publish_to_pypi(pypi_token)
        
        # 6. 保存配置
        save_publish_config(project_info, success_testpypi, success_pypi)
        
        # 7. 测试指导
        if success_pypi:
            test_installation()
        
        print("\n🎊 发布流程完成!")
        if success_pypi:
            print("🌟 用户现在可以使用: uvx mcp-feedback-pipe")
        
    except KeyboardInterrupt:
        print("\n❌ 用户中断发布")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 发布过程中出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 