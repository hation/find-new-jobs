#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细数据检查脚本
验证夸克爬取数据的完整性、准确性和一致性
"""

import json
import os
from collections import Counter
from datetime import datetime

def detailed_data_check():
    """详细数据检查"""
    print("🔍 夸克爬取数据详细检查")
    print("=" * 60)
    
    # 找到最新的输出目录
    import glob
    output_dirs = glob.glob("output/quark_page1_*")
    if not output_dirs:
        print("❌ 未找到输出目录")
        return
    
    latest_dir = sorted(output_dirs, key=os.path.getmtime, reverse=True)[0]
    print(f"📁 检查目录: {latest_dir}")
    print()
    
    # 1. 检查汇总报告
    print("1️⃣ 汇总报告检查:")
    summary_file = os.path.join(latest_dir, "crawl_summary.json")
    if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        crawl_summary = summary.get("crawl_summary", {})
        print(f"   ✅ 总计获取: {crawl_summary.get('total_positions_extracted', 0)} 个岗位")
        print(f"   ✅ 目标岗位: {crawl_summary.get('target_positions', 0)} 个")
        print(f"   ✅ 完成比例: {crawl_summary.get('completion_percentage', 0):.1f}%")
        print(f"   ✅ 成功页数: {crawl_summary.get('successful_pages', 0)}/10 页")
        print(f"   ✅ 数据质量: {crawl_summary.get('data_quality', 'unknown')}")
    else:
        print("   ❌ 汇总报告文件不存在")
    
    print()
    
    # 2. 检查处理后的数据
    print("2️⃣ 处理后数据检查:")
    processed_file = os.path.join(latest_dir, "all_positions_processed.json")
    if os.path.exists(processed_file):
        with open(processed_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        positions = data.get("positions", [])
        metadata = data.get("metadata", {})
        
        print(f"   ✅ 岗位总数: {len(positions)}")
        print(f"   ✅ 字段数/岗位: {metadata.get('fields_per_position', 0)}")
        print(f"   ✅ 数据来源: {metadata.get('source', 'unknown')}")
        print(f"   ✅ 提取时间: {metadata.get('extract_time', 'unknown')}")
        
        # 检查字段完整性
        if positions:
            first_pos = positions[0]
            print(f"   ✅ 字段示例: {', '.join(list(first_pos.keys())[:8])}...")
            
            # 统计字段缺失情况
            missing_fields = []
            required_fields = [
                'position_id', 'position_name', 'position_category',
                'work_location', 'update_time', 'education_requirement',
                'position_description', 'position_requirements'
            ]
            
            for pos in positions[:5]:  # 检查前5个岗位
                for field in required_fields:
                    if field not in pos or not pos[field]:
                        missing_fields.append(field)
            
            if missing_fields:
                print(f"   ⚠️  发现缺失字段: {set(missing_fields)}")
            else:
                print("   ✅ 所有关键字段完整")
    else:
        print("   ❌ 处理后数据文件不存在")
    
    print()
    
    # 3. 检查原始数据文件
    print("3️⃣ 原始数据文件检查:")
    raw_files = glob.glob(os.path.join(latest_dir, "quark_page_*_raw.json"))
    print(f"   ✅ 找到 {len(raw_files)} 个原始数据文件")
    
    total_raw_positions = 0
    page_distribution = {}
    
    for raw_file in sorted(raw_files):
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            page = raw_data.get("metadata", {}).get("page", "unknown")
            positions = raw_data.get("positions", [])
            count = len(positions)
            
            total_raw_positions += count
            page_distribution[page] = count
            
        except Exception as e:
            print(f"   ❌ 读取 {raw_file} 失败: {e}")
    
    print(f"   ✅ 原始数据总计: {total_raw_positions} 个岗位")
    print(f"   📊 页面分布: {page_distribution}")
    
    print()
    
    # 4. 数据一致性检查
    print("4️⃣ 数据一致性检查:")
    
    # 检查处理数据与原始数据数量是否一致
    if 'positions' in locals():
        processed_count = len(positions)
        print(f"   ✅ 处理后数据: {processed_count} 个岗位")
        print(f"   ✅ 原始数据: {total_raw_positions} 个岗位")
        
        if processed_count == total_raw_positions:
            print("   ✅ 数据数量一致")
        else:
            print(f"   ⚠️  数据数量不一致: 处理后 {processed_count} vs 原始 {total_raw_positions}")
    
    # 检查岗位ID唯一性
    if 'positions' in locals():
        position_ids = [pos.get('position_id') for pos in positions]
        unique_ids = set(position_ids)
        
        print(f"   ✅ 唯一岗位ID: {len(unique_ids)} 个")
        print(f"   ✅ 总计岗位数: {len(position_ids)} 个")
        
        if len(unique_ids) == len(position_ids):
            print("   ✅ 所有岗位ID唯一")
        else:
            print(f"   ⚠️  发现重复岗位ID: {len(position_ids) - len(unique_ids)} 个")
            
            # 找出重复的ID
            id_counter = Counter(position_ids)
            duplicates = [id for id, count in id_counter.items() if count > 1]
            print(f"     重复ID: {duplicates[:5]}{'...' if len(duplicates) > 5 else ''}")
    
    print()
    
    # 5. 数据质量分析
    print("5️⃣ 数据质量分析:")
    
    if 'positions' in locals():
        # 分析工作地点分布
        locations = []
        categories = []
        
        for pos in positions:
            locations.append(pos.get('work_location', '未知'))
            categories.append(pos.get('position_category', '未知'))
        
        location_counter = Counter(locations)
        category_counter = Counter(categories)
        
        print(f"   📍 工作地点分布: {len(location_counter)} 个不同地点")
        print(f"      主要地点: {', '.join([f'{loc}({count})' for loc, count in location_counter.most_common(5)])}")
        
        print(f"   🏷️  岗位类别分布: {len(category_counter)} 个不同类别")
        print(f"      主要类别: {', '.join([f'{cat}({count})' for cat, count in category_counter.most_common(5)])}")
        
        # 检查字段填充率
        fields_to_check = ['position_description', 'position_requirements', 'position_url']
        for field in fields_to_check:
            filled = sum(1 for pos in positions if pos.get(field))
            fill_rate = filled / len(positions) * 100
            print(f"   📝 {field}填充率: {fill_rate:.1f}% ({filled}/{len(positions)})")
    
    print()
    
    # 6. 数据文件大小检查
    print("6️⃣ 文件大小检查:")
    
    files_to_check = [
        ("汇总报告", "crawl_summary.json"),
        ("处理后数据", "all_positions_processed.json"),
        ("原始数据目录", "")
    ]
    
    for name, filename in files_to_check:
        if filename:
            filepath = os.path.join(latest_dir, filename)
            if os.path.exists(filepath):
                size_kb = os.path.getsize(filepath) / 1024
                print(f"   📄 {name}: {size_kb:.1f} KB")
            else:
                print(f"   ❌ {name}: 文件不存在")
        else:
            dir_size = sum(os.path.getsize(os.path.join(latest_dir, f)) for f in os.listdir(latest_dir) if os.path.isfile(os.path.join(latest_dir, f)))
            print(f"   📁 所有文件总计: {dir_size/1024:.1f} KB")
    
    print()
    print("=" * 60)
    print("🎯 检查总结:")
    print(f"   目录: {latest_dir}")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   状态: ✅ 数据检查完成")
    print("=" * 60)

def main():
    """主函数"""
    print("🔍 夸克校园招聘数据详细检查")
    print("=" * 60)
    print("📊 验证数据完整性、准确性和一致性")
    print()
    
    # 切换到脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    detailed_data_check()

if __name__ == "__main__":
    main()