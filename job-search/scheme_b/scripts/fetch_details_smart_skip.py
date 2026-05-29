#!/usr/bin/env python3
"""
方案B - 智能获取详情脚本（优化连续版）

优化策略：
1. 在token有效期内连续获取，直到连续失败才停止
2. 从中间位置开始，跳过更多可能失效的ID
3. 移除尝试次数限制，最大化token利用率
4. 成功时重置失败计数，继续获取

核心原则：
- 数据格式适应性 ✅
- 数据清洗前置 ✅
- 错误诊断分层 ✅
- 环境配置显式化 ✅
- 字段映射验证 ✅
- 保守执行策略（优化版） ✅
"""

import subprocess
import json
import os
import time
import sys
from pathlib import Path

# 尝试导入yaml模块
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  yaml模块未安装，将尝试安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        import yaml
        YAML_AVAILABLE = True
        print("✅ yaml模块安装成功")
    except:
        print("❌ 无法安装yaml模块，部分功能可能受限")

def parse_response(response_text):
    """原则1: 数据格式适应性 - 支持JSON和YAML格式"""
    # 首先尝试JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # 如果YAML模块可用，尝试YAML
        if YAML_AVAILABLE:
            try:
                return yaml.safe_load(response_text)
            except yaml.YAMLError:
                pass
        
        # 如果都失败，尝试简单的YAML解析（基础情况）
        if 'data:' in response_text and 'error:' in response_text:
            # 简单解析YAML格式
            lines = response_text.strip().split('\n')
            data = {}
            current_key = None
            current_value = []
            
            for line in lines:
                line = line.strip()
                if line.endswith(':'):
                    if current_key:
                        # 保存上一个键的值
                        if current_value:
                            data[current_key] = '\n'.join(current_value).strip()
                        current_value = []
                    current_key = line[:-1].strip()
                elif current_key and line:
                    current_value.append(line)
            
            if current_key and current_value:
                data[current_key] = '\n'.join(current_value).strip()
            
            return data
        
        # 返回空数据
        return {}

def clean_security_id(security_id_str):
    """原则2: 数据清洗前置 - 清理security_id格式"""
    if '|' in security_id_str:
        return security_id_str.split('|')[0].strip()
    return security_id_str.strip()

def diagnose_error(error_data):
    """原则3: 错误诊断分层 - 分层诊断错误"""
    error_code = error_data.get('code', '')
    error_msg = error_data.get('message', '')
    
    # 第一层：认证错误（根本错误）
    if error_code == 'not_authenticated':
        return {
            'level': 'critical',
            'type': 'authentication',
            'message': f'Token已过期: {error_msg}',
            'action': '重新登录: boss logout && boss login',
            'should_stop': True
        }
    
    # 第二层：数据错误（表面错误）
    elif error_code == 200301:
        return {
            'level': 'warning',
            'type': 'data_invalid',
            'message': f'职位不存在: {error_msg}',
            'action': '跳过此security_id，继续下一个',
            'should_stop': False
        }
    
    # 第三层：语法错误（security_id格式问题）
    elif 'No such option' in str(error_data) or 'Usage:' in str(error_data):
        return {
            'level': 'warning',
            'type': 'syntax_error',
            'message': f'security_id格式错误或命令语法错误',
            'action': '跳过此security_id，检查格式',
            'should_stop': False
        }
    
    # 第三层：其他错误
    else:
        return {
            'level': 'error',
            'type': 'unknown',
            'message': f'未知错误: {error_code} - {error_msg}',
            'action': '检查网络连接或security_id有效性',
            'should_stop': False
        }

def setup_environment():
    """原则4: 环境配置显式化 - 显式设置环境"""
    # 获取工作目录
    workspace = os.environ.get('SCHEME_B_WORKSPACE')
    if not workspace or not os.path.exists(workspace):
        # 默认路径
        default_path = os.path.expanduser("~/招聘数据/方案B_立即执行_20260515_010114")
        if os.path.exists(default_path):
            workspace = default_path
        else:
            print("❌ 找不到工作目录,请设置 SCHEME_B_WORKSPACE 环境变量")
            print("💡 例如: export SCHEME_B_WORKSPACE=\"/Users/xingan/招聘数据/方案B_立即执行_20260515_010114\"")
            sys.exit(1)
    
    # 设置工作目录
    os.chdir(workspace)
    
    # 设置PATH
    python_bin = "/Users/xingan/Library/Python/3.12/bin"
    os.environ["PATH"] = f"{python_bin}:{os.environ.get('PATH', '')}"
    
    return workspace

def check_dependencies():
    """检查必要的工具和文件"""
    # 检查boss命令
    try:
        result = subprocess.run(['boss', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ boss命令可用: {result.stdout.strip()}")
        else:
            print(f"⚠️  boss命令返回非零状态: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ boss命令未安装或不在PATH中")
        print("💡 请安装: pip install boss-zhipin")
        return False
    
    # 检查必要文件
    required_files = ['all_security_ids_final.txt', 'fetched_security_ids.txt']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 必要文件不存在: {file}")
            return False
    
    return True

def read_and_clean_security_ids():
    """读取并清理security_id"""
    # 读取所有security_id
    security_ids = []
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                security_ids.append(clean_security_id(line))
    
    # 读取已获取记录
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    fetched_ids.add(clean_security_id(line))
    
    # 找到未获取的
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    
    return security_ids, fetched_ids, unfetched

def main():
    print("🚀 方案B - 智能获取详情脚本（智能跳过版）")
    print("=" * 60)
    print("💡 应用六大核心原则:")
    print("   1. 数据格式适应性 ✅")
    print("   2. 数据清洗前置 ✅")
    print("   3. 错误诊断分层 ✅")
    print("   4. 环境配置显式化 ✅")
    print("   5. 字段映射验证 ✅")
    print("   6. 保守执行策略 ✅")
    print("=" * 60)

    # 原则4: 环境配置显式化
    workspace = setup_environment()
    print(f"📁 工作目录: {workspace}")

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 原则2: 数据清洗前置
    security_ids, fetched_ids, unfetched = read_and_clean_security_ids()
    
    print(f"\n📋 数据统计:")
    print(f"   总security_id数: {len(security_ids)}")
    print(f"   已获取记录: {len(fetched_ids)} 个")
    print(f"   未获取的: {len(unfetched)} 个")

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

    # 原则6: 保守执行策略 - 优化为连续获取直到失败
    max_consecutive_failures = 3  # 连续失败3次就停止（更宽松）
    consecutive_failures = 0  # 连续失败计数
    success_count = 0
    failed_count = 0
    skipped_count = 0
    should_stop = False
    
    # 新增：从中间位置开始，跳过更多可能失效的ID
    skip_more_count = 10  # 如果前几个失败，跳过更多
    start_from_middle = True  # 是否从中间开始

    print(f"\n🚀 开始智能获取详情（智能跳过版）...")
    print("=" * 60)
    print("💡 智能跳过: 自动跳过前几个可能无效的security_id")
    print("💡 token有效期:约3-5分钟，立即执行")
    print(f"💡 停止条件: 连续失败{max_consecutive_failures}次")
    print("=" * 60)

    # 跳过前几个可能无效的security_id
    skip_count = 0
    skip_threshold = 3  # 跳过前3个
    
    # 优化：如果从中间开始，跳过更多
    if start_from_middle and len(unfetched) > 20:
        skip_threshold = 10  # 跳过前10个
        print(f"💡 从中间开始策略: 跳过前{skip_threshold}个可能失效的ID")

    # 优化：连续获取直到失败，移除尝试次数限制
    print(f"💡 新策略: 连续获取直到连续失败{max_consecutive_failures}次")
    print(f"💡 token有效期内尽可能多地获取")
    
    for i, security_id in enumerate(unfetched):
        # 如果应该停止，则跳出循环
        if should_stop:
            print(f"🛑 达到停止条件，提前结束获取")
            break

        # 跳过前几个
        if i < skip_threshold:
            print(f"\n📋 跳过第 {i+1} 个(总第 {start_num + i} 个)")
            print(f"   security_id: {security_id[:30]}...")
            print(f"   💡 智能跳过: 前{skip_threshold}个可能已失效")
            skipped_count += 1
            skip_count += 1
            continue

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
                # 原则1: 数据格式适应性
                data = parse_response(result.stdout)

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

                    # 保存原始响应（保持YAML格式）
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)

                    print(f"✅ 获取成功!")
                    print(f"   职位: {job_name}")
                    print(f"   薪资: {salary_desc}")
                    print(f"   保存为: {filename}")

                    # 原则5: 字段映射验证
                    encrypt_id = job_info.get('encryptId', '')
                    if encrypt_id:
                        print(f"   encryptId: {encrypt_id[:20]}...")
                        
                        # 验证字段名
                        if 'postDescription' in job_info:
                            print(f"   ✅ 字段映射正确: postDescription → 职位描述")
                        else:
                            print(f"   ⚠️  未找到postDescription字段")
                    else:
                        print(f"   ⚠️  没有encryptId")

                    # 更新已获取记录
                    with open('fetched_security_ids.txt', 'a', encoding='utf-8') as f:
                        f.write(security_id + '\n')

                    success_count += 1
                    consecutive_failures = 0  # 成功时重置失败计数

                else:
                    # 原则3: 错误诊断分层
                    if 'error' in data:
                        error_diagnosis = diagnose_error(data['error'])
                        print(f"❌ {error_diagnosis['message']}")
                        print(f"💡 {error_diagnosis['action']}")
                        
                        if error_diagnosis['should_stop']:
                            should_stop = True
                    else:
                        print(f"❌ 获取失败: 响应数据格式不正确")
                        print(f"   响应前100字符: {result.stdout[:100]}")

                    failed_count += 1
                    consecutive_failures += 1

            else:
                print(f"❌ 命令执行失败")
                if result.stderr:
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

        # 每个请求间隔1秒（除非已经停止）
        if not should_stop:
            time.sleep(1)

        # 检查停止条件：连续失败达到阈值
        if consecutive_failures >= max_consecutive_failures:
            print(f"💡 连续失败{consecutive_failures}次，达到停止条件，停止获取")
            should_stop = True

        # 显示当前进度
        print(f"💡 进度: 已尝试{i+1}次，成功{success_count}个，失败{failed_count}个，跳过{skipped_count}个")
        
        # 如果已经停止，跳出循环
        if should_stop:
            break

    print(f"\n{'=' * 60}")
    print(f"📊 获取统计:")
    print(f"   尝试获取: {success_count + failed_count + skipped_count} 个")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {failed_count} 个")
    print(f"   ⚠️  跳过: {skipped_count} 个（智能跳过{skip_count}个 + 已知问题{skipped_count-skip_count}个）")

    if success_count > 0:
        print(f"\n🎉 成功获取 {success_count} 个新详情!")
        print(f"📁 文件保存到: {workspace}/职位详情/")
        print(f"📝 已更新记录: {workspace}/fetched_security_ids.txt")

        # 显示获取的职位
        print(f"\n📋 获取的职位:")
        for i in range(success_count):
            detail_num = start_num + i + skip_count  # 考虑跳过的数量
            filename = f'职位详情/detail_{detail_num}.json'
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                data = parse_response(content)
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
        print(f"      运行: python3 verify_excel_data.py")
    else:
        print(f"\n❌ 本次获取失败，可能原因:")
        print(f"   1. token可能已过期 (需要重新登录)")
        print(f"   2. 前几个security_id已失效，但已智能跳过")
        print(f"   3. 网络连接问题")
        print(f"   4. security_id无效")
        print(f"\n💡 建议步骤:")
        print(f"   1. 重新登录BOSS直聘")
        print(f"   2. 再次运行本脚本（会智能跳过无效ID）")
        print(f"   3. 如果仍然失败，检查网络连接")

    print(f"\n✅ 脚本执行完成")
    print(f"💡 下次使用: python3 fetch_details_smart_skip.py")
    print(f"💡 核心原则应用总结:")
    print(f"   - ✅ 数据格式适应性: 支持JSON/YAML")
    print(f"   - ✅ 数据清洗前置: 清理security_id格式")
    print(f"   - ✅ 错误诊断分层: 区分表面/根本错误")
    print(f"   - ✅ 环境配置显式化: PATH和工作目录")
    print(f"   - ✅ 字段映射验证: 验证postDescription字段")
    print(f"   - ✅ 保守执行策略: 智能跳过+失败停止")

if __name__ == "__main__":
    main()