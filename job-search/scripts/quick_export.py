#!/usr/bin/env python3
"""
Job Search技能 - 快速Excel导出工具
命令行界面，方便直接使用
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# 添加当前目录到PATH，以便导入export_to_excel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from export_to_excel import ExcelExporter
except ImportError:
    print("❌ 无法导入ExcelExporter，请确保export_to_excel.py在同一目录")
    sys.exit(1)

def load_json_data(file_path):
    """从JSON文件加载数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同的JSON格式
        if isinstance(data, list):
            return data
        elif 'data' in data and 'jobList' in data['data']:
            return data['data']['jobList']
        elif 'jobList' in data:
            return data['jobList']
        else:
            print(f"⚠️  JSON格式不标准，尝试直接使用")
            return [data] if isinstance(data, dict) else []
            
    except Exception as e:
        print(f"❌ 加载JSON文件失败: {e}")
        return []

def load_text_data(file_path):
    """从文本文件加载数据（boss-cli原始输出）"""
    jobs = []
    current_job = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.rstrip('\n')
            
            if not line.strip():
                continue
                
            # 检测新岗位开始
            if line.startswith('jobName:') and not line.startswith('    jobName:'):
                # 保存上一个岗位
                if current_job:
                    jobs.append(current_job)
                
                # 开始新岗位
                current_job = {'jobName': line.replace('jobName:', '').strip()}
                
            elif current_job:
                # 提取字段
                if line.startswith('  '):  # 缩进字段
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        current_job[key.strip()] = value.strip()
        
        # 添加最后一个岗位
        if current_job:
            jobs.append(current_job)
            
        return jobs
        
    except Exception as e:
        print(f"❌ 加载文本文件失败: {e}")
        return []

def export_from_boss_cli(keyword, city="深圳", pages=3):
    """直接从boss-cli搜索并导出"""
    import subprocess
    import time
    
    print(f"🔍 正在搜索 {city} 的 {keyword} 岗位（{pages}页）...")
    
    all_jobs = []
    
    for page in range(1, pages + 1):
        print(f"  第 {page}/{pages} 页...")
        
        try:
            # 执行boss-cli命令
            cmd = f"boss search '{keyword}' --city {city} --page {page} --json"
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
    parser = argparse.ArgumentParser(description='快速导出BOSS直聘岗位数据到Excel格式')
    
    # 输入源选项
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--json-file', '-j', help='从JSON文件导入数据')
    input_group.add_argument('--text-file', '-t', help='从文本文件导入数据（boss-cli原始输出）')
    input_group.add_argument('--search', '-s', help='直接搜索关键词并导出')
    
    # 搜索参数
    parser.add_argument('--city', default='深圳', help='搜索城市（默认：深圳）')
    parser.add_argument('--pages', type=int, default=3, help='搜索页数（默认：3）')
    parser.add_argument('--keyword', help='搜索关键词（与--search一起使用）')
    
    # 输出参数
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--filename', '-f', help='输出文件名')
    
    args = parser.parse_args()
    
    print("🚀 Job Search技能 - Excel快速导出工具")
    print("=" * 50)
    
    # 加载数据
    jobs_data = []
    
    if args.json_file:
        print(f"📁 从JSON文件加载: {args.json_file}")
        jobs_data = load_json_data(args.json_file)
        
    elif args.text_file:
        print(f"📁 从文本文件加载: {args.text_file}")
        jobs_data = load_text_data(args.text_file)
        
    elif args.search:
        keyword = args.keyword if args.keyword else args.search
        print(f"🔍 直接搜索: {keyword} (城市: {args.city}, 页数: {args.pages})")
        jobs_data = export_from_boss_cli(keyword, args.city, args.pages)
    
    if not jobs_data:
        print("❌ 没有找到任何岗位数据")
        sys.exit(1)
    
    print(f"📊 加载完成，共 {len(jobs_data)} 个岗位")
    
    # 创建导出器
    exporter = ExcelExporter(args.output_dir)
    
    # 导出数据
    try:
        output_files = exporter.export_jobs_to_excel(
            jobs_data, 
            filename=args.filename,
            include_stats=True
        )
        
        print(f"\n🎉 导出成功！")
        print(f"📁 主要文件: {output_files[0]}")
        
        # 提供使用建议
        print(f"\n💡 立即用Excel打开:")
        print(f"  open \"{output_files[0]}\"")
        
        print(f"\n📋 所有生成的文件:")
        for file in output_files:
            print(f"  • {os.path.basename(file)}")
            
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()