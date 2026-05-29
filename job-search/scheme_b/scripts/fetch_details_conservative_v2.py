#!/usr/bin/env python3
"""
方案B - 智能获取详情脚本 (保守策略 v2.3)
适用于技能架构,不硬编码工作目录
策略：获取失败就停止，立即进入汇总
"""

import subprocess
import json
import os
import time
import sys
from pathlib import Path

def get_workspace_path():
    """获取工作空间路径"""
    # 1. 优先使用环境变量
    workspace = os.environ.get('SCHEME_B_WORKSPACE')
    if workspace and os.path.exists(workspace):
        print(f"💡 使用环境变量指定目录: {workspace}")
        return workspace
    
    # 2. 新的默认路径：技能目录下的output文件夹
    skill_output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'output'
    )
    if os.path.exists(skill_output_path):
        print(f"💡 使用技能输出目录: {skill_output_path}")
        return skill_output_path

    # 3. 旧的默认路径（向后兼容）
    old_default_path = os.path.expanduser("~/招聘数据/方案B_立即执行_20260515_010114")
    if os.path.exists(old_default_path):
        print(f"💡 使用旧默认目录: {old_default_path}")
        return old_default_path

    # 4. 当前目录
    current_dir = os.getcwd()
    if os.path.exists(os.path.join(current_dir, 'all_security_ids_final.txt')):
        print(f"💡 使用当前目录: {current_dir}")
        return current_dir

    print("❌ 找不到工作目录")
    print("💡 建议设置:")
    print("   1. 环境变量: export SCHEME_B_WORKSPACE=\"/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output\"")
    print("   2. 或确保技能output目录存在")
    sys.exit(1)
def main():
    print("🚀 方案B - 智能获取详情脚本 (保守策略 v2.3)")
    print("=" * 60)
    print("💡 保守策略: 获取失败就停止，立即进入汇总")
    print("💡 停止条件: 连续失败2次或达到最大尝试次数")
    print("💡 目标: 最大化token利用，避免无效尝试")
    print("=" * 60)

    # 获取工作目录
    workspace = get_workspace_path()
    print(f"📁 工作目录: {workspace}")
    os.chdir(workspace)

    # 设置环境变量
    os.environ["PATH"] = f"/Users/xingan/Library/Python/3.12/bin:{os.environ.get('PATH', '')}"

    print("🔍 检查boss命令...")
    try:
        result = subprocess.run(['boss', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ boss命令可用: {result.stdout.strip()}")
        else:
            print(f"⚠️  boss命令返回非零状态: {result.stderr}")
    except FileNotFoundError:
        print("❌ boss命令未安装或不在PATH中")
        print("💡 请安装: pip install boss-zhipin")
        sys.exit(1)

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

    # 读取已获取记录
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 与security_ids读取逻辑保持一致：处理|分隔符
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            fetched_ids.add(security_id)
                else:
                    # 如果没有|分隔符，直接使用（但需要验证长度）
                    if len(line) > 100:
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

    # 获取当前最大编号
    max_num = 0
    detail_dir = '职位详情'
    if os.path.exists(detail_dir):
        for filename in os.listdir(detail_dir):
            if filename.startswith('detail_') and filename.endswith('.json'):
                try:
                    num = int(filename[7:-5])  # detail_xxx.json
                    if num > max_num:
                        max_num = num
                except:
                    pass

    start_num = max_num + 1  # 从最大编号+1开始

    # 保守策略: 获取失败就停止
    max_attempts = 10  # 最多尝试10次
    consecutive_failures = 0  # 连续失败计数
    max_consecutive_failures = 2  # 连续失败2次就停止
    success_count = 0
    failed_count = 0
    skipped_count = 0

    print(f"\n🚀 开始智能获取详情(保守策略 v2.3)...")
    print("=" * 60)
    print("💡 保守策略: 获取失败就停止，立即进入汇总")
    print("💡 token有效期:约3-5分钟，立即执行")
    print(f"💡 停止条件: 连续失败{max_consecutive_failures}次")
    print("=" * 60)

    # 检查停止条件
    should_stop = False

    for i, security_id in enumerate(unfetched[:max_attempts]):
        # 如果应该停止，则跳出循环
        if should_stop:
            print(f"🛑 达到停止条件，提前结束获取")
            break

        print(f"\n📋 尝试获取第 {i+1} 个(总第 {start_num + i} 个)")
        print(f"   security_id: {security_id[:30]}...")

        # 跳过已知有问题的第一个security_id
        if security_id.startswith('157gfiaER1wka'):
            print(f"   ⚠️  跳过已知有问题的security_id")
            skipped_count += 1
            continue

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
                        filename = f"职位详情/detail_{start_num + i}.json"

                        # 检查文件是否已存在
                        if os.path.exists(filename):
                            print(f'⚠️  文件命名冲突，跳过保存')
                            break

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
                        else:
                            print(f"   ⚠️  没有encryptId")

                        # 更新已获取记录
                        with open(fetched_file, 'a', encoding='utf-8') as f:
                            f.write(security_id + '\n')

                        success_count += 1
                        consecutive_failures = 0  # 成功时重置失败计数

                    else:
                        error_code = data.get('error', {}).get('code', '无')
                        error_msg = data.get('error', {}).get('message', '未知错误')
                        print(f"❌ 获取失败: code={error_code}, message={error_msg}")

                        # 检查是否是token问题
                        if error_code in [10001, 10002, 10003]:  # 常见的token错误码
                            print(f"💡 可能是token失效，建议重新登录")
                            should_stop = True
                        else:
                            print(f"💡 可能是无效的security_id")

                        failed_count += 1
                        consecutive_failures += 1

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
        if i < len(unfetched[:max_attempts]) - 1:
            time.sleep(1)

        # 检查停止条件：连续失败2次
        if consecutive_failures >= max_consecutive_failures:
            print(f"💡 连续失败{consecutive_failures}次，可能token已过期，停止获取")
            should_stop = True

        # 显示当前进度
        print(f"💡 进度: 已尝试{i+1}次，成功{success_count}个，失败{failed_count}个")

    print(f"\n{'=' * 60}")
    print(f"📊 获取统计:")
    print(f"   尝试获取: {min(max_attempts, len(unfetched))} 个")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {failed_count} 个")
    print(f"   ⚠️  跳过: {skipped_count} 个(已知问题)")

    if success_count > 0:
        print(f"\n🎉 成功获取 {success_count} 个新详情!")
        print(f"📁 文件保存到: {workspace}/职位详情/")
        print(f"📝 已更新记录: {fetched_file}")

        # 显示获取的职位
        print(f"\n📋 获取的职位:")
        for i in range(success_count):
            detail_num = start_num + i
            filename = f'职位详情/detail_{detail_num}.json'
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                job_info = data.get('data', {}).get('jobInfo', {})
                salary = job_info.get('salaryDesc', '薪资未知')
                name = job_info.get('jobName', '未知职位')
                print(f"   {i+1}. {name} - {salary}")
            except:
                print(f"   {i+1}. 文件读取失败: {filename}")

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
    print(f"💡 下次使用: python3 fetch_details_conservative_v2.py")

if __name__ == "__main__":
    main()