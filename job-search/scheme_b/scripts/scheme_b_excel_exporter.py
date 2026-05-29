#!/usr/bin/env python3
"""
方案B Excel导出工具
专门用于从securityId文件导出Excel数据
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

def read_security_ids(file_path):
    """读取securityId文件"""
    security_ids = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
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
                else:
                    print(f"⚠️  第{line_num}行格式错误: {line}")
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
    
    return security_ids

def load_job_details_from_json(details_dir):
    """从JSON文件加载职位详情"""
    job_details = []
    
    if not Path(details_dir).exists():
        print(f"⚠️  详情目录不存在: {details_dir}")
        return job_details
    
    json_files = list(Path(details_dir).glob("*.json"))
    print(f"📁 找到 {len(json_files)} 个详情文件")
    
    for json_file in json_files[:50]:  # 最多处理50个文件
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('ok'):
                details = extract_job_details_for_excel(data, str(json_file))
                if details:
                    job_details.append(details)
        except Exception as e:
            print(f"⚠️  解析文件失败 {json_file.name}: {e}")
    
    return job_details

def extract_job_details_for_excel(detail_data, source_file):
    """从详情数据中提取Excel字段"""
    try:
        data = detail_data.get('data', {})
        job_info = data.get('jobInfo', {})
        brand_info = data.get('brandComInfo', {})
        
        # 35个字段的Excel模板
        details = {
            # ===== 基础信息 =====
            '职位ID': job_info.get('encryptId', ''),
            '职位名称': job_info.get('jobName', ''),
            'security_id': job_info.get('securityId', ''),
            
            # ===== 薪资信息 =====
            '薪资范围': job_info.get('salaryDesc', ''),
            '薪资下限': job_info.get('salaryLow', ''),
            '薪资上限': job_info.get('salaryHigh', ''),
            '薪资单位': job_info.get('salaryPeriod', ''),
            
            # ===== 要求信息 =====
            '工作经验': job_info.get('experienceName', ''),
            '学历要求': job_info.get('degreeName', ''),
            '职位类型': job_info.get('jobType', ''),
            
            # ===== 工作地点 =====
            '城市': job_info.get('city', ''),
            '区域': job_info.get('areaDistrict', ''),
            '地址': job_info.get('address', ''),
            '经度': job_info.get('longitude', ''),
            '纬度': job_info.get('latitude', ''),
            
            # ===== 公司信息 =====
            '公司名称': brand_info.get('brandName', ''),
            '公司规模': brand_info.get('scaleName', ''),
            '所属行业': brand_info.get('industryName', ''),
            '公司类型': brand_info.get('brandStageName', ''),
            '公司介绍': brand_info.get('introduction', '')[:500],
            
            # ===== 职位详情 =====
            '岗位描述': job_info.get('postDescription', '')[:2000],
            '职位亮点': job_info.get('highlight', ''),
            '技能要求': ', '.join(job_info.get('skills', [])),
            '福利待遇': ', '.join(job_info.get('welfareList', [])),
            
            # ===== 招聘信息 =====
            '招聘人数': job_info.get('recruitNum', ''),
            '发布人': job_info.get('publisher', {}).get('name', ''),
            '发布人职位': job_info.get('publisher', {}).get('title', ''),
            '在线状态': job_info.get('online', ''),
            
            # ===== 时间信息 =====
            '发布时间': job_info.get('publishTime', ''),
            '更新时间': job_info.get('updateTime', ''),
            '截止时间': job_info.get('deadLine', ''),
            
            # ===== 统计信息 =====
            '是否急招': job_info.get('urgent', ''),
            '是否推荐': job_info.get('recommend', ''),
            '职位状态': job_info.get('status', ''),
            '浏览数量': job_info.get('viewCount', ''),
            '申请数量': job_info.get('applyCount', ''),
            
            # ===== 系统信息 =====
            '数据来源': source_file,
            '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return details
        
    except Exception as e:
        print(f"⚠️  提取Excel字段失败: {e}")
        return None

def create_excel_from_security_ids(security_ids_file, output_file, use_existing_details=True):
    """
    从securityId文件创建Excel
    参数:
        security_ids_file: securityId文件路径
        output_file: 输出Excel文件路径
        use_existing_details: 是否使用已有的详情文件
    """
    print("🚀 方案B Excel导出工具")
    print("=" * 70)
    print(f"📁 输入文件: {security_ids_file}")
    print(f"📊 输出文件: {output_file}")
    print("=" * 70)
    
    # 读取securityId
    security_ids = read_security_ids(security_ids_file)
    if not security_ids:
        print("❌ 没有找到securityId")
        return False
    
    print(f"📊 找到 {len(security_ids)} 个securityId")
    
    # 加载已有的职位详情
    job_details = []
    if use_existing_details:
        details_dir = Path("职位详情")
        if details_dir.exists():
            job_details = load_job_details_from_json(details_dir)
            print(f"📊 从已有文件加载 {len(job_details)} 个职位详情")
    
    # 如果详情不足，显示提示
    if len(job_details) < min(10, len(security_ids)):
        print(f"\n⚠️  职位详情不足 ({len(job_details)}/{len(security_ids)})")
        print("💡 建议执行以下步骤获取更多详情:")
        print(f"   1. 在Chrome浏览器中登录BOSS直聘")
        print(f"   2. 关闭Chrome浏览器")
        print(f"   3. 执行获取详情脚本")
        print(f"   4. 重新运行此导出工具")
        
        # 询问是否继续
        response = input("\n是否继续导出? (y/n): ").strip().lower()
        if response != 'y':
            print("⏹️  用户取消导出")
            return False
    
    # 创建DataFrame
    if job_details:
        df = pd.DataFrame(job_details)
        
        # 保存到Excel
        try:
            df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"\n✅ Excel文件已生成: {output_file}")
            print(f"📊 导出统计:")
            print(f"  - 职位数量: {len(job_details)} 个")
            print(f"  - 字段数量: {len(df.columns)} 个")
            print(f"  - 文件大小: {Path(output_file).stat().st_size:,} 字节")
            
            # 显示字段列表
            print(f"\n📋 导出字段列表:")
            columns_by_category = {
                '基础信息': ['职位ID', '职位名称', 'security_id'],
                '薪资信息': ['薪资范围', '薪资下限', '薪资上限', '薪资单位'],
                '要求信息': ['工作经验', '学历要求', '职位类型'],
                '工作地点': ['城市', '区域', '地址', '经度', '纬度'],
                '公司信息': ['公司名称', '公司规模', '所属行业', '公司类型', '公司介绍'],
                '职位详情': ['岗位描述', '职位亮点', '技能要求', '福利待遇'],
                '招聘信息': ['招聘人数', '发布人', '发布人职位', '在线状态'],
                '时间信息': ['发布时间', '更新时间', '截止时间'],
                '统计信息': ['是否急招', '是否推荐', '职位状态', '浏览数量', '申请数量'],
                '系统信息': ['数据来源', '提取时间']
            }
            
            for category, fields in columns_by_category.items():
                existing_fields = [f for f in fields if f in df.columns]
                if existing_fields:
                    print(f"  {category} ({len(existing_fields)}个):")
                    for field in existing_fields:
                        print(f"    • {field}")
            
            return True
            
        except Exception as e:
            print(f"❌ Excel导出失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("❌ 没有职位详情可导出")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='方案B Excel导出工具')
    parser.add_argument('--input', default='all_security_ids_final.txt', help='securityId文件路径')
    parser.add_argument('--output', help='输出Excel文件路径')
    parser.add_argument('--skip-details', action='store_true', help='跳过详情检查')
    
    args = parser.parse_args()
    
    # 确定输出文件路径
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"深圳AI岗位_方案B_{timestamp}.xlsx"
    
    # 执行导出
    success = create_excel_from_security_ids(
        security_ids_file=args.input,
        output_file=output_file,
        use_existing_details=not args.skip_details
    )
    
    if success:
        print(f"\n{'=' * 70}")
        print("🎉 方案B Excel导出完成！")
        print(f"📁 输出文件: {output_file}")
        print(f"💡 使用说明:")
        print(f"  1. 使用Excel打开文件查看数据")
        print(f"  2. 如需更多详情，请先获取职位详情")
        print(f"  3. 重新运行此工具导出完整数据")
        print(f"{'=' * 70}")
        sys.exit(0)
    else:
        print(f"\n❌ Excel导出失败")
        sys.exit(1)

if __name__ == "__main__":
    main()