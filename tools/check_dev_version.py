#!/usr/bin/env python3
"""
验证是否使用开发版本
"""

import sys
import os

print('=== 验证开发版本 ===')
print('Python路径:')
for i, path in enumerate(sys.path[:5]):  # 只显示前5个
    print(f'  {i}: {path}')

print('\n=== 导入backend ===')
try:
    import backend
    print('✓ backend导入成功')
    print('包位置:', backend.__file__)
    
    # 检查是否是开发版本
    if '/backend/' in backend.__file__:
        print('✅ 正在使用开发版本')
    else:
        print('❌ 正在使用安装版本')
        
except Exception as e:
    print('✗ 导入失败:', e)

print('\n=== 检查MCP工具 ===')
try:
    from backend.server import mcp
    print('✓ mcp对象导入成功')
    
    import asyncio
    async def check_tools():
        tools = await mcp.list_tools()
        print(f'注册的工具数量: {len(tools)}')
        for tool in tools:
            print(f'  - {tool.name}')
    
    asyncio.run(check_tools())
    
except Exception as e:
    print('✗ MCP工具检查失败:', e)
