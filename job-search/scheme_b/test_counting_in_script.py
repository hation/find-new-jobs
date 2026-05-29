#!/usr/bin/env python3
"""
模拟技能脚本的完整计数逻辑
"""

import os
import sys

# 模拟技能脚本的环境
workspace = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"
os.chdir(workspace)

print("🔍 模拟技能脚本的完整计数逻辑")
print("=" * 60)
print(f"📁 工作目录: {workspace}")

# 1. 读取security_ids（完全按照修复后的脚本逻辑）
print("\n📋 1. 读取security_ids:")
security_ids = []
with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            security_ids.append(line)  # ❌ 注意：这是脚本修复前的错误逻辑！

print(f"   ❌ 脚本修复前的逻辑: {len(security_ids)}个")
print(f"   示例: {security_ids[0][:80]}")

# 2. 修复后的逻辑
print("\n📋 2. 修复后的读取逻辑:")
security_ids_fixed = []
with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            # 修复后的逻辑：处理|分隔符
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 1:
                    security_id = parts[0].strip()
                    if security_id and len(security_id) > 100:
                        security_ids_fixed.append(security_id)
            else:
                if len(line) > 100:
                    security_ids_fixed.append(line)

print(f"   ✅ 修复后的逻辑: {len(security_ids_fixed)}个")
print(f"   示例: {security_ids_fixed[0][:50]}...")

# 3. 读取fetched_ids（按照脚本逻辑）
print("\n📋 3. 读取fetched_ids:")
fetched_ids = set()
fetched_file = 'fetched_security_ids.txt'
if os.path.exists(fetched_file):
    with open(fetched_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 1:
                    fetched_ids.add(parts[0].strip())
            else:
                fetched_ids.add(line)

print(f"   ✅ 读取fetched_ids数: {len(fetched_ids)}")

# 4. 计算未获取（使用两种逻辑）
print("\n📋 4. 计算未获取:")
# 错误逻辑的未获取
unfetched_wrong = [sid for sid in security_ids if sid not in fetched_ids]
print(f"   ❌ 错误逻辑未获取: {len(unfetched_wrong)}个")

# 正确逻辑的未获取
unfetched_correct = [sid for sid in security_ids_fixed if sid not in fetched_ids]
print(f"   ✅ 正确逻辑未获取: {len(unfetched_correct)}个")

# 5. 分析差异
print("\n🔍 5. 分析差异:")
if len(unfetched_wrong) > len(unfetched_correct):
    diff = len(unfetched_wrong) - len(unfetched_correct)
    print(f"   • 错误逻辑多计算了 {diff} 个")
    print(f"   • 原因: security_ids中包含职位名称，导致比较错误")
    
    # 显示几个示例
    print(f"   • 示例对比:")
    for i in range(min(3, len(unfetched_wrong))):
        wrong_sid = unfetched_wrong[i]
        # 检查是否是包含|的完整行
        if '|' in wrong_sid:
            print(f"     [{i}] ❌ 错误格式: {wrong_sid[:60]}...")
            # 提取纯security_id部分
            pure_sid = wrong_sid.split('|')[0]
            is_in_fetched = pure_sid in fetched_ids
            print(f"         纯security_id: {pure_sid[:30]}..., 在fetched中: {is_in_fetched}")

# 6. 验证脚本实际显示的值
print("\n📋 6. 验证脚本实际显示:")
# 模拟脚本的打印
print(f"   总security_id数: {len(security_ids_fixed)}")
print(f"   已获取记录: {len(fetched_ids)} 个")
print(f"   未获取的security_id: {len(unfetched_correct)} 个")

# 7. 检查是否还有其他计数问题
print("\n🔍 7. 检查其他可能的计数问题:")
# 读取all_security_ids_final.txt的实际行数
with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
    all_lines = f.readlines()
    total_lines = len(all_lines)
    comment_lines = sum(1 for l in all_lines if l.strip().startswith('#'))
    empty_lines = sum(1 for l in all_lines if not l.strip())
    valid_lines = total_lines - comment_lines - empty_lines
    
print(f"   • 文件总行数: {total_lines}")
print(f"   • 注释行: {comment_lines}")
print(f"   • 空行: {empty_lines}")
print(f"   • 有效行: {valid_lines}")
print(f"   • 脚本读取: {len(security_ids_fixed)}")

if valid_lines != len(security_ids_fixed):
    print(f"   ❌ 行数不匹配!")
else:
    print(f"   ✅ 行数匹配正确")