#!/usr/bin/env python3
"""
测试boss命令是否可用
"""

import subprocess
import os

print("🔍 测试boss命令")
print("=" * 60)

# 测试1: 直接调用boss命令
print("测试1: 直接调用'boss'命令")
try:
    result = subprocess.run(['boss', '--version'], capture_output=True, text=True)
    print(f"  返回码: {result.returncode}")
    print(f"  输出: {result.stdout.strip()}")
    print(f"  错误: {result.stderr.strip()}")
    print(f"  ✅ boss命令可用")
except FileNotFoundError as e:
    print(f"  ❌ FileNotFoundError: {e}")
    print(f"  💡 boss命令未找到")
except Exception as e:
    print(f"  ❌ 其他错误: {e}")

print()

# 测试2: 使用完整路径
print("测试2: 使用完整路径")
boss_path = '/Library/Frameworks/Python.framework/Versions/3.12/bin/boss'
if os.path.exists(boss_path):
    print(f"  ✅ boss命令存在: {boss_path}")
    try:
        result = subprocess.run([boss_path, '--version'], capture_output=True, text=True)
        print(f"  返回码: {result.returncode}")
        print(f"  输出: {result.stdout.strip()}")
        print(f"  ✅ 完整路径可用")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
else:
    print(f"  ❌ boss命令不存在: {boss_path}")

print()

# 测试3: 检查环境变量
print("测试3: 检查环境变量")
print(f"  PATH: {os.environ.get('PATH', '未设置')}")
print(f"  PYTHONPATH: {os.environ.get('PYTHONPATH', '未设置')}")

print()

# 测试4: 尝试获取一个详情（简单测试）
print("测试4: 尝试获取详情（简单测试）")
test_security_id = "dd8Q-bwMsw2ES-d1m8PnUuvF803t2eM88v_t5Hz9fyCz7LKKBbZ609J-AvYFC8jPL2PidXJ0RJYZhjze"
try:
    # 只运行1秒，避免长时间等待
    result = subprocess.run(['timeout', '1', 'boss', 'detail', test_security_id], 
                          capture_output=True, text=True, timeout=2)
    print(f"  返回码: {result.returncode}")
    print(f"  输出前100字符: {result.stdout[:100] if result.stdout else '空'}")
    if result.returncode == 0:
        print(f"  ✅ 获取详情成功")
    else:
        print(f"  ⚠️  获取详情失败，返回码: {result.returncode}")
except subprocess.TimeoutExpired:
    print(f"  ⏱️  命令超时（可能正在运行）")
except Exception as e:
    print(f"  ❌ 错误: {e}")