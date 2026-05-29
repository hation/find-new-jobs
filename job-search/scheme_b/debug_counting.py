#!/usr/bin/env python3
"""
调试技能脚本计数问题
"""

import os

def debug_counting():
    print("🔍 调试技能脚本计数问题")
    print("=" * 60)
    
    # 工作目录
    workspace = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"
    os.chdir(workspace)
    
    print(f"📁 工作目录: {workspace}")
    
    # 1. 读取security_ids（按照修复后的脚本逻辑）
    print("\n📋 1. 读取security_ids (修复后逻辑):")
    security_ids = []
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
                            security_ids.append(security_id)
                else:
                    if len(line) > 100:
                        security_ids.append(line)
    
    print(f"   ✅ 读取security_ids数: {len(security_ids)}")
    print(f"   示例: {security_ids[0][:50]}...")
    
    # 2. 读取fetched_ids（按照脚本逻辑）
    print("\n📋 2. 读取fetched_ids (脚本逻辑):")
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
    if fetched_ids:
        sample = next(iter(fetched_ids))
        print(f"   示例: {sample[:50]}...")
    
    # 3. 计算未获取
    print("\n📋 3. 计算未获取:")
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    print(f"   ✅ 未获取数: {len(unfetched)}")
    
    # 4. 验证数据一致性
    print("\n🔍 4. 数据验证:")
    
    # 检查重复
    security_set = set(security_ids)
    print(f"   • security_ids唯一值: {len(security_set)} (重复: {len(security_ids) - len(security_set)})")
    
    # 检查格式差异
    print(f"   • 检查格式问题:")
    for i, sid in enumerate(list(security_set)[:3]):
        print(f"     security_id[{i}]: 长度={len(sid)}, 包含~={'~' in sid}")
    
    # 5. 详细对比
    print("\n🔍 5. 详细对比（前3个security_id）:")
    for i, sid in enumerate(list(security_set)[:3]):
        in_fetched = sid in fetched_ids
        print(f"   [{i}] {sid[:30]}...")
        print(f"      长度: {len(sid)}, 在fetched中: {in_fetched}")
    
    # 6. 检查可能的格式不匹配
    print("\n🔍 6. 检查可能的格式不匹配:")
    
    # 检查security_ids中的格式
    print(f"   • security_ids格式检查:")
    for sid in security_ids[:2]:
        print(f"     - {sid[:30]}... 长度={len(sid)}")
    
    # 检查fetched_ids中的格式
    print(f"   • fetched_ids格式检查:")
    for sid in list(fetched_ids)[:2]:
        print(f"     - {sid[:30]}... 长度={len(sid)}")
    
    # 7. 手动验证几个是否真的匹配
    print("\n🔍 7. 手动验证匹配:")
    test_count = min(5, len(security_ids), len(fetched_ids))
    matches = 0
    for i in range(test_count):
        sec_id = list(security_set)[i]
        if sec_id in fetched_ids:
            matches += 1
            print(f"   ✅ [{i}] 匹配: {sec_id[:30]}...")
        else:
            print(f"   ❌ [{i}] 不匹配: {sec_id[:30]}...")
    
    print(f"\n📊 匹配率: {matches}/{test_count} ({matches*100//test_count}%)")
    
    # 8. 检查fetched_security_ids.txt的实际内容
    print("\n📋 8. 检查fetched_security_ids.txt内容:")
    with open('fetched_security_ids.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        print(f"   • 总行数: {len(lines)}")
        print(f"   • 注释行: {sum(1 for l in lines if l.strip().startswith('#'))}")
        print(f"   • 空行: {sum(1 for l in lines if not l.strip())}")
        print(f"   • 有效行: {len(lines) - sum(1 for l in lines if not l.strip() or l.strip().startswith('#'))}")
        
        # 显示前几行
        print(f"   • 前3行内容:")
        for i, line in enumerate(lines[:3]):
            print(f"     [{i}] {line.strip()[:80]}")

if __name__ == "__main__":
    debug_counting()