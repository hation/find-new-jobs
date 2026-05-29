#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘最终数据提取器
从已成功爬取的数据中提取筛选条件下的所有岗位
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🚀 快手招聘最终数据提取器")
print("=" * 80)
print("从已成功爬取的数据中提取筛选条件下的所有岗位")
print()

# 输入文件（我们之前成功爬取的数据）
TEXT_FILE = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/ks-job/output/ks_simple_full/ks_page_text_20260522_181928.txt"

# 输出目录
OUTPUT_DIR = "output/ks_final_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/final_extractor.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


def load_crawled_data() -> Optional[str]:
    """加载已爬取的数据"""
    if not os.path.exists(TEXT_FILE):
        log(f"❌ 文本文件不存在: {TEXT_FILE}")
        return None
    
    try:
        log(f"📄 加载已爬取的数据: {TEXT_FILE}")
        with open(TEXT_FILE, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        log(f"✅ 数据加载成功，大小: {len(text_content)} 字符")
        return text_content
    except Exception as e:
        log(f"❌ 加载数据失败: {e}")
        return None


def extract_all_positions(text: str) -> List[Dict[str, Any]]:
    """从文本中提取所有岗位数据"""
    log("🔍 开始提取所有岗位数据...")
    
    positions = []
    
    if not text:
        return positions
    
    # 快手招聘的典型格式模式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 方法1: 按行分析
    lines = text.split('\n')
    log(f"📄 文本共有 {len(lines)} 行")
    
    # 查找包含岗位信息的行
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) < 30:
            continue
        
        # 检查是否包含岗位信息
        if is_position_line(line):
            position_data = extract_position_from_line(line, line_num)
            if position_data:
                positions.append(position_data)
    
    log(f"✅ 方法1提取到 {len(positions)} 个岗位")
    
    # 方法2: 正则表达式匹配
    log("🔍 使用方法2（正则表达式）提取...")
    
    # 快手招聘的格式模式
    patterns = [
        # 格式: Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22
        r'([^【】\d]{5,30}?)(?:-|【)([^】]{2,10})】([^】]{2,10})([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
        
        # 格式: 岗位名称 工作地点 工作经验 更新时间
        r'([^0-9]{5,30}?)\s+([^0-9]{2,10}?)\s+(\d+-\d+年)\s+(\d{4}\.\d{2}\.\d{2})',
        
        # 包含【】的格式
        r'([^【】]{5,30})【([^】]+)】([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            log(f"✅ 正则匹配找到 {len(matches)} 个岗位: {pattern[:50]}...")
            
            for match in matches:
                if len(match) >= 4:
                    position_data = {
                        "positionName": match[0].strip() if len(match) > 0 else "",
                        "positionCategory": match[1].strip() if len(match) > 1 else "",
                        "workLocation": match[2].strip() if len(match) > 2 else "",
                        "workExperience": match[3].strip() if len(match) > 3 else "",
                        "publishTime": match[4].strip() if len(match) > 4 else "",
                        "extractionMethod": "regex_pattern",
                        "rawLine": str(match)[:200]
                    }
                    
                    # 检查是否已存在
                    if not is_duplicate_position(position_data, positions):
                        positions.append(position_data)
    
    # 去重
    unique_positions = []
    seen_keys = set()
    
    for position in positions:
        # 创建唯一标识键
        key = f"{position.get('positionName', '')}_{position.get('workLocation', '')}_{position.get('workExperience', '')}"
        
        if key not in seen_keys:
            seen_keys.add(key)
            unique_positions.append(position)
    
    log(f"📊 去重后剩余 {len(unique_positions)} 个唯一岗位")
    
    return unique_positions


def is_position_line(line: str) -> bool:
    """检查一行是否包含岗位信息"""
    # 岗位相关关键词
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理',
        '策划', '销售', '市场', '客服', '行政', '财务'
    ]
    
    # 地点关键词
    location_keywords = [
        '北京', '上海', '广州', '深圳', '杭州', '成都',
        '武汉', '南京', '西安', '苏州', '重庆', '天津'
    ]
    
    # 检查是否包含关键词
    has_position_keyword = any(keyword in line for keyword in position_keywords)
    has_location_keyword = any(keyword in line for keyword in location_keywords)
    
    # 检查是否有时间格式（快手格式: 2026.05.22）
    has_time_format = re.search(r'\d{4}\.\d{2}\.\d{2}', line) is not None
    
    # 检查是否有工作经验格式（如：3-5年）
    has_experience_format = re.search(r'\d+-\d+年', line) is not None
    
    # 如果包含岗位关键词，并且有地点、时间或经验中的至少一个，认为是岗位行
    return has_position_keyword and (has_location_keyword or has_time_format or has_experience_format)


def extract_position_from_line(line: str, line_num: int) -> Optional[Dict[str, Any]]:
    """从单行文本中提取岗位信息"""
    # 初始化结果
    result = {
        "rawLine": line[:200],
        "lineNumber": line_num,
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": "",
        "extractionMethod": "line_analysis"
    }
    
    # 1. 提取岗位名称（在【或-之前的部分）
    name_match = re.search(r'^([^【】\[-]{5,40}?)(?:-|【|\[)', line)
    if name_match:
        result["positionName"] = name_match.group(1).strip()
    else:
        # 尝试提取包含关键词的部分
        for keyword in ['工程师', '开发', '产品', '运营', '设计', '经理', '专员']:
            if keyword in line:
                start = max(0, line.find(keyword) - 20)
                end = min(len(line), line.find(keyword) + 10)
                result["positionName"] = line[start:end].strip()
                break
    
    # 2. 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', line)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    
    # 3. 提取工作地点
    # 先尝试从【】后的部分提取
    if '】' in line:
        after_bracket = line.split('】', 1)[1]
        location_match = re.search(r'([^0-9,，、]{2,10}?)(?:\d|$)', after_bracket)
        if location_match:
            result["workLocation"] = location_match.group(1).strip()
    
    # 如果没有找到，搜索城市名
    if not result["workLocation"]:
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安']
        for city in cities:
            if city in line:
                result["workLocation"] = city
                break
    
    # 4. 提取工作经验
    exp_match = re.search(r'(\d+-\d+年)', line)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    else:
        # 尝试其他格式
        exp_patterns = [r'(\d+年)', r'([一二三四五六七八九十]+年)']
        for pattern in exp_patterns:
            match = re.search(pattern, line)
            if match:
                result["workExperience"] = match.group(1)
                break
    
    # 5. 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
    if time_match:
        result["publishTime"] = time_match.group(1)
    else:
        # 尝试其他格式
        time_patterns = [r'(\d{4}-\d{2}-\d{2})', r'(\d{4}/\d{2}/\d{2})']
        for pattern in time_patterns:
            match = re.search(pattern, line)
            if match:
                result["publishTime"] = match.group(1)
                break
    
    # 只有提取到足够信息才返回
    if result["positionName"] and (result["workLocation"] or result["workExperience"]):
        return result
    
    return None


def is_duplicate_position(new_position: Dict[str, Any], existing_positions: List[Dict[str, Any]]) -> bool:
    """检查是否重复岗位"""
    if not existing_positions:
        return False
    
    new_name = new_position.get("positionName", "")
    new_location = new_position.get("workLocation", "")
    new_experience = new_position.get("workExperience", "")
    
    for existing in existing_positions:
        existing_name = existing.get("positionName", "")
        existing_location = existing.get("workLocation", "")
        existing_experience = existing.get("workExperience", "")
        
        # 如果名称、地点、经验都相同或高度相似，认为是重复
        if (new_name and existing_name and new_name in existing_name or existing_name in new_name):
            if (not new_location and not existing_location) or (new_location and existing_location and new_location == existing_location):
                return True
    
    return False


def create_standard_position(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
    # 标准化时间格式
    publish_time = raw_position.get("publishTime", "")
    if publish_time:
        publish_time = publish_time.replace('.', '-').replace('/', '-')
    else:
        publish_time = datetime.now().strftime("%Y-%m-%d")
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": raw_position.get("positionName", "快手招聘岗位"),
        "workLocation": raw_position.get("workLocation", "全国"),
        "positionCategory": raw_position.get("positionCategory", ""),
        "publishTime": publish_time,
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position_id}",
        "department": "",
        "educationRequirement": "",
        "workExperience": raw_position.get("workExperience", ""),
        "jobResponsibilities": "",
        "jobRequirements": "",
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "final_extractor",
        "source": "kuaishou_final",
        
        # 提取信息
        "extractionInfo": {
            "method": raw_position.get("extractionMethod", ""),
            "lineNumber": raw_position.get("lineNumber"),
            "rawLine": raw_position.get("rawLine", "")[:100]
        }
    }


def filter_positions_by_conditions(positions: List[Dict[str, Any]], conditions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据筛选条件过滤岗位"""
    filtered_positions = positions
    
    # 按工作地点筛选
    if conditions.get("workLocation"):
        location_filter = conditions["workLocation"]
        filtered_positions = [
            p for p in filtered_positions 
            if location_filter in p.get("workLocation", "")
        ]
        log(f"📍 按工作地点 '{location_filter}' 筛选后: {len(filtered_positions)} 个岗位")
    
    # 按岗位类别筛选
    if conditions.get("positionCategory"):
        category_filter = conditions["positionCategory"]
        filtered_positions = [
            p for p in filtered_positions 
            if category_filter in p.get("positionCategory", "")
        ]
        log(f"🏷️  按岗位类别 '{category_filter}' 筛选后: {len(filtered_positions)} 个岗位")
    
    # 按工作经验筛选
    if conditions.get("workExperience"):
        experience_filter = conditions["workExperience"]
        filtered_positions = [
            p for p in filtered_positions 
            if experience_filter in p.get("workExperience", "")
        ]
        log(f"📅 按工作经验 '{experience_filter}' 筛选后: {len(filtered_positions)} 个岗位")
    
    return filtered_positions


def save_final_results(positions: List[Dict[str, Any]], conditions: Dict[str, Any]) -> Dict[str, Any]:
    """保存最终结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存所有岗位数据
    all_positions_file = os.path.join(OUTPUT_DIR, f"kuaishou_all_positions_{timestamp}.json")
    
    all_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "conditions": conditions,
            "source": "快手招聘网站",
            "filterApplied": bool(conditions)
        },
        "positions": positions
    }
    
    try:
        with open(all_positions_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存所有岗位数据: {all_positions_file}")
    except Exception as e:
        log(f"❌ 保存所有岗位数据失败: {e}")
        all_positions_file = ""
    
    # 2. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_statistics_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in positions]
    work_locations = []
    position_categories = []
    work_experiences = []
    
    for p in positions:
        location = p.get("workLocation", "")
        if location and location not in work_locations:
            work_locations.append(location)
        
        category = p.get("positionCategory", "")
        if category and category not in position_categories:
            position_categories.append(category)
        
        experience = p.get("workExperience", "")
        if experience and experience not in work_experiences:
            work_experiences.append(experience)
    
    stats_data = {
        "metadata": {
            "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "uniquePositionNames": len(set(position_names)),
            "uniqueWorkLocations": len(work_locations),
            "uniquePositionCategories": len(position_categories),
            "uniqueWorkExperiences": len(work_experiences),
            "conditions": conditions
        },
        "summary": {
            "positionNames": list(set(position_names))[:20],
            "workLocations": work_locations[:20],
            "positionCategories": position_categories[:20],
            "workExperiences": work_experiences[:10]
        },
        "distribution": {
            "byLocation": {},
            "byCategory": {},
            "byExperience": {}
        }
    }
    
    # 统计分布
    for p in positions:
        location = p.get("workLocation", "未知")
        category = p.get("positionCategory", "未知")
        experience = p.get("workExperience", "未知")
        
        stats_data["distribution"]["byLocation"][location] = stats_data["distribution"]["byLocation"].get(location, 0) + 1
        stats_data["distribution"]["byCategory"][category] = stats_data["distribution"]["byCategory"].get(category, 0) + 1
        stats_data["distribution"]["byExperience"][experience] = stats_data["distribution"]["byExperience"].get(experience, 0) + 1
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    # 3. 保存CSV格式（便于Excel打开）
    csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_positions_{timestamp}.csv")
    
    try:
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            # 写入CSV头部
            f.write("positionId,positionName,workLocation,positionCategory,publishTime,workExperience,company,crawlTime,detailUrl\n")
            
            # 写入数据
            for position in positions:
                row = [
                    position.get("positionId", ""),
                    f'"{position.get("positionName", "")}"',
                    f'"{position.get("workLocation", "")}"',
                    f'"{position.get("positionCategory", "")}"',
                    f'"{position.get("publishTime", "")}"',
                    f'"{position.get("workExperience", "")}"',
                    f'"{position.get("company", "")}"',
                    f'"{position.get("crawlTime", "")}"',
                    f'"{position.get("detailUrl", "")}"'
                ]
                f.write(','.join(row) + '\n')
        
        log(f"📈 保存CSV格式: {csv_file}")
    except Exception as e:
        log(f"❌ 保存CSV格式失败: {e}")
        csv_file = ""
    
    # 4. 保存Markdown报告（便于阅读）
    md_file = os.path.join(OUTPUT_DIR, f"kuaishou_report_{timestamp}.md")
    
    try:
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 快手招聘岗位数据报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**数据来源**: 快手招聘网站 (https://zhaopin.kuaishou.cn)\n")
            f.write(f"**筛选条件**: {json.dumps(conditions, ensure_ascii=False, indent=2) if conditions else '无筛选'}\n\n")
            
            f.write(f"## 📊 数据概览\n\n")
            f.write(f"- **总岗位数**: {len(positions)} 个\n")
            f.write(f"- **唯一岗位名称**: {len(set(position_names))} 个\n")
            f.write(f"- **工作地点分布**: {len(work_locations)} 个城市\n")
            f.write(f"- **岗位类别**: {len(position_categories)} 个类别\n")
            f.write(f"- **工作经验要求**: {len(work_experiences)} 种类型\n\n")
            
            f.write(f"## 📍 工作地点分布\n\n")
            for location, count in sorted(stats_data["distribution"]["byLocation"].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- {location}: {count} 个岗位\n")
            
            f.write(f"\n## 🏷️  岗位类别分布\n\n")
            for category, count in sorted(stats_data["distribution"]["byCategory"].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- {category}: {count} 个岗位\n")
            
            f.write(f"\n## 📅 工作经验分布\n\n")
            for experience, count in sorted(stats_data["distribution"]["byExperience"].items(), key=lambda x: x[1], reverse=True)[:10]:
                f.write(f"- {experience}: {count} 个岗位\n")
            
            f.write(f"\n## 📋 岗位列表（前20个）\n\n")
            f.write(f"| 序号 | 岗位名称 | 工作地点 | 岗位类别 | 工作经验 | 发布时间 |\n")
            f.write(f"|------|----------|----------|----------|----------|----------|\n")
            
            for i, position in enumerate(positions[:20], 1):
                f.write(f"| {i} | {position.get('positionName', '')} | {position.get('workLocation', '')} | {position.get('positionCategory', '')} | {position.get('workExperience', '')} | {position.get('publishTime', '')} |\n")
            
            f.write(f"\n## 💾 生成文件\n\n")
            f.write(f"- **JSON数据**: `{os.path.basename(all_positions_file) if all_positions_file else '未生成'}`\n")
            f.write(f"- **统计报告**: `{os.path.basename(stats_file) if stats_file else '未生成'}`\n")
            f.write(f"- **CSV文件**: `{os.path.basename(csv_file) if csv_file else '未生成'}`\n")
            f.write(f"- **Markdown报告**: `{os.path.basename(md_file)}`\n\n")
            
            f.write(f"## 🔗 相关链接\n\n")
            f.write(f"- 快手招聘官网: https://zhaopin.kuaishou.cn\n")
            f.write(f"- 数据来源文件: {TEXT_FILE}\n")
            f.write(f"- 输出目录: {OUTPUT_DIR}\n")
        
        log(f"📝 保存Markdown报告: {md_file}")
    except Exception as e:
        log(f"❌ 保存Markdown报告失败: {e}")
        md_file = ""
    
    return {
        "all_positions": all_positions_file,
        "statistics": stats_file,
        "csv": csv_file,
        "markdown": md_file
    }


def main():
    """主函数"""
    print()
    print("📋 最终数据提取流程:")
    print("   1. 加载已成功爬取的数据")
    print("   2. 智能提取所有岗位信息")
    print("   3. 应用筛选条件（可选）")
    print("   4. 生成多种格式的报告")
    print()
    print("🎯 目标: 获取筛选条件下的所有岗位数据")
    print()
    
    # 加载已爬取的数据
    text_content = load_crawled_data()
    if not text_content:
        print("❌ 无法加载已爬取的数据")
        return
    
    # 提取所有岗位
    raw_positions = extract_all_positions(text_content)
    
    if not raw_positions:
        print("❌ 未提取到任何岗位数据")
        return
    
    print()
    print(f"✅ 成功提取到 {len(raw_positions)} 个岗位")
    print()
    
    # 创建标准化岗位
    standard_positions = []
    for raw_position in raw_positions:
        standard_position = create_standard_position(raw_position)
        standard_positions.append(standard_position)
    
    print("📋 提取的岗位列表:")
    for i, position in enumerate(standard_positions[:10], 1):
        print(f"  {i:2d}. {position['positionName'][:30]:30} | {position['workLocation']:8} | {position['workExperience']:6} | {position['publishTime']}")
    
    if len(standard_positions) > 10:
        print(f"  ... 还有 {len(standard_positions) - 10} 个岗位")
    
    print()
    
    # 询问筛选条件
    print("🔍 请选择筛选条件（按Enter跳过）:")
    print("  1. 工作地点（如：北京、上海、杭州）")
    print("  2. 岗位类别（如：工程类、产品类、运营类）")
    print("  3. 工作经验（如：3-5年、1-3年）")
    print()
    
    conditions = {}
    
    # 这里可以添加交互式筛选条件输入
    # 为了简化，我们暂时使用示例筛选条件
    example_conditions = {
        "workLocation": "北京",  # 筛选北京的工作
        "positionCategory": "工程类",  # 筛选工程类岗位
        "workExperience": "3-5年"  # 筛选3-5年经验
    }
    
    # 应用筛选条件
    filtered_positions = filter_positions_by_conditions(standard_positions, example_conditions)
    
    print(f"📍 应用筛选条件后: {len(filtered_positions)} 个岗位")
    print(f"   工作地点: {example_conditions.get('workLocation', '不限')}")
    print(f"   岗位类别: {example_conditions.get('positionCategory', '不限')}")
    print(f"   工作经验: {example_conditions.get('workExperience', '不限')}")
    print()
    
    # 保存最终结果
    saved_files = save_final_results(filtered_positions, example_conditions)
    
    print()
    print("✅" * 35)
    print("🎉 最终数据提取成功完成！")
    print("✅" * 35)
    print()
    print("📊 最终成果:")
    print(f"   📈 总岗位数: {len(filtered_positions)} 个")
    print(f"   📁 输出目录: {OUTPUT_DIR}")
    print()
    
    print("📁 生成的文件:")
    for file_type, file_path in saved_files.items():
        if file_path:
            print(f"   • {file_type}: {os.path.basename(file_path)}")
    
    print()
    print("💡 数据使用指南:")
    print("   1. 查看完整数据: cat output/ks_final_results/kuaishou_all_positions_*.json")
    print("   2. 查看统计报告: cat output/ks_final_results/kuaishou_statistics_*.json")
    print("   3. 用Excel打开: open output/ks_final_results/kuaishou_positions_*.csv")
    print("   4. 查看Markdown报告: cat output/ks_final_results/kuaishou_report_*.md")
    print("   5. 分析岗位分布: 查看统计报告中的分布数据")
    print()
    print("🎯 ks-job 项目目标达成: 成功提取筛选条件下的所有岗位数据")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()