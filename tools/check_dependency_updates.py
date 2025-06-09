#!/usr/bin/env python3
"""
依赖更新检查脚本
检查外部依赖是否有新版本可用
"""

import requests
import json
import re
from typing import Dict, List, Tuple
from packaging import version

# 当前使用的依赖版本
CURRENT_DEPENDENCIES = {
    'marked': '15.0.12',
    'mermaid': '11.6.0', 
    'prismjs': '1.30.0'
}

def get_npm_latest_version(package_name: str) -> str:
    """获取NPM包的最新版本"""
    try:
        url = f"https://registry.npmjs.org/{package_name}/latest"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('version', 'unknown')
    except Exception as e:
        print(f"❌ 获取 {package_name} 版本失败: {e}")
        return 'unknown'

def compare_versions(current: str, latest: str) -> Tuple[bool, str]:
    """比较版本号"""
    if latest == 'unknown':
        return False, "无法获取最新版本"
    
    try:
        current_ver = version.parse(current)
        latest_ver = version.parse(latest)
        
        if latest_ver > current_ver:
            # 判断更新类型
            if latest_ver.major > current_ver.major:
                return True, "主版本更新"
            elif latest_ver.minor > current_ver.minor:
                return True, "次版本更新"
            else:
                return True, "补丁更新"
        elif latest_ver == current_ver:
            return False, "已是最新版本"
        else:
            return False, "当前版本较新"
    except Exception as e:
        return False, f"版本比较失败: {e}"

def check_security_advisories(package_name: str) -> List[str]:
    """检查安全公告（简化版）"""
    # 这里可以集成GitHub Security Advisory API
    # 暂时返回空列表
    return []

def generate_update_report() -> None:
    """生成更新报告"""
    print("🔍 检查依赖更新...")
    print("=" * 60)
    
    updates_available = []
    
    for package, current_ver in CURRENT_DEPENDENCIES.items():
        print(f"\n📦 检查 {package}...")
        latest_ver = get_npm_latest_version(package)
        
        has_update, update_type = compare_versions(current_ver, latest_ver)
        
        print(f"   当前版本: {current_ver}")
        print(f"   最新版本: {latest_ver}")
        print(f"   状态: {update_type}")
        
        if has_update:
            updates_available.append({
                'package': package,
                'current': current_ver,
                'latest': latest_ver,
                'type': update_type
            })
            
            # 检查安全公告
            advisories = check_security_advisories(package)
            if advisories:
                print(f"   ⚠️ 安全公告: {len(advisories)} 个")
        
        print("-" * 40)
    
    # 生成总结
    print(f"\n📋 检查完成!")
    if updates_available:
        print(f"🔄 发现 {len(updates_available)} 个可更新的依赖:")
        for update in updates_available:
            priority = "🔴 高优先级" if "主版本" in update['type'] else "🟡 中优先级" if "次版本" in update['type'] else "🟢 低优先级"
            print(f"   • {update['package']}: {update['current']} → {update['latest']} ({update['type']}) {priority}")
        
        print(f"\n💡 建议操作:")
        print(f"   1. 查看更新日志确认兼容性")
        print(f"   2. 在测试环境验证功能")
        print(f"   3. 更新 DEPENDENCY_VERSIONS.md")
        print(f"   4. 更新 HTML 模板中的版本号")
    else:
        print("✅ 所有依赖都是最新版本!")

def main():
    """主函数"""
    try:
        generate_update_report()
    except KeyboardInterrupt:
        print("\n\n⏹️ 检查被用户中断")
    except Exception as e:
        print(f"\n❌ 检查过程中出现错误: {e}")

if __name__ == "__main__":
    main()
