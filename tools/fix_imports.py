#!/usr/bin/env python3
"""
批量修复导入语句的脚本
1. 将所有内部导入统一为 from backend... 格式
2. 移除不必要的 sys.path 修改
3. 修复旧包名导入
"""

import os
import re
import sys
from pathlib import Path

def fix_imports_in_file(file_path):
    """
    修复单个文件中的导入语句
    
    参数:
        file_path (str): 要处理的文件路径
        
    返回:
        bool: 如果文件被修改返回True，否则返回False
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = False
        
        # 1. 修复旧包名导入
        # 替换 from mcp_feedback_pipe 为 from backend
        content, count1 = re.subn(
            r'from\s+mcp_feedback_pipe(\.|\s+import)', 
            r'from backend\1', 
            content
        )
        
        # 替换 import mcp_feedback_pipe 为 import backend
        content, count2 = re.subn(
            r'import\s+mcp_feedback_pipe(\s+as|\s*$|\s*#|\s*\n)', 
            r'import backend\1', 
            content
        )
        
        # 2. 修复 src.mcp_feedback_pipe 导入
        content, count3 = re.subn(
            r'from\s+src\.mcp_feedback_pipe(\.|\s+import)', 
            r'from backend\1', 
            content
        )
        
        # 3. 移除 sys.path 修改相关的代码块
        patterns_to_remove = [
            # 标准的 sys.path 添加模式
            r'#\s*添加.*?到.*?路径\s*\n.*?sys\.path\.insert\(.*?\)\s*\n',
            r'#\s*添加.*?目录到路径\s*\n.*?sys\.path\.insert\(.*?\)\s*\n',
            r'.*?current_dir\s*=\s*os\.path\.dirname.*?\n.*?src_dir\s*=\s*os\.path\.join.*?\n.*?if\s+src_dir\s+not\s+in\s+sys\.path:\s*\n\s*sys\.path\.insert.*?\n',
            r'.*?project_root\s*=\s*Path.*?\n.*?src_dir\s*=\s*project_root.*?\n.*?sys\.path\.insert.*?\n',
            # 更通用的模式
            r'^\s*sys\.path\.(?:insert|append)\([^)]*\)\s*\n?',
            # 移除空的 try-except 块
            r'^\s*try:\s*\n\s*import\s+sys\s*\n\s*except\s+ImportError:\s*\n\s*pass\s*\n',
        ]
        
        for pattern in patterns_to_remove:
            content, count = re.subn(pattern, '', content, flags=re.MULTILINE | re.DOTALL)
            if count > 0:
                changes_made = True
        
        # 4. 清理多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip() + '\n'
        
        # 如果有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已修复: {file_path}")
            return True
        else:
            print(f"- 无需修复: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ 修复失败 {file_path}: {e}")
        return False

def collect_python_files(directories):
    """
    收集指定目录中的所有Python文件
    
    参数:
        directories (list): 要扫描的目录和文件列表
        
    返回:
        list: 找到的所有Python文件路径
    """
    python_files = []
    
    for item in directories:
        item_path = Path(item)
        if not item_path.exists():
            print(f"警告: 路径不存在: {item}")
            continue
            
        if item_path.is_file():
            if item_path.suffix == '.py':
                python_files.append(str(item_path))
        elif item_path.is_dir():
            for root, _, files in os.walk(item):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(str(Path(root) / file))
    
    return python_files

def main():
    """主函数"""
    print("开始批量修复导入语句...\n")
    
    # 要处理的目录和文件
    targets = [
        "backend",           # 后端代码
        "tests",             # 测试目录
        "tools",             # 工具脚本
        "scripts",           # 其他脚本
    ]
    
    # 收集所有Python文件
    python_files = collect_python_files(targets)
    python_files = sorted(list(set(python_files)))  # 去重并排序
    
    if not python_files:
        print("未找到任何Python文件，请检查路径设置")
        return
    
    print(f"找到 {len(python_files)} 个Python文件")
    print("-" * 50)
    
    # 处理文件
    fixed_files = 0
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_files += 1
    
    # 输出统计信息
    print("\n" + "=" * 50)
    print("修复完成！")
    print("=" * 50)
    print(f"总文件数: {len(python_files)}")
    print(f"已修复文件数: {fixed_files}")
    print(f"无需修复文件数: {len(python_files) - fixed_files}")
    
    if fixed_files > 0:
        print("\n建议: 请运行测试以确保修复没有引入新的问题")
        print("命令: python -m pytest tests/ -v")

if __name__ == "__main__":
    main()
