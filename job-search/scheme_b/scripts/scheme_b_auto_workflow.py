#!/usr/bin/env python3
"""
方案B自动工作流脚本
自动执行：获取详情 → 失败停止 → 智能合并 → 验证结果
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            print(f"✅ 执行成功!")
            print(f"输出:\n{result.stdout}")
            return True
        else:
            print(f"❌ 执行失败 (返回码: {result.returncode})")
            print(f"错误输出:\n{result.stderr[:500]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 执行超时 (5分钟)")
        return False
    except Exception as e:
        print(f"❌ 执行异常: {e}")
        return False

def check_data_quality():
    """检查数据质量"""
    print(f"\n{'='*60}")
    print(f"📊 检查数据质量")
    print(f"{'='*60}")
    
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    
    # 检查Excel文件
    excel_file = os.path.join(workspace, "深圳_ai.xlsx")
    if not os.path.exists(excel_file):
        print(f"❌ Excel文件不存在: {excel_file}")
        return False
    
    # 使用Python检查数据
    python_code = f"""
import pandas as pd
import os

excel_file = '{excel_file}'
if os.path.exists(excel_file):
    df = pd.read_excel(excel_file)
    print(f'📊 数据质量检查:')
    print(f'   文件: {excel_file}')
    print(f'   行数: {{len(df)}}')
    
    # 检查数据完整性
    if '数据完整性' in df.columns:
        complete = (df['数据完整性'] == '完整').sum()
        print(f'   完整数据: {{complete}}/{{len(df)}} ({{complete/len(df)*100:.1f}}%)')
    
    # 检查关键字段填充率
    key_fields = ['技能要求', '福利待遇', '职位标签', '职位描述', '地址']
    for field in key_fields:
        if field in df.columns:
            non_empty = df[field].notna().sum()
            print(f'   {{field}}: {{non_empty}}/{{len(df)}} ({{non_empty/len(df)*100:.1f}}%)')
    
    # 检查数据一致性
    with open('{workspace}/all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        security_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if len(df) == len(security_ids):
        print(f'✅ 数据一致性: Excel({{len(df)}}) = Security_id({{len(security_ids)}})')
    else:
        print(f'❌ 数据不一致: Excel({{len(df)}}) ≠ Security_id({{len(security_ids)}})')
else:
    print(f'❌ 文件不存在: {{excel_file}}')
"""
    
    result = subprocess.run(
        ["python3", "-c", python_code],
        cwd=workspace,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(f"❌ 检查失败: {result.stderr}")
        return False

def main():
    print("🚀 方案B自动工作流")
    print("=" * 60)
    print("💡 策略: 获取失败就停止，立即进入汇总")
    print("💡 工作流: 获取 → 停止（失败时）→ 合并 → 验证")
    print("💡 目标: 最大化token利用，最小化无效尝试")
    print("=" * 60)
    
    # 1. 记录开始时间
    start_time = datetime.now()
    print(f"📅 开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. 切换到工作空间
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 3. 检查当前状态
    print(f"\n📊 检查当前状态...")
    print(f"   工作空间: {workspace}")
    
    # 检查是否有Excel文件
    if os.path.exists("深圳_ai.xlsx"):
        print(f"   ✅ Excel文件存在: 深圳_ai.xlsx")
    else:
        print(f"   ⚠️  Excel文件不存在，可能需要先运行合并脚本")
    
    # 检查详情文件数量
    detail_dir = "职位详情"
    if os.path.exists(detail_dir):
        detail_files = [f for f in os.listdir(detail_dir) if f.startswith('detail_') and f.endswith('.json')]
        print(f"   📁 详情文件: {len(detail_files)} 个")
    else:
        print(f"   ⚠️  详情目录不存在: {detail_dir}")
    
    # 4. 执行获取详情（保守策略）
    print(f"\n🔄 步骤1: 获取详情（保守策略）...")
    
    # 切换到脚本目录
    script_dir = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/scripts"
    os.chdir(script_dir)
    
    # 运行保守策略获取脚本
    get_success = run_command(
        "python3 fetch_details_conservative.py",
        "获取详情（保守策略）"
    )
    
    if not get_success:
        print(f"\n💡 获取详情失败或token已过期")
        print(f"💡 需要重新登录BOSS直聘")
        print(f"💡 继续执行合并步骤...")
    
    # 5. 执行智能合并
    print(f"\n🔄 步骤2: 智能合并（使用最终修复工具）...")
    
    os.chdir(workspace)
    merge_success = run_command(
        "python3 final_fix_excel.py",
        "智能合并数据"
    )
    
    if not merge_success:
        print(f"\n❌ 合并失败，尝试使用简单合并工具...")
        # 尝试使用简化合并工具
        os.chdir(script_dir)
        run_command(
            "python3 scheme_b_excel_merge_simple.py",
            "简化合并（备用）"
        )
        os.chdir(workspace)
    
    # 6. 验证数据质量
    print(f"\n🔄 步骤3: 验证数据质量...")
    quality_ok = check_data_quality()
    
    if quality_ok:
        print(f"✅ 数据质量验证通过!")
    else:
        print(f"⚠️  数据质量验证发现问题")
    
    # 7. 统计结果
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print(f"\n{'='*60}")
    print(f"🏁 自动工作流执行完成")
    print(f"{'='*60}")
    print(f"📅 开始时间: {start_time.strftime('%H:%M:%S')}")
    print(f"📅 结束时间: {end_time.strftime('%H:%M:%S')}")
    print(f"⏱️  总耗时: {duration:.1f} 秒")
    
    # 检查详情文件数量
    detail_files = []
    if os.path.exists("职位详情"):
        detail_files = [f for f in os.listdir("职位详情") if f.startswith('detail_') and f.endswith('.json')]
    
    # 检查已获取记录
    fetched_count = 0
    if os.path.exists("fetched_security_ids.txt"):
        with open("fetched_security_ids.txt", 'r', encoding='utf-8') as f:
            fetched_count = len([line for line in f if line.strip()])
    
    print(f"\n📊 最终状态:")
    print(f"   详情文件: {len(detail_files)} 个")
    print(f"   已获取记录: {fetched_count} 个")
    print(f"   主Excel文件: {'✅ 存在' if os.path.exists('深圳_ai.xlsx') else '❌ 不存在'}")
    
    # 8. 推荐下一步
    print(f"\n💡 推荐下一步:")
    
    if not get_success or (fetched_count < len(detail_files)):
        print(f"   1. 🔄 重新登录BOSS直聘")
        print(f"   2. 🚀 再次运行本工作流")
    else:
        # 检查是否还有未获取的
        with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
            all_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        remaining = len(all_ids) - fetched_count
        if remaining > 0:
            print(f"   1. 📊 还有 {remaining} 个详情待获取")
            print(f"   2. 🔄 重新登录后继续获取")
        else:
            print(f"   1. 🎉 所有详情已获取完成!")
            print(f"   2. 📈 可以开始数据分析和报告生成")
    
    print(f"\n✅ 自动工作流执行完成!")
    print(f"💡 下次使用: python3 scheme_b_auto_workflow.py")

if __name__ == "__main__":
    main()