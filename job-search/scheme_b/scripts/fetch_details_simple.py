#!/usr/bin/env python3
"""
简化的获取详情脚本 - 方案B专用
从securityId文件获取职位详情
"""

import os
import sys
import json
import time
from pathlib import Path

def setup_environment():
    """设置环境变量"""
    boss_path = "/Users/xingan/Library/Python/3.12/bin"
    if boss_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = f"{boss_path}:{os.environ.get('PATH', '')}"

def run_boss_command(cmd_args):
    """运行boss命令"""
    import subprocess
    cmd = ["boss"] + cmd_args
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout
    except:
        return False, "命令执行失败"

def check_login():
    """检查登录状态"""
    print("🔍 检查登录状态...")
    success, result = run_boss_command(["status"])
    
    if success and "search=ok" in result:
        print("✅ 登录状态正常 (search=ok)")
        return True
    else:
        print("❌ 登录状态异常")
        return False

def fetch_details_from_file(input_file, max_details=10, batch_size=5):
    """
    从文件获取详情
    参数:
        input_file: securityId文件
        max_details: 最多获取多少个详情
        batch_size: 每批处理多少个
    """
    print(f"\n📋 从文件获取详情: {input_file}")
    print("=" * 60)
    
    # 读取securityId
    security_ids = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 3:
                    security_ids.append({
                        'security_id': parts[0],
                        'job_name': parts[1],
                        'page': parts[2],
                        'line_num': line_num
                    })
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return False
    
    if not security_ids:
        print("❌ 没有找到securityId")
        return False
    
    print(f"📊 找到 {len(security_ids)} 个securityId")
    
    # 限制获取数量
    if len(security_ids) > max_details:
        print(f"🔧 将获取前 {max_details} 个详情")
        security_ids = security_ids[:max_details]
    
    # 创建详情目录
    details_dir = Path("职位详情_本次获取")
    details_dir.mkdir(exist_ok=True)
    
    # 分批获取
    total_success = 0
    
    for batch_start in range(0, len(security_ids), batch_size):
        batch_end = min(batch_start + batch_size, len(security_ids))
        batch_ids = security_ids[batch_start:batch_end]
        
        print(f"\n🔄 批次 {batch_start//batch_size + 1}: 处理 {len(batch_ids)} 个职位")
        print("-" * 40)
        
        batch_success = 0
        for i, job_info in enumerate(batch_ids, 1):
            security_id = job_info['security_id']
            job_name = job_info['job_name']
            page = job_info['page']
            
            print(f"  [{i}] 获取: {job_name} (第{page}页)")
            
            # 获取详情
            success, result = run_boss_command(["detail", security_id, "--json"])
            
            if success:
                try:
                    detail_data = json.loads(result)
                    if detail_data.get('ok'):
                        # 保存详情文件
                        detail_file = details_dir / f"detail_{security_id[:10]}.json"
                        with open(detail_file, 'w', encoding='utf-8') as f:
                            json.dump(detail_data, f, ensure_ascii=False, indent=2)
                        
                        batch_success += 1
                        print(f"      ✅ 成功")
                    else:
                        print(f"      ❌ 数据异常")
                except:
                    print(f"      ❌ 解析失败")
            else:
                print(f"      ❌ 获取失败")
            
            # 延迟
            if i < len(batch_ids):
                time.sleep(1)
        
        total_success += batch_success
        print(f"✅ 批次完成: {batch_success}/{len(batch_ids)} 成功")
        
        # 检查token是否过期
        if batch_end < len(security_ids):
            print(f"\n💡 检查登录状态...")
            if not check_login():
                print("⚠️  登录状态异常，需要重新登录")
                print("💡 请执行以下步骤:")
                print("  1. 在Chrome浏览器中重新登录BOSS直聘")
                print("  2. 关闭Chrome浏览器")
                print("  3. 重新运行此脚本")
                break
    
    print(f"\n📊 详情获取完成:")
    print(f"  ✅ 成功: {total_success} 个")
    print(f"  ❌ 失败: {len(security_ids) - total_success} 个")
    print(f"  📊 成功率: {total_success/len(security_ids)*100:.1f}%")
    print(f"  📁 详情文件: {details_dir}")
    
    return total_success > 0

def main():
    """主函数"""
    print("🚀 简化的获取详情脚本 - 方案B专用")
    print("=" * 70)
    print("💡 从securityId文件获取职位详情")
    print("💡 分批处理，避免token过期")
    print("=" * 70)
    
    # 设置环境
    setup_environment()
    
    # 检查登录状态
    if not check_login():
        print("\n❌ 登录状态异常，无法继续")
        print("💡 请执行以下步骤:")
        print("  1. 在Chrome浏览器中登录BOSS直聘")
        print("  2. 关闭Chrome浏览器")
        print("  3. 重新运行此脚本")
        return False
    
    # 输入文件
    input_file = "all_security_ids_final.txt"
    if not Path(input_file).exists():
        print(f"❌ 输入文件不存在: {input_file}")
        print("💡 请先运行方案B收集securityId")
        return False
    
    # 获取详情
    success = fetch_details_from_file(
        input_file=input_file,
        max_details=15,  # 最多获取15个详情
        batch_size=5     # 每批5个
    )
    
    if success:
        print(f"\n{'=' * 70}")
        print("🎉 获取详情完成！")
        print("💡 下一步操作:")
        print("  1. 使用Excel导出工具生成Excel文件")
        print("  2. 或重新登录获取更多详情")
        print(f"{'=' * 70}")
        return True
    else:
        print(f"\n❌ 获取详情失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)