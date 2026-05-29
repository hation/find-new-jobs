#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚂蚁国际招聘API响应数据分析脚本
基于实际的API响应数据进行结构分析
版本: v1.0.0
创建时间: 2026-05-22
"""

import json
import sys
from pathlib import Path
from collections import Counter

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def analyze_response_structure(response_data):
    """分析响应数据结构"""
    print("\n" + "="*70)
    print("🔍 蚂蚁国际招聘API响应数据分析")
    print("="*70)
    
    if not isinstance(response_data, dict):
        print(f"❌ 响应数据不是字典类型: {type(response_data)}")
        return
    
    # 1. 分析顶层结构
    print("📊 顶层字段分析:")
    for key, value in response_data.items():
        value_type = type(value).__name__
        if isinstance(value, (list, dict)):
            print(f"  📦 {key}: {value_type} (长度: {len(value) if isinstance(value, list) else '字典'})")
        else:
            print(f"  📄 {key}: {value_type} = {value}")
    
    # 2. 分析分页信息
    print("\n📊 分页信息:")
    pagination_fields = ["totalCount", "pageSize", "currentPage"]
    for field in pagination_fields:
        if field in response_data:
            print(f"  📄 {field}: {response_data[field]}")
    
    # 3. 分析岗位数据
    if "content" in response_data and isinstance(response_data["content"], list):
        positions = response_data["content"]
        print(f"\n📊 岗位数据统计:")
        print(f"  📋 岗位数量: {len(positions)}")
        
        if positions:
            # 分析第一个岗位的完整结构
            first_position = positions[0]
            print(f"\n🔍 第一个岗位的完整字段结构:")
            analyze_position_structure(first_position)
            
            # 分析所有岗位的字段分布
            print(f"\n📊 所有岗位字段分布统计:")
            analyze_field_distribution(positions)
            
            # 分析分类信息
            print(f"\n🎯 分类信息分析:")
            analyze_categories(positions)
            
            # 分析工作地点分布
            print(f"\n📍 工作地点分布:")
            analyze_locations(positions)
            
            # 分析经验要求分布
            print(f"\n📈 经验要求分布:")
            analyze_experience_requirements(positions)
            
            # 分析学历要求分布
            print(f"\n🎓 学历要求分布:")
            analyze_degree_requirements(positions)
            
            # 分析发布时间分布
            print(f"\n📅 发布时间分析:")
            analyze_publish_times(positions)
    
    # 4. 保存分析结果
    save_analysis_results(response_data)

def analyze_position_structure(position):
    """分析单个岗位的结构"""
    if not isinstance(position, dict):
        return
    
    print("  📋 字段详情:")
    for key, value in position.items():
        value_type = type(value).__name__
        
        if value is None:
            print(f"    • {key}: None")
        elif isinstance(value, str):
            # 字符串长度限制
            display_value = value[:50] + "..." if len(value) > 50 else value
            print(f"    • {key}: str = \"{display_value}\"")
        elif isinstance(value, (int, float, bool)):
            print(f"    • {key}: {value_type} = {value}")
        elif isinstance(value, list):
            if value:
                first_item = value[0]
                if isinstance(first_item, str):
                    sample = value[:3] if len(value) > 3 else value
                    print(f"    • {key}: list[{len(value)}] = {sample}")
                else:
                    print(f"    • {key}: list[{len(value)}] (复杂类型)")
            else:
                print(f"    • {key}: list[0] (空列表)")
        elif isinstance(value, dict):
            print(f"    • {key}: dict (键: {list(value.keys())})")
        else:
            print(f"    • {key}: {value_type}")

def analyze_field_distribution(positions):
    """分析字段分布"""
    field_counter = Counter()
    
    for position in positions:
        if isinstance(position, dict):
            for field in position.keys():
                field_counter[field] += 1
    
    total_positions = len(positions)
    print("  📊 字段出现频率:")
    for field, count in field_counter.most_common():
        percentage = (count / total_positions) * 100
        print(f"    • {field}: {count}/{total_positions} ({percentage:.1f}%)")

def analyze_categories(positions):
    """分析分类信息"""
    category_counter = Counter()
    
    for position in positions:
        if isinstance(position, dict) and "categories" in position:
            categories = position["categories"]
            if isinstance(categories, list):
                for category in categories:
                    category_counter[category] += 1
    
    print("  📊 岗位分类分布:")
    for category, count in category_counter.most_common(10):
        print(f"    • {category}: {count}个岗位")
    
    if len(category_counter) > 10:
        print(f"    • ... 共{len(category_counter)}种分类")

def analyze_locations(positions):
    """分析工作地点分布"""
    location_counter = Counter()
    
    for position in positions:
        if isinstance(position, dict) and "workLocations" in position:
            locations = position["workLocations"]
            if isinstance(locations, list):
                for location in locations:
                    location_counter[location] += 1
    
    print("  📊 工作地点分布:")
    for location, count in location_counter.most_common(10):
        print(f"    • {location}: {count}个岗位")
    
    if len(location_counter) > 10:
        print(f"    • ... 共{len(location_counter)}个工作地点")

def analyze_experience_requirements(positions):
    """分析经验要求分布"""
    experience_counter = Counter()
    
    for position in positions:
        if isinstance(position, dict) and "experience" in position:
            experience = position["experience"]
            if isinstance(experience, dict):
                from_years = experience.get("from")
                to_years = experience.get("to")
                
                if from_years is not None:
                    if to_years is not None:
                        exp_range = f"{from_years}-{to_years}年"
                    else:
                        exp_range = f"{from_years}+年"
                    experience_counter[exp_range] += 1
                elif to_years is not None:
                    experience_counter[f"≤{to_years}年"] += 1
                else:
                    experience_counter["经验不限"] += 1
            else:
                experience_counter["无经验要求"] += 1
        else:
            experience_counter["未指定经验"] += 1
    
    print("  📊 经验要求分布:")
    for exp_range, count in experience_counter.most_common():
        print(f"    • {exp_range}: {count}个岗位")

def analyze_degree_requirements(positions):
    """分析学历要求分布"""
    degree_counter = Counter()
    
    for position in positions:
        if isinstance(position, dict) and "degree" in position:
            degree = position["degree"]
            if degree:
                degree_counter[degree] += 1
            else:
                degree_counter["未指定"] += 1
        else:
            degree_counter["无学历要求"] += 1
    
    print("  📊 学历要求分布:")
    for degree, count in degree_counter.most_common():
        # 翻译学历要求
        degree_map = {
            "bachelor": "本科",
            "master": "硕士",
            "doctor": "博士",
            "college": "大专",
            "high_school": "高中"
        }
        display_degree = degree_map.get(degree, degree)
        print(f"    • {display_degree}: {count}个岗位")

def analyze_publish_times(positions):
    """分析发布时间分布"""
    from datetime import datetime
    
    publish_times = []
    
    for position in positions:
        if isinstance(position, dict) and "publishTime" in position:
            publish_time = position["publishTime"]
            if publish_time:
                try:
                    # 解析ISO格式时间
                    dt = datetime.fromisoformat(publish_time.replace('Z', '+00:00'))
                    publish_times.append(dt)
                except:
                    pass
    
    if publish_times:
        # 按日期分组
        date_counter = Counter()
        for dt in publish_times:
            date_str = dt.strftime("%Y-%m-%d")
            date_counter[date_str] += 1
        
        print("  📊 按发布日期分布:")
        for date_str, count in date_counter.most_common(5):
            print(f"    • {date_str}: {count}个岗位")
        
        # 计算平均发布时间间隔
        if len(publish_times) > 1:
            publish_times.sort()
            time_diffs = []
            for i in range(1, len(publish_times)):
                diff = (publish_times[i] - publish_times[i-1]).total_seconds() / 3600  # 小时
                time_diffs.append(diff)
            
            avg_diff = sum(time_diffs) / len(time_diffs)
            print(f"  ⏱️  平均发布间隔: {avg_diff:.1f}小时")

def save_analysis_results(response_data):
    """保存分析结果"""
    output_dir = project_root / "output" / "analysis"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 保存完整的响应数据
    full_response_file = output_dir / "full_response.json"
    with open(full_response_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 完整响应数据已保存到: {full_response_file}")
    
    # 2. 保存字段映射配置建议
    if "content" in response_data and isinstance(response_data["content"], list) and response_data["content"]:
        first_position = response_data["content"][0]
        
        mapping_suggestion = {
            "field_mapping": {},
            "pagination": {
                "total": response_data.get("totalCount"),
                "page_size": response_data.get("pageSize"),
                "current_page": response_data.get("currentPage")
            },
            "sample_position": extract_sample_structure(first_position)
        }
        
        # 生成字段映射建议
        for key in first_position.keys():
            mapping_suggestion["field_mapping"][key] = {
                "type": type(first_position[key]).__name__,
                "required": True if first_position[key] is not None else False,
                "sample": str(first_position[key])[:100] if first_position[key] else None
            }
        
        mapping_file = output_dir / "field_mapping_suggestion.json"
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping_suggestion, f, ensure_ascii=False, indent=2)
        print(f"💾 字段映射建议已保存到: {mapping_file}")
        
        # 3. 保存统计报告
        stats_report = generate_stats_report(response_data)
        stats_file = output_dir / "statistics_report.md"
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write(stats_report)
        print(f"💾 统计报告已保存到: {stats_file}")

def extract_sample_structure(position, max_depth=2, current_depth=0):
    """提取样本结构"""
    if current_depth >= max_depth:
        return "..."
    
    if isinstance(position, dict):
        result = {}
        for key, value in position.items():
            if isinstance(value, (dict, list)):
                result[key] = extract_sample_structure(value, max_depth, current_depth + 1)
            else:
                if value is None:
                    result[key] = None
                elif isinstance(value, str):
                    result[key] = value[:50] + "..." if len(value) > 50 else value
                else:
                    result[key] = value
        return result
    elif isinstance(position, list):
        if position:
            return [extract_sample_structure(position[0], max_depth, current_depth + 1)]
        else:
            return []
    else:
        return position

def generate_stats_report(response_data):
    """生成统计报告"""
    report = "# 📊 蚂蚁国际招聘API响应数据统计报告\n\n"
    report += f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"**数据来源**: 蚂蚁国际招聘API\n\n"
    
    # 基本信息
    report += "## 📋 基本信息\n\n"
    report += f"- **总岗位数**: {response_data.get('totalCount', 'N/A')}\n"
    report += f"- **当前页岗位数**: {len(response_data.get('content', []))}\n"
    report += f"- **页大小**: {response_data.get('pageSize', 'N/A')}\n"
    report += f"- **当前页码**: {response_data.get('currentPage', 'N/A')}\n"
    report += f"- **Trace ID**: {response_data.get('traceId', 'N/A')}\n"
    report += f"- **API状态**: {response_data.get('success', 'N/A')} ({response_data.get('errorMsg', 'N/A')})\n\n"
    
    # 如果有岗位数据，添加详细分析
    if "content" in response_data and response_data["content"]:
        positions = response_data["content"]
        report += "## 📊 数据质量分析\n\n"
        
        # 字段完整性分析
        report += "### 字段完整性\n\n"
        field_stats = {}
        for position in positions:
            for field in position.keys():
                if field not in field_stats:
                    field_stats[field] = 0
                if position[field] is not None:
                    field_stats[field] += 1
        
        report += "| 字段名 | 出现次数 | 完整率 |\n"
        report += "|--------|----------|--------|\n"
        for field, count in sorted(field_stats.items()):
            completeness = (count / len(positions)) * 100
            report += f"| {field} | {count}/{len(positions)} | {completeness:.1f}% |\n"
        report += "\n"
        
        # 数据样本
        report += "## 🔍 数据样本\n\n"
        report += "### 第一个岗位的完整数据\n\n"
        report += "```json\n"
        report += json.dumps(positions[0], ensure_ascii=False, indent=2)
        report += "\n```\n\n"
        
        # 配置建议
        report += "## ⚙️ 配置建议\n\n"
        report += "基于分析结果，建议更新以下配置：\n\n"
        report += "### 1. 字段映射配置\n"
        report += "```json\n"
        report += "{\n"
        report += "  \"position_id\": \"id\",\n"
        report += "  \"position_name\": \"name\",\n"
        report += "  \"work_locations\": \"workLocations\",\n"
        report += "  \"department\": \"department\",\n"
        report += "  \"degree\": \"degree\",\n"
        report += "  \"experience\": \"experience\",\n"
        report += "  \"requirement\": \"requirement\",\n"
        report += "  \"description\": \"description\",\n"
        report += "  \"publish_time\": \"publishTime\"\n"
        report += "}\n"
        report += "```\n\n"
        
        report += "### 2. 分页配置\n"
        report += "```json\n"
        report += "{\n"
        report += "  \"page_param\": \"pageNo\",\n"
        report += "  \"size_param\": \"pageSize\",\n"
        report += "  \"default_page_size\": 10\n"
        report += "}\n"
        report += "```\n\n"
        
        report += "### 3. 响应结构配置\n"
        report += "```json\n"
        report += "{\n"
        report += "  \"success_field\": \"success\",\n"
        report += "  \"data_field\": \"content\",\n"
        report += "  \"total_field\": \"totalCount\",\n"
        report += "  \"page_field\": \"currentPage\",\n"
        report += "  \"page_size_field\": \"pageSize\"\n"
        report += "}\n"
        report += "```\n"
    
    return report

def main():
    """主函数"""
    print("="*70)
    print("🚀 蚂蚁国际招聘API响应数据分析工具")
    print("="*70)
    
    # 这里可以加载保存的响应文件，或者直接使用提供的响应数据
    # 为了演示，我们创建一个示例响应数据
    sample_response = {
        "success": True,
        "errorMsg": "成功",
        "errorCode": "success",
        "content": [
            {
                "bucket": "DEFAULT",
                "positionUrl": "",
                "id": 1944010,
                "name": "OceanBase-Business Development Manager-Thailand-OceanBase",
                "categories": ["BD-销售型BD"],
                "publishTime": "2026-05-22T03:04:01.000+00:00",
                "workLocations": ["曼谷"],
                "requirement": "1.\tPassion and energy...",
                "description": "1.\tMeet sales quota...",
                "experience": {"from": 6, "to": None},
                "degree": "bachelor",
                "department": "OceanBase",
                "code": "GP1944010",
                "tags": ["NEW"],
                "tid": "219feabc17794206648957890e453b"
            }
        ],
        "traceId": "219feabc17794206648957890e453b",
        "totalCount": 965,
        "pageSize": 10,
        "currentPage": 1
    }
    
    print("📊 使用示例数据进行分析...")
    analyze_response_structure(sample_response)
    
    print("\n" + "="*70)
    print("🎉 分析完成！")
    print("="*70)
    print("\n📋 下一步:")
    print("  1. 检查 output/analysis/ 目录下的分析结果")
    print("  2. 根据分析结果更新 config/api_auth.json")
    print("  3. 测试实际的API连接")
    print("  4. 验证字段映射是否正确")

if __name__ == "__main__":
    from datetime import datetime
    main()