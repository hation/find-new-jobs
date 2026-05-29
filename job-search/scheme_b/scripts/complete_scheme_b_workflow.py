#!/usr/bin/env python3
"""
完整的方案B工作流：获取职位详情并导出Excel
包含完整的后续流程
"""

import os
import sys
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

def setup_environment():
    """设置环境变量"""
    boss_path = "/Users/xingan/Library/Python/3.12/bin"
    if boss_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = f"{boss_path}:{os.environ.get('PATH', '')}"

def run_boss_command(cmd_args, description=""):
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
        
        if result.returncode == 0:
            if description:
                print(f"✅ {description}")
            return True, result.stdout
        else:
            error_msg = result.stderr or result.stdout or "未知错误"
            if description:
                print(f"❌ {description}失败: {error_msg[:100]}")
            return False, error_msg
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {description}超时")
        return False, "命令超时"
    except Exception as e:
        print(f"🚨 {description}异常: {e}")
        return False, str(e)

def check_login_status():
    """检查登录状态"""
    print("🔍 检查登录状态...")
    success, result = run_boss_command(["status"], "检查状态")
    
    if success and "search=ok" in result:
        print("✅ 登录状态正常 (search=ok)")
        return True
    else:
        print("❌ 登录状态异常")
        print("💡 请确保已在Chrome浏览器中登录并关闭浏览器")
        return False

def fetch_job_details_from_security_ids(security_ids_file, max_details=20, batch_size=10):
    """
    从securityId文件获取职位详情
    分批获取，避免token过期
    """
    print(f"\n🔍 从文件获取职位详情: {security_ids_file}")
    print("=" * 60)
    
    # 读取securityId
    security_ids = []
    try:
        with open(security_ids_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 3:
                    security_ids.append({
                        'security_id': parts[0],
                        'job_name': parts[1],
                        'page': parts[2]
                    })
    except Exception as e:
        print(f"❌ 读取securityId文件失败: {e}")
        return []
    
    if not security_ids:
        print("❌ 没有找到securityId")
        return []
    
    print(f"📊 找到 {len(security_ids)} 个securityId")
    print(f"🔧 将获取前 {min(max_details, len(security_ids))} 个职位详情")
    
    # 限制获取数量
    security_ids = security_ids[:max_details]
    
    # 创建详情目录
    details_dir = Path("职位详情")
    details_dir.mkdir(exist_ok=True)
    
    # 分批获取详情
    all_details = []
    successful_count = 0
    
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
            success, result = run_boss_command(
                ["detail", security_id, "--json"],
                f"获取详情"
            )
            
            if success:
                try:
                    detail_data = json.loads(result)
                    if detail_data.get('ok'):
                        # 保存详情文件
                        detail_file = details_dir / f"detail_{security_id[:10]}.json"
                        with open(detail_file, 'w', encoding='utf-8') as f:
                            json.dump(detail_data, f, ensure_ascii=False, indent=2)
                        
                        # 提取关键信息
                        job_details = extract_job_details(detail_data, security_id)
                        if job_details:
                            all_details.append(job_details)
                            batch_success += 1
                            print(f"      ✅ 成功")
                        else:
                            print(f"      ⚠️  信息提取失败")
                    else:
                        print(f"      ❌ 数据异常")
                except:
                    print(f"      ❌ 解析失败")
            else:
                print(f"      ❌ 获取失败")
            
            # 延迟
            if i < len(batch_ids):
                time.sleep(1)
        
        successful_count += batch_success
        print(f"✅ 批次完成: {batch_success}/{len(batch_ids)} 成功")
        
        # 批次间提示
        if batch_end < len(security_ids):
            print(f"\n💡 批次完成，准备下一批次")
            print(f"📊 当前进度: {batch_end}/{len(security_ids)} 个职位")
            print(f"📊 成功获取: {successful_count} 个详情")
            print(f"⏳ 请确保登录状态正常，准备继续...")
    
    print(f"\n📊 详情获取完成:")
    print(f"  ✅ 成功: {successful_count} 个")
    print(f"  ❌ 失败: {len(security_ids) - successful_count} 个")
    print(f"  📊 成功率: {successful_count/len(security_ids)*100:.1f}%")
    
    return all_details

def extract_job_details(detail_data, security_id):
    """从详情数据中提取关键信息"""
    try:
        data = detail_data.get('data', {})
        job_info = data.get('jobInfo', {})
        brand_info = data.get('brandComInfo', {})
        
        # 提取35个字段（根据之前的模板）
        details = {
            # 基础信息
            'security_id': security_id,
            '职位名称': job_info.get('jobName', ''),
            '职位ID': job_info.get('encryptId', ''),
            '薪资范围': job_info.get('salaryDesc', ''),
            '薪资下限': job_info.get('salaryLow', ''),
            '薪资上限': job_info.get('salaryHigh', ''),
            '薪资单位': job_info.get('salaryPeriod', ''),
            '工作经验': job_info.get('experienceName', ''),
            '学历要求': job_info.get('degreeName', ''),
            '职位类型': job_info.get('jobType', ''),
            
            # 工作地点
            '城市': job_info.get('city', ''),
            '区域': job_info.get('areaDistrict', ''),
            '地址': job_info.get('address', ''),
            '经度': job_info.get('longitude', ''),
            '纬度': job_info.get('latitude', ''),
            
            # 公司信息
            '公司名称': brand_info.get('brandName', ''),
            '公司规模': brand_info.get('scaleName', ''),
            '所属行业': brand_info.get('industryName', ''),
            '公司类型': brand_info.get('brandStageName', ''),
            '公司介绍': brand_info.get('introduction', '')[:500],
            
            # 职位详情
            '岗位描述': job_info.get('postDescription', '')[:1000],
            '职位亮点': job_info.get('highlight', ''),
            '技能要求': ', '.join(job_info.get('skills', [])),
            '福利待遇': ', '.join(job_info.get('welfareList', [])),
            
            # 招聘信息
            '招聘人数': job_info.get('recruitNum', ''),
            '发布人': job_info.get('publisher', {}).get('name', ''),
            '发布人职位': job_info.get('publisher', {}).get('title', ''),
            '在线状态': job_info.get('online', ''),
            
            # 时间信息
            '发布时间': job_info.get('publishTime', ''),
            '更新时间': job_info.get('updateTime', ''),
            '截止时间': job_info.get('deadLine', ''),
            
            # 其他信息
            '是否急招': job_info.get('urgent', ''),
            '是否推荐': job_info.get('recommend', ''),
            '职位状态': job_info.get('status', ''),
            '浏览数量': job_info.get('viewCount', ''),
            '申请数量': job_info.get('applyCount', ''),
            
            # 提取时间
            '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return details
        
    except Exception as e:
        print(f"⚠️  提取职位详情失败: {e}")
        return None

def export_to_excel(job_details, output_file):
    """导出到Excel"""
    print(f"\n📊 导出到Excel: {output_file}")
    print("=" * 60)
    
    if not job_details:
        print("❌ 没有职位详情可导出")
        return False
    
    try:
        # 创建DataFrame
        df = pd.DataFrame(job_details)
        
        # 保存到Excel
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        print(f"✅ Excel文件已生成: {output_file}")
        print(f"📊 导出数据: {len(job_details)} 行 × {len(df.columns)} 列")
        
        # 显示字段列表
        print(f"\n📋 导出字段 ({len(df.columns)} 个):")
        for i, col in enumerate(df.columns, 1):
            print(f"  [{i:2d}] {col}")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel导出失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 完整的方案B工作流：获取职位详情并导出Excel")
    print("=" * 70)
    print("💡 包含：登录检查 → 获取详情 → 导出Excel")
    print("💡 基于已收集的securityId文件")
    print("=" * 70)
    
    # 设置环境
    setup_environment()
    
    # 检查登录状态
    if not check_login_status():
        print("\n❌ 登录状态异常，无法继续")
        print("💡 请执行以下步骤:")
        print("  1. 在Chrome浏览器中登录BOSS直聘")
        print("  2. 关闭Chrome浏览器")
        print("  3. 重新运行此脚本")
        return False
    
    # securityId文件路径
    security_ids_file = "all_security_ids_final.txt"
    if not Path(security_ids_file).exists():
        print(f"❌ securityId文件不存在: {security_ids_file}")
        return False
    
    # 获取职位详情
    job_details = fetch_job_details_from_security_ids(
        security_ids_file,
        max_details=20,  # 最多获取20个详情
        batch_size=8     # 每批8个，避免token过期
    )
    
    if not job_details:
        print("❌ 没有获取到职位详情")
        return False
    
    # 导出到Excel
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"深圳AI岗位详情_{timestamp}.xlsx"
    
    success = export_to_excel(job_details, output_file)
    
    if success:
        print(f"\n{'=' * 70}")
        print("🎉 完整的方案B工作流执行成功！")
        print(f"📊 执行结果:")
        print(f"  - 登录状态: ✅ 正常")
        print(f"  - 获取详情: {len(job_details)} 个职位")
        print(f"  - 导出Excel: {output_file}")
        print(f"  - 输出目录: {os.getcwd()}")
        print(f"{'=' * 70}")
        return True
    else:
        print(f"\n❌ 工作流执行失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)