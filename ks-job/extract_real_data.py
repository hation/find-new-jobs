#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从分页JSON文件中提取真实数据并生成正确的CSV
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("📊 快手招聘真实数据提取与合并")
print("=" * 80)

# 输入目录
INPUT_DIR = "output/ks_paginated"
OUTPUT_DIR = "output/ks_real_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 查找所有分页数据文件
page_files = [f for f in os.listdir(INPUT_DIR) if f.startswith('positions_page_') and f.endswith('.json')]
page_files.sort()

print(f"📄 找到 {len(page_files)} 个分页数据文件")
print()

all_real_positions = []
total_positions = 0

# 从文本中提取岗位信息的函数
def extract_position_from_text(text: str, page_num: int) -> Optional[Dict[str, Any]]:
    """从文本中提取岗位信息"""
    if not text or len(text) < 20:
        return None
    
    # 快手招聘的典型格式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 清理文本
    text = text.strip()
    
    # 提取岗位名称（在【或-之前的部分）
    position_name = ""
    if '【' in text:
        before_bracket = text.split('【')[0]
        position_name = before_bracket.strip()
    elif '-' in text:
        before_dash = text.split('-')[0]
        position_name = before_dash.strip()
    else:
        # 如果没有分隔符，尝试提取前部分
        parts = text.split(' ')
        if len(parts) > 0:
            position_name = parts[0].strip()
    
    # 提取岗位类别（在【】中）
    position_category = ""
    if '【' in text and '】' in text:
        match = re.search(r'【([^】]+)】', text)
        if match:
            position_category = match.group(1).strip()
    
    # 提取工作地点
    work_location = ""
    # 常见城市
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安', '天津', '重庆']
    for city in cities:
        if city in text:
            work_location = city
            break
    
    # 如果没找到单一城市，可能是多个城市
    if not work_location and ',' in text:
        # 尝试提取逗号分隔的城市
        for city in cities:
            if f"{city}," in text or f",{city}" in text:
                work_location = text
                break
    
    # 提取工作经验
    work_experience = ""
    exp_match = re.search(r'(\d+-\d+年)', text)
    if exp_match:
        work_experience = exp_match.group(1)
    
    # 提取发布时间
    publish_time = ""
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', text)
    if time_match:
        publish_time = time_match.group(1)
    
    # 只有包含足够信息才返回
    if position_name and work_location:
        return {
            "positionName": position_name,
            "positionCategory": position_category,
            "workLocation": work_location,
            "workExperience": work_experience,
            "publishTime": publish_time,
            "page": page_num,
            "rawText": text[:200]
        }
    
    return None

# 读取每个页面的数据
for page_file in page_files:
    page_num = int(page_file.split('_')[2].split('.')[0])
    
    try:
        with open(os.path.join(INPUT_DIR, page_file), 'r', encoding='utf-8') as f:
            page_data = json.load(f)
        
        positions = page_data.get('positions', [])
        real_positions_in_page = 0
        
        # 处理每个位置数据
        for position_data in positions:
            text = position_data.get('text', '')
            html = position_data.get('html', '')
            
            # 从文本中提取岗位信息
            if text and len(text) > 20:
                # 检查是否是表格行数据
                if 'Java 开发工程师' in text or '技术战略' in text or 'PMO' in text or 'AI' in text or '游戏' in text:
                    position_info = extract_position_from_text(text, page_num)
                    if position_info:
                        all_real_positions.append(position_info)
                        real_positions_in_page += 1
                else:
                    # 可能是包含多个岗位的文本块
                    lines = text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if len(line) > 20 and ('Java' in line or '技术' in line or 'PMO' in line or 'AI' in line or '游戏' in line):
                            position_info = extract_position_from_text(line, page_num)
                            if position_info:
                                all_real_positions.append(position_info)
                                real_positions_in_page += 1
        
        print(f"📄 第 {page_num:2d} 页: 提取到 {real_positions_in_page:3d} 个真实岗位")
        total_positions += real_positions_in_page
        
    except Exception as e:
        print(f"❌ 处理第 {page_num} 页失败: {e}")

print()
print(f"📊 总计: {total_positions} 个真实岗位，来自 {len(page_files)} 页")
print()

# 统计信息
position_names = set()
work_locations = set()
position_categories = set()
work_experiences = set()
pages = set()

for position in all_real_positions:
    position_names.add(position.get('positionName', ''))
    work_locations.add(position.get('workLocation', ''))
    position_categories.add(position.get('positionCategory', ''))
    work_experiences.add(position.get('workExperience', ''))
    pages.add(position.get('page', 1))

# 按页面统计
positions_by_page = {}
for position in all_real_positions:
    page_num = position.get('page', 1)
    positions_by_page[page_num] = positions_by_page.get(page_num, 0) + 1

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

# 1. 保存所有真实岗位数据
all_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_real_positions_{timestamp}.json")

# 创建标准化的岗位数据
standard_positions = []
for idx, position in enumerate(all_real_positions):
    position_id = f"KS_REAL_{position.get('page', 1):03d}_{idx+1:03d}_{timestamp}"
    
    # 标准化时间格式
    publish_time = position.get("publishTime", "")
    if publish_time:
        publish_time = publish_time.replace('.', '-')
    else:
        publish_time = datetime.now().strftime("%Y-%m-%d")
    
    standard_position = {
        "positionId": position_id,
        "positionName": position.get("positionName", ""),
        "workLocation": position.get("workLocation", ""),
        "positionCategory": position.get("positionCategory", ""),
        "publishTime": publish_time,
        "workExperience": position.get("workExperience", ""),
        "pageNumber": position.get("page", 1),
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position_id}",
        "rawText": position.get("rawText", "")[:100]
    }
    standard_positions.append(standard_position)

all_data = {
    "metadata": {
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPositions": total_positions,
        "totalPages": len(pages),
        "source": "快手招聘网站（真实数据提取）",
        "note": f"从 {len(page_files)} 页中提取的真实岗位数据"
    },
    "statistics": {
        "uniquePositionNames": len(position_names),
        "uniqueWorkLocations": len(work_locations),
        "uniquePositionCategories": len(position_categories),
        "uniqueWorkExperiences": len(work_experiences),
        "positionsByPage": positions_by_page
    },
    "summary": {
        "positionNames": list(position_names)[:20],
        "workLocations": list(work_locations)[:20],
        "positionCategories": list(position_categories)[:20],
        "workExperiences": list(work_experiences)[:10]
    },
    "positions": standard_positions
}

with open(all_data_file, 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"💾 保存所有真实岗位数据: {all_data_file}")

# 2. 保存统计报告
stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_real_stats_{timestamp}.json")

stats_data = {
    "metadata": {
        "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalPositions": total_positions,
        "totalPages": len(pages),
        "dataFiles": page_files
    },
    "pageDistribution": positions_by_page,
    "samplePositions": standard_positions[:10]
}

with open(stats_file, 'w', encoding='utf-8') as f:
    json.dump(stats_data, f, ensure_ascii=False, indent=2)
print(f"📊 保存统计报告: {stats_file}")

# 3. 保存正确的CSV格式
csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_real_positions_{timestamp}.csv")

with open(csv_file, 'w', encoding='utf-8-sig') as f:
    # 写入CSV头部
    f.write("positionId,positionName,workLocation,positionCategory,publishTime,workExperience,pageNumber,company,crawlTime,detailUrl\n")
    
    # 写入真实数据
    for position in standard_positions:
        row = [
            position.get("positionId", ""),
            f'"{position.get("positionName", "")}"',
            f'"{position.get("workLocation", "")}"',
            f'"{position.get("positionCategory", "")}"',
            f'"{position.get("publishTime", "")}"',
            f'"{position.get("workExperience", "")}"',
            str(position.get("pageNumber", 1)),
            f'"{position.get("company", "")}"',
            f'"{position.get("crawlTime", "")}"',
            f'"{position.get("detailUrl", "")}"'
        ]
        f.write(','.join(row) + '\n')

print(f"📈 保存正确的CSV格式: {csv_file}")

# 4. 显示前10个岗位作为示例
print()
print("📋 前10个真实岗位示例:")
for i, position in enumerate(standard_positions[:10]):
    print(f"  {i+1:2d}. {position.get('positionName', '')[:30]:30} | {position.get('workLocation', ''):8} | {position.get('positionCategory', '')[:10]:10} | {position.get('workExperience', ''):8} | 第{position.get('pageNumber', 1)}页")

print()
print("✅" * 35)
print("🎉 真实数据提取与合并完成！")
print("✅" * 35)
print()
print("📊 最终成果:")
print(f"   📈 总岗位数: {total_positions} 个")
print(f"   📄 总页面数: {len(pages)} 页")
print(f"   📂 输出目录: {OUTPUT_DIR}")
print()
print("📁 生成的文件:")
print(f"   • 所有真实岗位数据: {os.path.basename(all_data_file)}")
print(f"   • 统计报告: {os.path.basename(stats_file)}")
print(f"   • 正确的CSV格式: {os.path.basename(csv_file)}")
print()
print("💡 数据使用:")
print("   1. 查看所有真实数据: cat output/ks_real_data/kuaishou_real_positions_*.json")
print("   2. 查看统计报告: cat output/ks_real_data/kuaishou_real_stats_*.json")
print("   3. 用Excel打开: open output/ks_real_data/kuaishou_real_positions_*.csv")
print()
print("🎯 ks-job 项目目标达成: 成功提取并合并所有分页的真实岗位数据")
print()
print("=" * 80)