#!/usr/bin/env python3
"""
测试获取详情 - 简化版本
直接测试第一个未获取的security_id
"""

import subprocess
import json
import os
import time

def main():
    print("🔍 测试获取详情 - 简化版本")
    print("=" * 60)
    print("💡 直接测试第一个未获取的security_id")
    print("💡 使用绝对路径boss命令")
    print("=" * 60)
    
    # 工作空间路径
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 设置PATH
    os.environ["PATH"] = f"/Users/xingan/Library/Python/3.12/bin:{os.environ.get('PATH', '')}"
    
    # 读取所有security_id
    print(f"\n📋 读取security_id...")
    security_ids = []
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 处理格式: security_id|职位名称|页码
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            security_ids.append(security_id)
                else:
                    # 如果没有|分隔符，直接使用
                    if len(line) > 100:
                        security_ids.append(line)
    
    print(f"   总security_id数: {len(security_ids)}")
    if security_ids:
        print(f"   第一个security_id: {security_ids[0][:30]}...")
        print(f"   完整长度: {len(security_ids[0])} 字符")
    
    # 读取已获取记录
    print(f"\n📝 读取已获取记录...")
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    fetched_ids.add(line)
        
        print(f"   已获取记录（去重后）: {len(fetched_ids)} 个")
        if fetched_ids:
            first_fetched = list(fetched_ids)[0]
            print(f"   第一个已获取: {first_fetched[:30]}...")
    else:
        print(f"   没有已获取记录文件")
    
    # 找到未获取的
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    print(f"\n📋 未获取的security_id: {len(unfetched)} 个")
    
    if not unfetched:
        print("🎉 所有security_id都已获取")
        return
    
    # 测试第一个未获取的
    test_id = unfetched[0]
    print(f"\n🚀 测试获取第一个未获取的security_id:")
    print(f"   security_id: {test_id[:30]}...")
    print(f"   完整长度: {len(test_id)} 字符")
    
    # 检查是否包含特殊字符
    if '|' in test_id:
        print(f"   ⚠️  security_id中包含|符号，需要清理")
        test_id = test_id.split('|')[0].strip()
        print(f"   清理后: {test_id[:30]}...")
    
    # 测试boss命令
    print(f"\n🔧 测试boss命令...")
    try:
        # 先测试boss --version
        print(f"   1. 测试boss --version...")
        version_result = subprocess.run(
            ['boss', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if version_result.returncode == 0:
            print(f"   ✅ boss命令正常: {version_result.stdout.strip()}")
        else:
            print(f"   ❌ boss命令失败: {version_result.stderr}")
            return
        
        # 测试获取详情
        print(f"\n   2. 测试获取详情...")
        print(f"      执行: boss detail {test_id[:30]}...")
        
        start_time = time.time()
        detail_result = subprocess.run(
            ['boss', 'detail', test_id],
            capture_output=True,
            text=True,
            timeout=15
        )
        elapsed_time = time.time() - start_time
        
        print(f"      耗时: {elapsed_time:.2f} 秒")
        print(f"      返回码: {detail_result.returncode}")
        
        if detail_result.returncode == 0:
            print(f"\n📊 响应统计:")
            print(f"      输出长度: {len(detail_result.stdout)} 字符")
            print(f"      错误长度: {len(detail_result.stderr)} 字符")
            
            if len(detail_result.stdout) < 100:
                print(f"\n⚠️  输出太短，可能有问题:")
                print(f"      输出: {detail_result.stdout}")
            else:
                try:
                    data = json.loads(detail_result.stdout)
                    print(f"\n✅ JSON解析成功!")
                    
                    if 'data' in data and data['data']:
                        job_info = data['data'].get('jobInfo', {})
                        boss_info = data['data'].get('bossInfo', {})
                        
                        print(f"      📋 职位信息:")
                        print(f"          名称: {job_info.get('jobName', '未知')}")
                        print(f"          薪资: {job_info.get('salaryDesc', '未知')}")
                        print(f"          encryptId: {job_info.get('encryptId', '未知')[:20]}...")
                        
                        print(f"      👤 联系人信息:")
                        print(f"          姓名: {boss_info.get('name', '未知')}")
                        print(f"          职位: {boss_info.get('title', '未知')}")
                        
                        print(f"\n🎉 测试成功! 可以获取详情数据")
                        print(f"💡 建议: 运行完整获取脚本")
                        
                    elif 'error' in data:
                        error = data['error']
                        print(f"\n❌ API返回错误:")
                        print(f"      代码: {error.get('code', '未知')}")
                        print(f"      信息: {error.get('message', '未知')}")
                        
                        if error.get('code') in [10001, 10002, 10003]:
                            print(f"💡 可能是token已过期，需要重新登录")
                        else:
                            print(f"💡 可能是security_id无效")
                    else:
                        print(f"\n⚠️  API返回无数据")
                        print(f"      完整响应: {detail_result.stdout[:200]}...")
                        
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON解析失败: {e}")
                    print(f"      输出前200字符: {detail_result.stdout[:200]}")
                    
                    # 检查是否是YAML格式（data:开头）
                    if detail_result.stdout.startswith('data:'):
                        print(f"💡 发现YAML格式输出，可能是token问题")
                        print(f"💡 需要重新登录BOSS直聘")
        else:
            print(f"\n❌ 命令执行失败")
            if detail_result.stderr:
                print(f"      错误输出: {detail_result.stderr[:200]}")
            else:
                print(f"      无错误输出")
                print(f"      完整输出: {detail_result.stdout[:200]}")
                
    except subprocess.TimeoutExpired:
        print(f"\n⏰ 命令超时 (15秒)")
    except FileNotFoundError:
        print(f"\n❌ boss命令未找到")
        print(f"💡 请检查PATH设置")
    except Exception as e:
        print(f"\n❌ 其他错误: {e}")
    
    print(f"\n✅ 测试完成")
    print(f"💡 根据测试结果决定下一步操作")

if __name__ == "__main__":
    main()