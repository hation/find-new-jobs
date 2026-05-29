#!/usr/bin/env python3
"""
获取详情 - 保守策略版本
策略：获取失败就停止，立即进入汇总步骤
"""

import subprocess
import json
import os
import time
from datetime import datetime

def main():
    print("🚀 BOSS直聘详情获取 - 保守策略")
    print("=" * 60)
    print("💡 保守策略: 获取失败就停止，立即进入汇总")
    print("💡 目标: 最大化利用token，避免无效尝试")
    print("💡 停止条件: 连续失败2次或总尝试10次")
    print("=" * 60)
    
    # 工作空间路径
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 读取所有security_id
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
    
    print(f"📋 总security_id数: {len(security_ids)}")
    
    # 读取已获取记录
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    fetched_ids.add(line)
        
        print(f"   已获取记录: {len(fetched_ids)} 个")
    else:
        print("   没有已获取记录文件,将创建新文件")

    # 找到未获取的
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    print(f"   未获取的security_id: {len(unfetched)} 个")
    
    if not unfetched:
        print("🎉 所有security_id都已获取")
        return
    
    # 创建职位详情目录
    os.makedirs('职位详情', exist_ok=True)
    
    # 保守策略参数
    max_attempts = 10  # 最多尝试10次
    max_consecutive_failures = 2  # 连续失败2次就停止
    success_count = 0
    failed_count = 0
    consecutive_failures = 0
    total_attempts = 0
    
    print(f"\n🎯 保守策略开始执行...")
    print(f"   最多尝试: {max_attempts} 次")
    print(f"   停止条件: 连续失败 {max_consecutive_failures} 次")
    
    # 开始获取
    for i, security_id in enumerate(unfetched[:max_attempts]):
        total_attempts = i + 1
        
        # 检查停止条件
        if consecutive_failures >= max_consecutive_failures:
            print(f"\n🛑 达到停止条件: 连续失败 {consecutive_failures} 次")
            print(f"💡 建议重新登录获取新token")
            break
        
        print(f"\n📋 尝试获取第 {i+1} 个(总第 {len(fetched_ids)+i+1} 个)")
        print(f"   security_id: {security_id[:30]}...")
        
        try:
            # 执行boss detail命令
            print(f"   执行命令: boss detail ...")
            result = subprocess.run(
                ['boss', 'detail', security_id],
                capture_output=True,
                text=True,
                timeout=15  # 15秒超时
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    
                    # 检查返回的数据结构
                    if data and 'data' in data and data['data']:
                        job_data = data['data']
                        job_info = job_data.get('jobInfo', {})
                        boss_info = job_data.get('bossInfo', {})
                        
                        job_name = job_info.get('jobName', '未知职位')
                        salary_desc = job_info.get('salaryDesc', '薪资未知')
                        
                        # 生成文件名
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"职位详情/detail_{len(fetched_ids)+i+1}.json"
                        
                        # 检查文件是否已存在
                        if os.path.exists(filename):
                            print(f"⚠️  文件已存在，跳过保存")
                        else:
                            with open(filename, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            
                            print(f"✅ 获取成功!")
                            print(f"   职位: {job_name}")
                            print(f"   薪资: {salary_desc}")
                            print(f"   保存为: {filename}")
                            
                            # 检查是否有encryptId
                            encrypt_id = job_info.get('encryptId', '')
                            if encrypt_id:
                                print(f"   encryptId: {encrypt_id[:20]}...")
                            
                            # 更新已获取记录
                            with open(fetched_file, 'a', encoding='utf-8') as f:
                                f.write(security_id + '\n')
                            
                            success_count += 1
                            consecutive_failures = 0  # 成功时重置失败计数
                            
                            # 成功获取后继续下一个
                            continue
                    else:
                        error_code = data.get('error', {}).get('code', '无')
                        error_msg = data.get('error', {}).get('message', '未知错误')
                        print(f"❌ API返回错误: code={error_code}, message={error_msg}")
                        
                        failed_count += 1
                        consecutive_failures += 1
                        
                        # 检查是否是token问题
                        if error_code in [10001, 10002, 10003]:  # 常见的token错误码
                            print(f"💡 可能是token失效，建议重新登录")
                            break
                        
                except json.JSONDecodeError:
                    print(f"❌ 返回的不是有效JSON")
                    print(f"   输出前100字符: {result.stdout[:100]}")
                    failed_count += 1
                    consecutive_failures += 1
            else:
                print(f"❌ 命令执行失败")
                print(f"   错误输出: {result.stderr[:100]}")
                failed_count += 1
                consecutive_failures += 1
        
        except subprocess.TimeoutExpired:
            print("❌ 请求超时 (15秒)")
            failed_count += 1
            consecutive_failures += 1
        except Exception as e:
            print(f"❌ 其他错误: {e}")
            failed_count += 1
            consecutive_failures += 1
        
        # 每个请求间隔1秒
        time.sleep(1)
    
    # 统计结果
    print(f"\n============================================================")
    print(f"📊 获取统计:")
    print(f"   尝试获取: {total_attempts} 个")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {failed_count} 个")
    print(f"   停止原因: {'连续失败' if consecutive_failures >= max_consecutive_failures else '达到最大尝试次数'}")
    
    if success_count > 0:
        print(f"\n🎉 成功获取 {success_count} 个新详情!")
        print(f"📁 文件保存到: {workspace}/职位详情/")
        print(f"📝 已更新记录: {fetched_file}")
        
        # 统计当前详情文件总数
        detail_files = [f for f in os.listdir('职位详情') if f.startswith('detail_') and f.endswith('.json')]
        print(f"📁 当前详情文件总数: {len(detail_files)} 个")
        
        # 计算预计数据完整性
        total_jobs = 150
        estimated_complete = len(detail_files)
        completeness_rate = estimated_complete / total_jobs * 100
        
        print(f"\n📈 预计数据完整性:")
        print(f"   当前完整详情: {estimated_complete}/{total_jobs} ({completeness_rate:.1f}%)")
        
        # 推荐下一步
        print(f"\n🚀 推荐下一步:")
        print(f"   1. 立即合并数据:")
        print(f"      cd {workspace}")
        print(f"      python3 final_fix_excel.py")
        print(f"   2. 验证数据质量:")
        print(f"      python3 -c \"import pandas as pd; df = pd.read_excel('深圳_ai.xlsx'); print(f'完整数据: {{(df[\\\"数据完整性\\\"] == \\\"完整\\\").sum()}}/{{len(df)}}')\"")
        
        if consecutive_failures >= max_consecutive_failures:
            print(f"\n💡 需要重新登录获取新token")
    else:
        print(f"\n❌ 本次获取失败，可能原因:")
        print(f"   1. token已过期 (需要重新登录)")
        print(f"   2. 网络连接问题")
        print(f"   3. security_id无效")
        print(f"\n💡 建议步骤:")
        print(f"   1. 重新登录BOSS直聘")
        print(f"   2. 再次运行本脚本")
        print(f"   3. 如果仍然失败，检查网络连接")
    
    print(f"\n✅ 脚本执行完成")
    print(f"💡 下次使用: python3 fetch_details_conservative.py")

if __name__ == "__main__":
    main()