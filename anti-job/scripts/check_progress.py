#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查爬取进度
"""

import json
from pathlib import Path
from datetime import datetime

def check_progress():
    project_root = Path(__file__).parent.parent
    output_base = project_root / "output"
    
    print("="*70)
    print("📊 检查蚂蚁国际招聘爬取进度")
    print("="*70)
    
    # 查找最新的爬取目录
    crawl_dirs = list(output_base.glob("auto_crawl_*"))
    if not crawl_dirs:
        print("❌ 没有找到爬取目录")
        return
    
    # 按时间排序，取最新的
    latest_dir = sorted(crawl_dirs, key=lambda x: x.name)[-1]
    print(f"📁 最新爬取目录: {latest_dir.name}")
    print(f"📁 完整路径: {latest_dir}")
    
    # 检查目录结构
    if not latest_dir.exists():
        print("❌ 目录不存在")
        return
    
    # 检查文件数量
    positions_dir = latest_dir / "positions"
    pages_dir = latest_dir / "pages"
    report_file = latest_dir / "crawl_report.json"
    
    positions_count = 0
    pages_count = 0
    
    if positions_dir.exists():
        positions_count = len(list(positions_dir.glob("*.json")))
    
    if pages_dir.exists():
        pages_count = len(list(pages_dir.glob("*.json")))
    
    print(f"\n📊 文件统计:")
    print(f"  📄 岗位文件: {positions_count} 个")
    print(f"  📄 页面文件: {pages_count} 个")
    
    # 检查报告文件
    if report_file.exists():
        print(f"  📊 报告文件: ✅ 存在")
        
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            
            print(f"\n📈 爬取进度:")
            print(f"  📄 总岗位数: {report['stats'].get('total_positions', 'N/A')}")
            print(f"  💾 已保存: {report['stats'].get('positions_saved', 'N/A')}")
            print(f"  📊 总页数: {report['stats'].get('total_pages', 'N/A')}")
            print(f"  ❌ 失败页数: {report['stats'].get('failed_pages', 'N/A')}")
            
            if 'duration_seconds' in report:
                print(f"  ⏱️  耗时: {report['duration_seconds']:.1f}秒")
            
            # 显示类别分布
            if 'category_summary' in report and 'category_counts' in report['category_summary']:
                print(f"\n🎯 类别分布:")
                category_counts = report['category_summary']['category_counts']
                total_saved = report['stats'].get('positions_saved', 0)
                
                for category, count in category_counts.items():
                    if count > 0 and total_saved > 0:
                        percentage = (count / total_saved) * 100
                        print(f"  • {category}: {count}个 ({percentage:.1f}%)")
            
        except Exception as e:
            print(f"❌ 读取报告文件失败: {e}")
    else:
        print(f"  📊 报告文件: ❌ 不存在（可能还在爬取中）")
    
    # 检查是否有正在进行的爬取（通过检查最新文件）
    if positions_dir.exists():
        position_files = list(positions_dir.glob("*.json"))
        if position_files:
            latest_position = max(position_files, key=lambda x: x.stat().st_mtime)
            latest_time = datetime.fromtimestamp(latest_position.stat().st_mtime)
            now = datetime.now()
            time_diff = (now - latest_time).total_seconds()
            
            print(f"\n⏰ 最新文件时间: {latest_time.strftime('%H:%M:%S')}")
            print(f"⏰ 与当前时间差: {time_diff:.0f}秒")
            
            if time_diff < 60:  # 1分钟内
                print("🟢 爬取可能仍在进行中")
            elif time_diff < 300:  # 5分钟内
                print("🟡 爬取可能已完成，或暂停中")
            else:
                print("🔴 爬取可能已停止")
    
    print("\n📁 目录内容预览:")
    for item in latest_dir.iterdir():
        if item.is_dir():
            file_count = len(list(item.glob("*")))
            print(f"  📂 {item.name}/ ({file_count}个文件)")
        else:
            size_kb = item.stat().st_size / 1024
            print(f"  📄 {item.name} ({size_kb:.1f}KB)")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    check_progress()