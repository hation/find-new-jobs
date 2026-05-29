#!/usr/bin/env python3
"""
Job Search技能 - 包含岗位描述的Excel导出工具
命令行界面，方便直接使用
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加当前目录到PATH，以便导入excel_export_with_description
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from excel_export_with_description import ExcelExporterWithDescription
except ImportError as e:
    print(f"❌ 无法导入ExcelExporterWithDescription: {e}")
    print("💡 请确保excel_export_with_description.py在同一目录")
    sys.exit(1)

def load_jobs_data(file_path):
    """从JSON文件加载数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📁 加载文件: {file_path}")
        
        # 处理不同的JSON格式
        if isinstance(data, list):
            print(f"✅ 格式: 岗位列表，共 {len(data)} 个岗位")
            return data
        elif 'data' in data and 'jobList' in data['data']:
            jobs = data['data']['jobList']
            print(f"✅ 格式: BOSS直聘标准格式，共 {len(jobs)} 个岗位")
            return jobs
        elif 'jobList' in data:
            jobs = data['jobList']
            print(f"✅ 格式: 简化格式，共 {len(jobs)} 个岗位")
            return jobs
        else:
            print(f"⚠️  格式不标准，尝试直接使用")
            return [data] if isinstance(data, dict) else []
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return []
    except Exception as e:
        print(f"❌ 加载文件失败: {e}")
        return []

def search_and_export(keyword, city="深圳", pages=3, include_description=True, max_desc=50):
    """直接从boss-cli搜索并导出（包含描述）"""
    import subprocess
    import time
    
    print(f"🔍 正在搜索 {city} 的 {keyword} 岗位（{pages}页）...")
    print(f"📝 包含岗位描述: {'是' if include_description else '否'}")
    
    all_jobs = []
    
    for page in range(1, pages + 1):
        print(f"  第 {page}/{pages} 页...")
        
        try:
            # 执行boss-cli命令
            cmd = f"boss search '{keyword}' --city {city} --page {page} --json"
            print(f"    执行: {cmd}")
            
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析JSON输出
                data = json.loads(result.stdout)
                
                # 提取岗位列表
                if 'data' in data and 'jobList' in data['data']:
                    page_jobs = data['data']['jobList']
                elif 'jobList' in data:
                    page_jobs = data['jobList']
                else:
                    page_jobs = []
                
                # 添加搜索信息
                for job in page_jobs:
                    job['search_keyword'] = keyword
                    job['search_page'] = page
                    job['search_city'] = city
                
                all_jobs.extend(page_jobs)
                print(f"    找到 {len(page_jobs)} 个岗位")
                
                # 如果这页没有数据，停止
                if len(page_jobs) == 0:
                    print("    本页无数据，停止搜索")
                    break
            else:
                print(f"    搜索失败: {result.stderr[:100]}")
                
        except Exception as e:
            print(f"    搜索异常: {e}")
        
        # 避免请求过快
        if page < pages:
            time.sleep(2)
    
    return all_jobs

def main():
    parser = argparse.ArgumentParser(
        description='导出BOSS直聘岗位数据到Excel（包含详细的岗位描述）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 从JSON文件导出，包含岗位描述
  python3 export_with_desc.py --input data.json
  
  # 从JSON文件导出，不获取岗位描述
  python3 export_with_desc.py --input data.json --no-description
  
  # 直接搜索并导出
  python3 export_with_desc.py --search AI --city 深圳 --pages 5
  
  # 指定输出目录和最多获取的描述数
  python3 export_with_desc.py --input data.json --output-dir ~/my-data --max-desc 100
        """
    )
    
    # 输入源选项
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument('--input', '-i', help='从JSON文件导入数据')
    input_group.add_argument('--search', '-s', help='直接搜索关键词并导出')
    
    # 搜索参数
    parser.add_argument('--city', default='深圳', help='搜索城市（默认：深圳）')
    parser.add_argument('--pages', type=int, default=3, help='搜索页数（默认：3）')
    parser.add_argument('--keyword', help='搜索关键词（与--search一起使用）')
    
    # 导出参数
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--no-description', action='store_true', help='不获取岗位描述（默认获取）')
    parser.add_argument('--max-desc', type=int, default=50, help='最多获取描述的岗位数（默认50）')
    parser.add_argument('--filename', '-f', help='输出文件名（可选）')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.input and not args.search:
        print("❌ 必须指定输入文件(--input)或搜索关键词(--search)")
        parser.print_help()
        sys.exit(1)
    
    print("🚀 Job Search技能 - Excel导出工具（包含岗位描述）")
    print("=" * 60)
    
    # 加载数据
    jobs_data = []
    
    if args.input:
        if not os.path.exists(args.input):
            print(f"❌ 文件不存在: {args.input}")
            sys.exit(1)
        
        jobs_data = load_jobs_data(args.input)
        
    elif args.search:
        keyword = args.keyword if args.keyword else args.search
        print(f"🔍 直接搜索: {keyword}")
        print(f"📍 城市: {args.city}")
        print(f"📄 页数: {args.pages}")
        print(f"📝 包含岗位描述: {'是' if not args.no_description else '否'}")
        
        jobs_data = search_and_export(
            keyword, 
            city=args.city, 
            pages=args.pages, 
            include_description=not args.no_description,
            max_desc=args.max_desc
        )
    
    if not jobs_data:
        print("❌ 没有找到任何岗位数据")
        sys.exit(1)
    
    print(f"📊 数据加载完成，共 {len(jobs_data)} 个岗位")
    
    # 检查是否有岗位ID（用于获取描述）
    if not args.no_description:
        jobs_with_id = [job for job in jobs_data if job.get('encryptJobId')]
        print(f"🔑 有岗位ID的岗位: {len(jobs_with_id)} 个")
        
        if len(jobs_with_id) == 0:
            print("⚠️  警告：没有岗位ID，无法获取岗位描述")
            print("💡 建议：使用boss-cli的--json格式输出，或者重新搜索")
    
    # 创建导出器
    include_description = not args.no_description
    exporter = ExcelExporterWithDescription(
        output_dir=args.output_dir,
        include_description=include_description
    )
    
    # 导出数据
    try:
        print("\n📤 开始导出Excel数据...")
        print("-" * 40)
        
        output_files = exporter.export_jobs_with_descriptions(
            jobs_data,
            fetch_descriptions=include_description,
            max_jobs_with_desc=args.max_desc
        )
        
        print("\n🎉 导出成功！")
        print("=" * 40)
        
        # 显示主要文件信息
        main_file = output_files[0]
        file_size = os.path.getsize(main_file) if os.path.exists(main_file) else 0
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"📁 主要文件: {os.path.basename(main_file)}")
        print(f"📏 文件大小: {file_size_mb:.2f} MB")
        print(f"📍 保存位置: {os.path.dirname(main_file)}")
        
        if include_description:
            # 统计描述获取情况
            descriptions = [job.get('jobDescription', '') for job in jobs_data[:args.max_desc]]
            valid_descriptions = [d for d in descriptions if d and d not in ['未获取岗位描述', '未能获取详细描述', '缺少岗位ID']]
            print(f"📝 岗位描述: 成功获取 {len(valid_descriptions)}/{min(len(jobs_data), args.max_desc)} 个")
        
        # 提供使用建议
        print("\n💡 使用建议:")
        print(f"1. 用Excel打开: open \"{main_file}\"")
        print("2. 调整'岗位描述'列宽查看完整内容")
        print("3. 使用筛选功能按描述关键词搜索")
        
        print(f"\n📋 所有生成的文件:")
        for file in output_files:
            basename = os.path.basename(file)
            size = os.path.getsize(file) if os.path.exists(file) else 0
            size_kb = size / 1024
            print(f"  • {basename} ({size_kb:.1f} KB)")
        
        # 显示Excel使用提示
        print(f"\n🔧 Excel使用技巧:")
        print("  1. 选中'岗位描述'列 → 格式 → 自动调整列宽")
        print("  2. 数据 → 筛选 → 在'岗位描述'列搜索关键词")
        print("  3. 文件 → 另存为 → 选择.xlsx格式保存")
        
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()