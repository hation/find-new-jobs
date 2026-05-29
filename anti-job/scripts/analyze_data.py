#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析爬取的蚂蚁国际招聘数据
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter
import statistics

def analyze_data():
    project_root = Path(__file__).parent.parent
    output_base = project_root / "output"
    
    print("="*70)
    print("📊 分析蚂蚁国际招聘数据")
    print("="*70)
    
    # 查找最新的爬取目录
    crawl_dirs = list(output_base.glob("auto_crawl_*"))
    if not crawl_dirs:
        print("❌ 没有找到爬取目录")
        return
    
    # 取最新的目录
    latest_dir = sorted(crawl_dirs, key=lambda x: x.name)[-1]
    print(f"📁 分析目录: {latest_dir.name}")
    
    # 检查是否完成
    report_file = latest_dir / "crawl_report.json"
    if not report_file.exists():
        print("⚠️  爬取可能还未完成，报告文件不存在")
        print("   将分析已爬取的数据...")
    
    # 分析岗位数据
    positions_dir = latest_dir / "positions"
    if not positions_dir.exists():
        print("❌ 岗位目录不存在")
        return
    
    position_files = list(positions_dir.glob("*.json"))
    if not position_files:
        print("❌ 没有岗位数据文件")
        return
    
    print(f"\n📊 数据文件: {len(position_files)} 个岗位文件")
    
    # 分析数据
    all_positions = []
    category_counter = Counter()
    location_counter = Counter()
    department_counter = Counter()
    experience_counter = Counter()
    degree_counter = Counter()
    
    field_counts = Counter()
    total_fields = 0
    
    for file_path in position_files[:100]:  # 先分析前100个，避免内存问题
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                position = json.load(f)
            
            all_positions.append(position)
            
            # 统计字段
            for field in position.keys():
                if position[field] is not None and position[field] != "":
                    field_counts[field] += 1
            
            total_fields += len(position)
            
            # 统计类别
            categories = position.get("categories", [])
            category_names = position.get("category_names", [])
            if category_names:
                for cat in category_names:
                    category_counter[cat] += 1
            elif categories:
                for cat in categories:
                    category_counter[str(cat)] += 1
            
            # 统计工作地点
            locations = position.get("workLocations", [])
            if locations:
                for loc in locations:
                    location_counter[loc] += 1
            
            # 统计部门
            department = position.get("department", "")
            if department:
                department_counter[department] += 1
            
            # 统计经验要求
            experience = position.get("experience", {})
            if isinstance(experience, dict):
                from_years = experience.get("from")
                to_years = experience.get("to")
                if from_years is not None or to_years is not None:
                    if from_years is not None and to_years is not None:
                        exp_range = f"{from_years}-{to_years}年"
                    elif from_years is not None:
                        exp_range = f"{from_years}+年"
                    else:
                        exp_range = f"≤{to_years}年"
                    experience_counter[exp_range] += 1
                else:
                    experience_counter["经验不限"] += 1
            else:
                experience_counter["未指定"] += 1
            
            # 统计学历要求
            degree = position.get("degree", "")
            if degree:
                degree_map = {
                    "bachelor": "本科",
                    "master": "硕士", 
                    "doctor": "博士",
                    "college": "大专",
                    "high_school": "高中"
                }
                display_degree = degree_map.get(degree, degree)
                degree_counter[display_degree] += 1
            else:
                degree_counter["未指定"] += 1
                
        except Exception as e:
            print(f"⚠️  分析文件 {file_path.name} 时出错: {e}")
    
    print(f"✅ 已分析 {len(all_positions)} 个岗位")
    
    # 输出分析结果
    print("\n" + "="*70)
    print("📈 数据分析结果")
    print("="*70)
    
    # 1. 字段完整性分析
    print(f"\n📋 字段完整性 (基于{len(all_positions)}个样本):")
    if all_positions:
        sample_position = all_positions[0]
        total_fields_in_sample = len(sample_position)
        
        print(f"  每个岗位平均字段数: {total_fields / len(all_positions):.1f}")
        print(f"  样本岗位字段数: {total_fields_in_sample}")
        
        print(f"\n  📊 字段出现频率:")
        sorted_fields = sorted(field_counts.items(), key=lambda x: x[1], reverse=True)
        for field, count in sorted_fields[:15]:  # 显示前15个
            percentage = (count / len(all_positions)) * 100
            print(f"    • {field}: {count}/{len(all_positions)} ({percentage:.1f}%)")
        
        if len(sorted_fields) > 15:
            print(f"    • ... 共{len(sorted_fields)}个字段")
    
    # 2. 类别分布
    print(f"\n🎯 岗位类别分布:")
    if category_counter:
        total_categories = sum(category_counter.values())
        for category, count in category_counter.most_common():
            percentage = (count / total_categories) * 100
            print(f"    • {category}: {count}个 ({percentage:.1f}%)")
    
    # 3. 工作地点分布
    print(f"\n📍 工作地点分布:")
    if location_counter:
        total_locations = sum(location_counter.values())
        for location, count in location_counter.most_common(10):
            percentage = (count / total_locations) * 100
            print(f"    • {location}: {count}个 ({percentage:.1f}%)")
        
        if len(location_counter) > 10:
            print(f"    • ... 共{len(location_counter)}个工作地点")
    
    # 4. 部门分布
    print(f"\n🏢 部门分布 (前10名):")
    if department_counter:
        for department, count in department_counter.most_common(10):
            print(f"    • {department}: {count}个")
        
        if len(department_counter) > 10:
            print(f"    • ... 共{len(department_counter)}个部门")
    
    # 5. 经验要求分布
    print(f"\n📈 经验要求分布:")
    if experience_counter:
        total_exp = sum(experience_counter.values())
        for exp_range, count in experience_counter.most_common():
            percentage = (count / total_exp) * 100
            print(f"    • {exp_range}: {count}个 ({percentage:.1f}%)")
    
    # 6. 学历要求分布
    print(f"\n🎓 学历要求分布:")
    if degree_counter:
        total_degree = sum(degree_counter.values())
        for degree, count in degree_counter.most_common():
            percentage = (count / total_degree) * 100
            print(f"    • {degree}: {count}个 ({percentage:.1f}%)")
    
    # 7. 数据质量评估
    print(f"\n🔍 数据质量评估:")
    
    # 检查必需字段
    required_fields = ["id", "name", "workLocations", "categories"]
    missing_counts = {}
    
    for field in required_fields:
        count = field_counts.get(field, 0)
        missing = len(all_positions) - count
        if missing > 0:
            missing_counts[field] = missing
    
    if missing_counts:
        print(f"  ⚠️  缺失必需字段:")
        for field, missing in missing_counts.items():
            print(f"    • {field}: 缺失{missing}个 ({missing/len(all_positions)*100:.1f}%)")
    else:
        print(f"  ✅ 所有必需字段完整")
    
    # 检查岗位名称长度
    name_lengths = []
    for position in all_positions:
        name = position.get("name", "")
        if name:
            name_lengths.append(len(name))
    
    if name_lengths:
        avg_length = statistics.mean(name_lengths)
        print(f"  📝 岗位名称平均长度: {avg_length:.1f}字符")
        print(f"  📝 最短名称: {min(name_lengths)}字符")
        print(f"  📝 最长名称: {max(name_lengths)}字符")
    
    # 8. 样本数据展示
    print(f"\n🔍 样本数据 (第一个岗位):")
    if all_positions:
        sample = all_positions[0]
        print(f"  📄 ID: {sample.get('id', 'N/A')}")
        print(f"  📄 名称: {sample.get('name', 'N/A')}")
        print(f"  📄 地点: {sample.get('workLocations', 'N/A')}")
        print(f"  📄 部门: {sample.get('department', 'N/A')}")
        print(f"  📄 类别: {sample.get('category_names', sample.get('categories', 'N/A'))}")
        print(f"  📄 学历: {sample.get('degree', 'N/A')}")
        
        experience = sample.get("experience", {})
        if isinstance(experience, dict):
            exp_str = f"{experience.get('from', '')}-{experience.get('to', '')}年"
            print(f"  📄 经验: {exp_str}")
        
        publish_time = sample.get("publishTime", "")
        if publish_time:
            print(f"  📄 发布时间: {publish_time}")
    
    # 9. 保存分析报告
    analysis_report = {
        "analysis_time": datetime.now().isoformat(),
        "data_source": str(latest_dir),
        "sample_size": len(all_positions),
        "field_analysis": dict(field_counts),
        "category_distribution": dict(category_counter),
        "location_distribution": dict(location_counter),
        "department_distribution": dict(department_counter.most_common(20)),
        "experience_distribution": dict(experience_counter),
        "degree_distribution": dict(degree_counter),
        "data_quality": {
            "required_fields_missing": dict(missing_counts),
            "name_length_stats": {
                "average": avg_length if name_lengths else 0,
                "min": min(name_lengths) if name_lengths else 0,
                "max": max(name_lengths) if name_lengths else 0
            }
        }
    }
    
    analysis_dir = latest_dir / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    
    report_file = analysis_dir / "data_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析报告已保存到: {report_file}")
    
    print("\n" + "="*70)
    print("🎉 数据分析完成")
    print("="*70)
    
    return analysis_report

if __name__ == "__main__":
    analyze_data()