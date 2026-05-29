#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汇总所有分页数据
"""

import json
import os
from datetime import datetime

print("=" * 80)
print("📊 快手招聘分页数据汇总报告")
print("=" * 80)

# 输入目录
INPUT_DIR = "output/ks_paginated"
OUTPUT_DIR = "output/ks_all_pages_aggregated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 查找所有分页数据文件
page_files = [f for f in os.listdir(INPUT_DIR) if f.startswith('positions_page_') and f.endswith('.json')]
page_files.sort()

print(f"📄 找到 {len(page_files)} 个分页数据文件")
print()

all_positions = []
total_positions = 0

# 读取每个页面的数据
for page_file in page_files:
    page_num = int(page_file.split('_')[2].split('.')[0])
    
    try:
        with open(os.path.join(INPUT_DIR, page_file), 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        positions = page_data.get('positions', [])
        count = len(positions)
        
        print(f"📄 第 {page_num:2d} 页: {count:3d} 个岗位")
        
        # 为每个岗位添加页码信息
        for position in positions:
            position['pageNumber'] = page_num
        
        all_positions.extend(positions)
        total_positions += count
        
    except Exception as e:
        print(f"❌ 读取第 {page_num} 页失败: {e}")

print()
print(f"📊 总计: {total_positions} 个岗位，来自 {len(page_files)} 页")
print()

# 统计信息
position_names = set()
work_locations = set()
position_categories = set()
work_experiences = set()
pages = set()

for position in all_positions:
    position_names.add(position.get('positionName', ''))
    work_locations.add(position.get('workLocation', ''))
    position_categories.add(position.get('positionCategory', ''))
    work_experiences.add(position.get('workExperience', ''))
    pages.add(position.get('pageNumber', 1))

# 按页面统计
positions_by_page = {}
for position in all_positions:
    page_num = position.get('pageNumber', 1)
    positions_by_page[page_num] = positions_by_page.get(page_num, 0) + 1

# 按地点统计
positions_by_location = {}
for position in all_positions:
    location = position.get('workLocation', '未知')
    positions_by_location[location] = positions_by_location.get(location, 0) + 1

# 按类别统计
positions_by_category = {}
for position in all_positions:
    category = position.get('positionCategory', '未知')
    positions_by_category[category] = positions_by_category.get(category, 0) + 1

# 按经验统计
positions_by_experience = {}
for position in all_positions:
    experience = position.get('workExperience', '未知')
    positions_by_experience[experience] = positions_by_experience.get(experience, 0) + 1

print("📈 统计信息:")
print(f"   • 唯一岗位名称: {len(position_names)} 种")
print(f"   • 唯一工作地点: {len(work_locations)} 个")
print(f"   • 唯一岗位类别: {len(position_categories)} 类")
print(f"   • 唯一工作经验: {len(work_experiences)} 种")
print()

print("📄 页面分布:")
for page_num in sorted(positions_by_page.keys()):
    count = positions_by_page[page_num]
    print(f"   第 {page_num:2d} 页: {count:3d} 个岗位 ({count/total_positions*100:.1f}%)")

print()

# 保存汇总数据
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 1. 保存所有岗位数据
all_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_all_pages_aggregated_{timestamp}.json")

all_data = {
    "metadata": {
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPositions": total_positions,
        "totalPages": len(pages),
        "source": "快手招聘网站（分页爬取）",
        "note": f"汇总了 {len(page_files)} 页的数据"
    },
    "statistics": {
        "uniquePositionNames": len(position_names),
        "uniqueWorkLocations": len(work_locations),
        "uniquePositionCategories": len(position_categories),
        "uniqueWorkExperiences": len(work_experiences),
        "positionsByPage": positions_by_page,
        "positionsByLocation": positions_by_location,
        "positionsByCategory": positions_by_category,
        "positionsByExperience": positions_by_experience
    },
    "summary": {
        "positionNames": list(position_names)[:20],
        "workLocations": list(work_locations)[:20],
        "positionCategories": list(position_categories)[:20],
        "workExperiences": list(work_experiences)[:10]
    },
    "positions": all_positions
}

with open(all_data_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"💾 保存所有分页数据: {all_data_file}")

# 2. 保存统计报告
stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_paginated_stats_{timestamp}.json")

stats_data = {
    "metadata": {
        "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPositions": total_positions,
        "totalPages": len(pages),
        "dataFiles": page_files
    },
    "pageDistribution": positions_by_page,
    "locationDistribution": positions_by_location,
    "categoryDistribution": positions_by_category,
    "experienceDistribution": positions_by_experience
}

with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(stats_data, f, ensure_ascii=False, indent=2)
print(f"📊 保存统计报告: {stats_file}")

# 3. 保存CSV格式
csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_paginated_positions_{timestamp}.csv")

with open(csv_file, 'w', encoding='utf-8-sig') as f:
    # 写入CSV头部
    f.write("positionId,positionName,workLocation,positionCategory,publishTime,workExperience,pageNumber,company,crawlTime\n")
    
    # 写入数据
    for position in all_positions:
        row = [
            position.get("positionId", ""),
            f'"{position.get("positionName", "")}"',
            f'"{position.get("workLocation", "")}"',
            f'"{position.get("positionCategory", "")}"',
            f'"{position.get("publishTime", "")}"',
            f'"{position.get("workExperience", "")}"',
            str(position.get("pageNumber", 1)),
            f'"{position.get("company", "快手")}"',
            f'"{position.get("crawlTime", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))}"'
        ]
        f.write(','.join(row) + '\n')

print(f"📈 保存CSV格式: {csv_file}")

print()
print("✅" * 35)
print("🎉 分页数据汇总完成！")
print("✅" * 35)
print()
print("📊 最终成果:")
print(f"   📈 总岗位数: {total_positions} 个")
print(f"   📄 总页面数: {len(pages)} 页")
print(f"   📂 输出目录: {OUTPUT_DIR}")
print()
print("📁 生成的文件:")
print(f"   • 所有分页数据: {os.path.basename(all_data_file)}")
print(f"   • 统计报告: {os.path.basename(stats_file)}")
print(f"   • CSV格式: {os.path.basename(csv_file)}")
print()
print("💡 数据使用:")
print("   1. 查看所有数据: cat output/ks_all_pages_aggregated/kuaishou_all_pages_aggregated_*.json")
print("   2. 查看统计报告: cat output/ks_all_pages_aggregated/kuaishou_paginated_stats_*.json")
print("   3. 用Excel打开: open output/ks_all_pages_aggregated/kuaishou_paginated_positions_*.csv")
print()
print("🎯 ks-job 项目目标达成: 成功获取筛选条件下的所有分页岗位数据")
print()
print("=" * 80)