#!/usr/bin/env python3
"""
SRI哈希值更新脚本
自动获取CDN资源的SRI哈希值并更新HTML模板
"""

import hashlib
import base64
import requests
import re
import os
from typing import Dict, List, Tuple

# CDN资源配置
CDN_RESOURCES = [
    {
        'name': 'marked',
        'version': '15.0.12',
        'url': 'https://cdn.jsdelivr.net/npm/marked@15.0.12/marked.min.js',
        'type': 'script'
    },
    {
        'name': 'mermaid',
        'version': '11.6.0',
        'url': 'https://cdn.jsdelivr.net/npm/mermaid@11.6.0/dist/mermaid.min.js',
        'type': 'script'
    },
    {
        'name': 'prismjs-css',
        'version': '1.30.0',
        'url': 'https://cdn.jsdelivr.net/npm/prismjs@1.30.0/themes/prism-tomorrow.min.css',
        'type': 'style'
    },
    {
        'name': 'prismjs-core',
        'version': '1.30.0',
        'url': 'https://cdn.jsdelivr.net/npm/prismjs@1.30.0/components/prism-core.min.js',
        'type': 'script'
    },
    {
        'name': 'prismjs-autoloader',
        'version': '1.30.0',
        'url': 'https://cdn.jsdelivr.net/npm/prismjs@1.30.0/plugins/autoloader/prism-autoloader.min.js',
        'type': 'script'
    }
]

def calculate_sri_hash(content: bytes, algorithm: str = 'sha384') -> str:
    """计算SRI哈希值"""
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(content)
    hash_digest = hash_obj.digest()
    hash_b64 = base64.b64encode(hash_digest).decode('ascii')
    return f"{algorithm}-{hash_b64}"

def fetch_resource_content(url: str) -> bytes:
    """获取资源内容"""
    print(f"正在获取: {url}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.content
    except requests.RequestException as e:
        print(f"获取资源失败 {url}: {e}")
        raise

def get_sri_hashes() -> Dict[str, str]:
    """获取所有资源的SRI哈希值"""
    sri_hashes = {}
    
    for resource in CDN_RESOURCES:
        try:
            content = fetch_resource_content(resource['url'])
            sri_hash = calculate_sri_hash(content)
            sri_hashes[resource['name']] = sri_hash
            print(f"✅ {resource['name']}: {sri_hash}")
        except Exception as e:
            print(f"❌ {resource['name']}: 获取失败 - {e}")
            sri_hashes[resource['name']] = "sha384-PLACEHOLDER"
    
    return sri_hashes

def update_html_template(sri_hashes: Dict[str, str]) -> None:
    """更新HTML模板中的SRI哈希值"""
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'frontend', 'templates', 'feedback.html'
    )
    
    if not os.path.exists(template_path):
        print(f"❌ 模板文件不存在: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新SRI哈希值
    replacements = [
        # Marked.js
        (r'(marked@15\.0\.12/marked\.min\.js["\s]+integrity=")[^"]*(")',
         f'\\1{sri_hashes.get("marked", "sha384-PLACEHOLDER")}\\2'),
        
        # Mermaid.js
        (r'(mermaid@11\.6\.0/dist/mermaid\.min\.js["\s]+integrity=")[^"]*(")',
         f'\\1{sri_hashes.get("mermaid", "sha384-PLACEHOLDER")}\\2'),
        
        # Prism.js CSS
        (r'(prismjs@1\.30\.0/themes/prism-tomorrow\.min\.css["\s]+rel="stylesheet"["\s]+integrity=")[^"]*(")',
         f'\\1{sri_hashes.get("prismjs-css", "sha384-PLACEHOLDER")}\\2'),
        
        # Prism.js Core
        (r'(prismjs@1\.30\.0/components/prism-core\.min\.js["\s]+integrity=")[^"]*(")',
         f'\\1{sri_hashes.get("prismjs-core", "sha384-PLACEHOLDER")}\\2'),
        
        # Prism.js Autoloader
        (r'(prismjs@1\.30\.0/plugins/autoloader/prism-autoloader\.min\.js["\s]+integrity=")[^"]*(")',
         f'\\1{sri_hashes.get("prismjs-autoloader", "sha384-PLACEHOLDER")}\\2'),
    ]
    
    updated_content = content
    for pattern, replacement in replacements:
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.MULTILINE)
    
    # 写回文件
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ HTML模板已更新: {template_path}")

def generate_sri_report(sri_hashes: Dict[str, str]) -> None:
    """生成SRI报告"""
    report_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'SRI_HASHES_REPORT.md'
    )
    
    report_content = """# CDN资源SRI哈希值报告

本报告包含所有外部CDN资源的SRI（子资源完整性）哈希值。

## 资源列表

| 资源名称 | 版本 | SRI哈希值 | URL |
|---------|------|-----------|-----|
"""
    
    for resource in CDN_RESOURCES:
        sri_hash = sri_hashes.get(resource['name'], 'N/A')
        report_content += f"| {resource['name']} | {resource['version']} | `{sri_hash}` | {resource['url']} |\n"
    
    report_content += f"""
## 更新时间

{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 验证方法

可以使用以下命令验证SRI哈希值：

```bash
curl -s [URL] | openssl dgst -sha384 -binary | openssl base64 -A
```

## 安全说明

- 所有资源都使用SHA-384算法计算哈希值
- 添加了`crossorigin="anonymous"`属性确保CORS安全
- 添加了`referrerpolicy="no-referrer"`防止信息泄露
- CSP策略限制了资源加载来源
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ SRI报告已生成: {report_path}")

def main():
    """主函数"""
    print("🔒 开始更新CDN资源SRI哈希值...")
    
    try:
        # 获取SRI哈希值
        sri_hashes = get_sri_hashes()
        
        # 更新HTML模板
        update_html_template(sri_hashes)
        
        # 生成报告
        generate_sri_report(sri_hashes)
        
        print("\n🎉 SRI哈希值更新完成！")
        print("\n📋 更新总结:")
        for name, hash_value in sri_hashes.items():
            status = "✅" if not hash_value.endswith("PLACEHOLDER") else "❌"
            print(f"{status} {name}: {hash_value}")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
