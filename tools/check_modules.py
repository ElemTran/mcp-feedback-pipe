#!/usr/bin/env python3
"""
检查模块导入状态
"""

import sys
import os

print('=== 检查模块导入状态 ===')
print('当前工作目录:', os.getcwd())
print('Python路径:')
for i, path in enumerate(sys.path):
    print(f'  {i}: {path}')

print('\n=== 尝试导入backend ===')
try:
    import backend
    print('✓ backend导入成功')
    print('包位置:', backend.__file__)
except Exception as e:
    print('✗ 导入失败:', e)

print('\n=== 检查sys.modules中的相关模块 ===')
for name in sorted(sys.modules.keys()):
    if 'backend' in name:
        print(f'  {name}: {sys.modules[name]}')

print('\n=== 尝试导入server模块 ===')
try:
    from . import server
    print('✓ server模块导入成功')
    print('server位置:', server.__file__)
except Exception as e:
    print('✗ server导入失败:', e)

print('\n=== 检查MCP工具注册 ===')
try:
    from backend.server import mcp
    print('✓ mcp对象导入成功')
    print('mcp对象类型:', type(mcp))
    
    # 尝试列出工具
    try:
        import asyncio
        async def check_tools():
            tools = await mcp.list_tools()
            print(f'注册的工具数量: {len(tools)}')
            for tool in tools:
                print(f'  - {tool.name}: {tool.description[:50]}...')
        
        asyncio.run(check_tools())
    except Exception as e:
        print('✗ 列出工具失败:', e)
        
except Exception as e:
    print('✗ mcp对象导入失败:', e)
