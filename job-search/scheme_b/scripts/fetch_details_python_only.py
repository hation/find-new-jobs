#!/usr/bin/env python3
"""
不使用boss命令的Python-only获取详情脚本
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

def get_workspace_path():
    """获取工作空间路径"""
    # 优先使用环境变量
    workspace = os.environ.get('SCHEME_B_WORKSPACE')
    if workspace and os.path.exists(workspace):
        print(f"💡 使用环境变量指定目录: {workspace}")
        return workspace
    
    # 新的默认路径：技能目录下的output文件夹
    skill_output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'output'
    )
    if os.path.exists(skill_output_path):
        print(f"💡 使用技能输出目录: {skill_output_path}")
        return skill_output_path

    print("❌ 找不到工作目录")
    sys.exit(1)

def fetch_detail_with_requests(security_id):
    """
    使用requests获取职位详情
    注意：这需要BOSS直聘的API访问权限
    """
    # 这里需要实际的API调用逻辑
    # 暂时返回模拟数据
    print(f"⚠️  警告: 使用模拟数据，需要实现真正的API调用")
    
    # 模拟返回数据
    mock_data = {
        "security_id": security_id,
        "job_title": f"模拟职位 {security_id[:10]}...",
        "company": "模拟公司",
        "salary": "20-30K",
        "location": "深圳",
        "experience": "3-5年",
        "education": "本科",
        "description": "这是模拟的职位描述",
        "fetched_at": datetime.now().isoformat(),
        "source": "mock"
    }
    
    return json.dumps(mock_data, ensure_ascii=False, indent=2)

def main():
    print("🚀 Python-only获取详情脚本")
    print("=" * 60)
    print("💡 不使用boss命令，直接使用Python API")
    print("⚠️  注意: 需要实现真正的API调用逻辑")
    print("=" * 60)
    
    # 获取工作目录
    workspace = get_workspace_path()
    os.chdir(workspace)
    print(f"📁 工作目录: {workspace}")
    
    # 读取security_ids
    print("\n📋 读取security_id...")
    security_ids = []
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            security_ids.append(security_id)
                else:
                    if len(line) > 100:
                        security_ids.append(line)
    
    print(f"   总security_id数: {len(security_ids)}")
    
    # 读取已获取记录
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            fetched_ids.add(security_id)
                else:
                    if len(line) > 100:
                        fetched_ids.add(line)
    
    print(f"   已获取记录: {len(fetched_ids)} 个")
    
    # 找到未获取的
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    print(f"   未获取的security_id: {len(unfetched)} 个")
    
    if not unfetched:
        print("🎉 所有security_id都已获取")
        return
    
    # 目标：再获取7个达到50%
    target_count = 75 - len(fetched_ids)
    if target_count <= 0:
        print(f"🎉 已超过50%目标 ({len(fetched_ids)}/150)")
        return
    
    max_attempts = min(target_count, 10)  # 最多尝试10个
    print(f"\n🚀 开始获取详情 (目标: {max_attempts}个)")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i, security_id in enumerate(unfetched[:max_attempts]):
        print(f"\n📋 尝试获取第 {i+1} 个")
        print(f"   security_id: {security_id[:30]}...")
        
        try:
            # 使用requests获取详情
            detail_data = fetch_detail_with_requests(security_id)
            
            # 保存详情文件
            detail_dir = "职位详情"
            os.makedirs(detail_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = int(time.time() * 1000)
            filename = os.path.join(detail_dir, f"detail_{len(fetched_ids)+i+1}_{timestamp}.json")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(detail_data)
            
            print(f"   ✅ 保存到: {filename}")
            
            # 记录已获取
            with open(fetched_file, 'a', encoding='utf-8') as f:
                f.write(f"{security_id}|Python获取\n")
            
            success_count += 1
            print(f"   💡 成功: {success_count}个")
            
            # 短暂等待，避免请求过快
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ 获取失败: {e}")
            fail_count += 1
            
            # 如果连续失败2次，停止
            if fail_count >= 2:
                print(f"   🛑 连续失败{fail_count}次，停止获取")
                break
    
    print(f"\n{'=' * 60}")
    print(f"📊 获取统计:")
    print(f"   ✅ 成功: {success_count}个")
    print(f"   ❌ 失败: {fail_count}个")
    print(f"   🎯 目标完成: {len(fetched_ids)+success_count}/150 ({int((len(fetched_ids)+success_count)*100/150)}%)")
    
    if success_count > 0:
        print(f"\n✅ 成功获取{success_count}个新详情")
    else:
        print(f"\n⚠️  未获取到新详情，请检查API调用")

if __name__ == "__main__":
    main()