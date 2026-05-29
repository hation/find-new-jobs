#!/usr/bin/env python3
"""
方案B - 智能获取详情脚本 (通用版本)
适用于技能架构,不硬编码工作目录
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
    print("🚀 方案B - 智能获取详情脚本")
    print("=" * 60)
    print("💡 通用版本,适用于技能架构")
    print("=" * 60)

    # 获取工作目录
    workspace = get_workspace_path()
    print(f"📁 工作目录: {workspace}")
    os.chdir(workspace)

    # 设置环境变量
    os.environ["PATH"] = f"/Users/xingan/Library/Python/3.12/bin:{os.environ.get('PATH', '')}"

    print("🔍 检查boss命令...")
    try:
        result = subprocess.run(['which', 'boss'], capture_output=True, text=True)
        boss_path = result.stdout.strip()
        if boss_path:
            print(f"✅ boss命令: {boss_path}")
        else:
            print("❌ boss命令不在PATH中")
            print("💡 请确保已安装boss-cli: pip install boss-cli")
            return
    except:
        print("⚠️  无法检查boss命令,继续尝试...")

    print("\n📋 读取security_id列表...")
    security_file = 'all_security_ids_final.txt'
    if not os.path.exists(security_file):
        print(f"❌ 找不到 {security_file}")
        print("💡 请确保工作目录包含必要的文件")
        return

    with open(security_file, 'r', encoding='utf-8') as f:
        security_ids = []
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # 跳过注释和空行
            
            parts = line.split('|')
            if len(parts) >= 1 and parts[0].strip():
                security_id = parts[0].strip()
                # 验证security_id格式
                if len(security_id) > 100 and ('-' in security_id or '_' in security_id):
                    security_ids.append(security_id)
                else:
                    print(f"⚠️  跳过无效security_id: {security_id[:30]}...")

    print(f"   总security_id数: {len(security_ids)}")
    if security_ids:
        print(f"   示例security_id: {security_ids[0][:30]}...")

    # 读取已获取记录
    fetched_ids = set()
    fetched_file = 'fetched_security_ids.txt'
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue  # 跳过空行和注释行
                
                # 处理格式: securityId|职位名称|页码|时间
                if '|' in line:
                    # 提取securityId（第一个字段）
                    security_id = line.split('|')[0].strip()
                    if security_id:
                        fetched_ids.add(security_id)
                else:
                    # 如果没有|，整行就是securityId
                    fetched_ids.add(line)
        
        print(f"   已获取记录: {len(fetched_ids)} 个（清理后）")
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

    print("\n🚀 开始智能获取详情(激进策略)...")
    print("=" * 60)
    print("💡 激进策略:获取2个未重复详情,尝试第3个")
    print("💡 token有效期:约3-5分钟,必须立即执行")
    print("=" * 60)

    success_count = 0
    failed_count = 0
    skipped_count = 0

    # 获取当前最大文件编号
    existing_files = [f for f in os.listdir('职位详情') if f.startswith('detail_') and f.endswith('.json')]
    
    # 找到最大编号
    max_num = 0
    for f in existing_files:
        try:
            # 从文件名提取数字，如 detail_21.json -> 21
            num = int(f.split('_')[1].split('.')[0])
            if num > max_num:
                max_num = num
        except:
            pass
    
    start_num = max_num + 1  # 从最大编号+1开始

    # 尝试获取多个,跳过有问题的
    max_attempts = 10  # 增加尝试次数
    consecutive_failures = 0  # 连续失败计数
    max_consecutive_failures = 2  # 最多连续失败2次就停止

    for i, security_id in enumerate(unfetched[:max_attempts]):
        print(f"\n📋 尝试获取第 {i+1} 个(总第 {start_num + i} 个)")
        print(f"   security_id: {security_id[:30]}...")

        # 跳过已知有问题的第一个security_id
        if security_id.startswith('157gfiaER1wka'):
            print(f"   ⚠️  跳过已知有问题的security_id")
            skipped_count += 1
            continue

        try:
            # 运行boss detail命令
            cmd = ['boss', 'detail', security_id, '--json']
            print(f"   执行命令: boss detail ...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15  # 15秒超时
            )

            print(f"   返回码: {result.returncode}")

            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)

                    if data.get('ok') is True and 'data' in data and data['data']:
                        # 获取职位信息
                        job_info = data['data'].get('jobInfo', {})
                        job_name = job_info.get('jobName', '未知职位')
                        salary_desc = job_info.get('salaryDesc', '面议')

                        # 保存详情文件，使用递增编号
                        detail_num = start_num + success_count
                        filename = f'职位详情/detail_{detail_num}.json'
                        
                        # 确保文件不会覆盖
                        counter = 0
                        while os.path.exists(filename):
                            counter += 1
                            detail_num = start_num + success_count + counter
                            filename = f'职位详情/detail_{detail_num}.json'
                            if counter > 10:
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

                        # 如果已经成功2个,尝试第3个后停止
                        if success_count >= 2 and i >= 2:
                            print(f"💡 已成功获取{success_count}个,继续尝试第3个...")
                    else:
                        error_code = data.get('error', {}).get('code', '无')
                        error_msg = data.get('error', {}).get('message', '未知错误')
                        print(f"❌ 获取失败: code={error_code}, message={error_msg}")

                        # 如果是前2个失败,可能是token问题
                        if i < 2 and success_count == 0:
                            print("💡 前2个就失败,可能需要重新登录")
                            failed_count += 1
                            break
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
        
        # 激进策略：成功时重置失败计数，连续失败时停止
        if success_count > 0:
            consecutive_failures = 0  # 成功时重置失败计数
        
        # 停止条件：连续失败2次，或者达到最大尝试次数
        if consecutive_failures >= max_consecutive_failures:
            print(f"💡 连续失败{consecutive_failures}次，可能token已过期，停止获取")
            break
        
        # 如果已经成功获取，显示进度
        if success_count > 0 and (i + 1) % 3 == 0:
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
                job_name = job_info.get('jobName', '未知职位')
                salary_desc = job_info.get('salaryDesc', '面议')
                print(f"   {i+1}. {job_name} - {salary_desc}")
            except:
                print(f"   {i+1}. 详情文件 {detail_num}")

        print(f"\n🚀 接下来可以合并Excel文件:")
        print(f"   python3 {os.path.dirname(__file__)}/scheme_b_excel_correct_merge.py")

        # 检查当前详情文件总数
        detail_files = [f for f in os.listdir('职位详情') if f.startswith('detail_') and f.endswith('.json')]
        print(f"\n📁 当前详情文件总数: {len(detail_files)} 个")

        # 计算预计数据完整性
        excel_files = [f for f in os.listdir('.') if f.startswith('深圳AI岗位_') and f.endswith('.xlsx')]
        if excel_files:
            import pandas as pd
            latest_excel = sorted(excel_files)[-1]
            try:
                df = pd.read_excel(latest_excel)
                total_jobs = len(df)
                if '数据完整性' in df.columns:
                    complete_jobs = (df['数据完整性'] == '完整').sum()
                    new_complete = complete_jobs + success_count
                    new_ratio = new_complete / total_jobs * 100

                    print(f"\n📈 预计数据完整性:")
                    print(f"   当前完整: {complete_jobs}/{total_jobs} ({complete_jobs/total_jobs*100:.1f}%)")
                    print(f"   新增后: {new_complete}/{total_jobs} ({new_ratio:.1f}%)")
            except:
                print(f"\n📊 Excel文件: {latest_excel}")
    else:
        print(f"\n⚠️  本次没有成功获取详情")
        print(f"💡 可能原因:")
        print(f"   1. token已过期")
        print(f"   2. 需要重新登录")
        print(f"   3. 网络问题")
        print(f"\n💡 建议:")
        print(f"   1. 重新登录BOSS直聘")
        print(f"   2. 重新运行此脚本")

    print(f"\n✅ 脚本执行完成")
    print(f"💡 下次使用: python3 {os.path.basename(__file__)}")

if __name__ == "__main__":
    main()