#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开始爬取B站招聘数据
自动爬取所有页数据，跳过交互
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src/framework"))

print("=" * 70)
print("🚀 开始自动爬取B站招聘数据")
print("=" * 70)

try:
    from src.bilibili_api_crawler import BilibiliAPICrawler
    from framework.data_exporter import DataExporter
    
    print("✅ 导入爬取器和导出器成功")
    
    # 创建爬取器实例
    print("🔧 创建B站API爬取器...")
    crawler = BilibiliAPICrawler("config/api_auth.json")
    
    # 显示状态
    status = crawler.get_status()
    print(f"📊 公司: {status.get('company')}")
    print(f"🌐 API地址: {status.get('api_url')}")
    print(f"📊 每页数量: {status.get('page_size')}")
    print(f"📁 数据目录: {status.get('data_dir')}")
    print(f"📁 输出目录: {status.get('output_dir')}")
    print()
    
    # 测试第1页
    print("🧪 测试爬取第1页...")
    success, page_data, error = crawler.crawl_page(1)
    
    if not success:
        print(f"❌ 测试失败: {error}")
        sys.exit(1)
    
    print(f"✅ 测试成功，获取{len(page_data)}条数据")
    print()
    
    # 显示数据样本
    if page_data:
        print("📋 第1页数据样本:")
        for i, job in enumerate(page_data[:5], 1):
            print(f"  {i}. {job.get('title')} - {job.get('location')}")
            print(f"     类别: {job.get('category')}")
            print(f"     发布时间: {job.get('publish_time')}")
            print()
    
    # 自动爬取所有页
    print("🚀 开始自动爬取所有页数据...")
    print("📝 爬取策略:")
    print(f"  • 每页数量: {crawler.page_size}")
    print(f"  • 最大页数: 10页（先测试）")
    print(f"  • 请求间隔: 2秒")
    print()
    
    all_data = crawler.crawl_all_pages(max_pages=10)  # 先爬取10页测试
    
    if not all_data:
        print("❌ 未爬取到任何数据")
        sys.exit(1)
    
    print(f"✅ 爬取完成，共获取{len(all_data)}条数据")
    print()
    
    # 显示统计信息
    print("📊 数据统计:")
    print(f"  • 总记录数: {len(all_data)}")
    print(f"  • 数据来源: B站招聘官网")
    print(f"  • 爬取时间: {status.get('last_crawl_time', '刚刚')}")
    print()
    
    # 显示数据分布
    locations = {}
    categories = {}
    
    for job in all_data:
        location = job.get('location', '未知')
        category = job.get('category', '未知')
        
        locations[location] = locations.get(location, 0) + 1
        categories[category] = categories.get(category, 0) + 1
    
    print("📍 工作地点分布:")
    for location, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {location}: {count}个岗位")
    
    print()
    print("🏷️ 岗位类别分布:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {category}: {count}个岗位")
    
    print()
    
    # 保存数据
    print("💾 保存数据...")
    save_path = crawler.save_final_data(all_data)
    
    if save_path:
        print(f"✅ 数据已保存到: {save_path}")
        
        # 显示文件信息
        import os
        if os.path.exists(save_path):
            file_size = os.path.getsize(save_path)
            print(f"📁 文件大小: {file_size:,} 字节")
            
            # 加载保存的数据验证
            with open(save_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            saved_jobs = saved_data.get("data", [])
            print(f"📊 保存的记录数: {len(saved_jobs)}")
            
            # 显示保存的样本
            if saved_jobs:
                print("📋 保存的数据样本:")
                for i, job in enumerate(saved_jobs[:3], 1):
                    print(f"  {i}. {job.get('title')}")
                    print(f"     ID: {job.get('position_id')}")
                    print(f"     地点: {job.get('location')}")
                    print(f"     时间: {job.get('publish_time')}")
                    print()
    else:
        print("❌ 数据保存失败")
    
    # 导出数据到Excel
    print("📤 导出数据到Excel...")
    try:
        exporter = DataExporter()
        
        result = exporter.export_data(
            data=all_data,
            format="excel",
            company_name="bilibili",
            additional_info={
                "crawled_at": status.get('last_crawl_time', ''),
                "total_jobs": len(all_data),
                "source": "B站招聘官网"
            }
        )
        
        if result.get("success"):
            excel_file = result.get("files", {}).get("excel")
            if excel_file and os.path.exists(excel_file):
                print(f"✅ Excel文件: {excel_file}")
                print(f"📁 文件大小: {os.path.getsize(excel_file):,} 字节")
            else:
                print("⚠️ Excel文件生成但路径未返回")
        else:
            print(f"❌ Excel导出失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"⚠️ Excel导出异常: {e}")
        print("💡 可能需要安装pandas和openpyxl: pip install pandas openpyxl")
    
    print()
    print("📁 生成的文件:")
    
    # 列出生成的文件
    data_dir = Path("data/bilibili/raw")
    output_dir = Path("output/bilibili")
    
    if data_dir.exists():
        raw_files = list(data_dir.glob("*.json"))
        if raw_files:
            print(f"  📂 原始数据文件 ({len(raw_files)}个):")
            for file in raw_files[-3:]:  # 显示最后3个文件
                print(f"    • {file.name}")
    
    if output_dir.exists():
        output_files = list(output_dir.glob("*.json")) + list(output_dir.glob("*.xlsx")) + list(output_dir.glob("*.csv"))
        if output_files:
            print(f"  📂 输出文件 ({len(output_files)}个):")
            for file in output_files:
                file_size = file.stat().st_size
                print(f"    • {file.name} ({file_size:,} 字节)")
    
    print()
    print("🎉 爬取任务完成！")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("🔧 请确保已安装所有依赖: pip install -r requirements.txt")
    sys.exit(1)

except Exception as e:
    print(f"❌ 程序运行出错: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ B站招聘数据爬取完成！")
print("=" * 70)