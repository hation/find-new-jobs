#!/usr/bin/env python3
"""
运行技能脚本但只到计数部分
"""

import os
import sys

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'scripts'))

# 导入脚本但修改执行
original_script = os.path.join(script_dir, 'scripts', 'fetch_details_conservative_v2.py')

# 读取脚本内容
with open(original_script, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到main函数并修改
# 在计数完成后就退出
modified_content = content.replace(
    'def main():',
    '''def debug_main():
    print("🔍 调试模式：只运行计数部分")
    print("=" * 60)'''
).replace(
    'if __name__ == "__main__":',
    '''if __name__ == "__main__":
    debug_main()'''
)

# 在计数完成后添加退出
modified_content = modified_content.replace(
    '    print(f"   未获取的security_id: {len(unfetched)} 个")\n',
    '    print(f"   未获取的security_id: {len(unfetched)} 个")\n    print("\\n🔍 调试完成，退出")\n    sys.exit(0)\n'
)

# 执行修改后的脚本
exec(modified_content)

# 如果上面没有执行，运行原始脚本的main函数
print("⚠️ 修改未生效，尝试直接运行...")

# 直接导入并运行
from fetch_details_conservative_v2 import main
main()