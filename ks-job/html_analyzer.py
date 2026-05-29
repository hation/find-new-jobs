#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘HTML分析器
从已保存的HTML文件中提取所有岗位数据
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🔍 快手招聘HTML分析器")
print("=" * 80)
print("从已保存的HTML文件中提取所有岗位数据")
print()

# 输入HTML文件
HTML_FILE = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/ks-job/output/ks_simple_full/ks_page_html_20260522_181928.html"

# 输出目录
OUTPUT_DIR = "output/ks_html_analysis"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/html_analyzer.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


def load_html_file() -> Optional[str]:
    """加载HTML文件"""
    if not os.path.exists(HTML_FILE):
        log(f"❌ HTML文件不存在: {HTML_FILE}")
        return None
    
    try:
        log(f"📄 加载HTML文件: {HTML_FILE}")
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        log(f"✅ HTML文件加载成功，大小: {len(html_content)} 字符")
        return html_content
    except Exception as e:
        log(f"❌ 加载HTML文件失败: {e}")
        return None


def extract_positions_from_html(html: str) -> List[Dict[str, Any]]:
    """从HTML中提取岗位数据"""
    log("🔍 开始从HTML中提取岗位数据...")
    
    positions = []
    
    if not html:
        return positions
    
    # 方法1: 查找包含岗位信息的script标签
    log("🔍 方法1: 查找包含岗位信息的script标签...")
    
    # 快手招聘可能将数据存储在window.__INITIAL_STATE__或类似变量中
    script_patterns = [
        r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
        r'var\s+positions\s*=\s*(\[.*?\]);',
        r'"positions"\s*:\s*(\[.*?\])',
        r'"list"\s*:\s*(\[.*?\])',
        r'data:\s*({.*?})',
        r'props:\s*({.*?})',
        r'initialState:\s*({.*?})',
        r'pageProps:\s*({.*?})'
    ]
    
    for pattern in script_patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        if matches:
            log(f"✅ 找到匹配模式: {pattern[:30]}...")
            log(f"   找到 {len(matches)} 个匹配")
            
            for i, match in enumerate(matches[:5]):  # 只检查前5个匹配
                try:
                    data = json.loads(match)
                    log(f"   匹配 {i+1}: JSON解析成功，类型: {type(data)}")
                    
                    # 递归查找岗位数据
                    found_positions = find_positions_in_data(data, f"pattern_{i}")
                    if found_positions:
                        log(f"   🎉 从匹配 {i+1} 中找到 {len(found_positions)} 个岗位")
                        positions.extend(found_positions)
                except json.JSONDecodeError as e:
                    log(f"   匹配 {i+1}: JSON解析失败: {e}")
                    continue
                except Exception as e:
                    log(f"   匹配 {i+1}: 处理失败: {e}")
                    continue
    
    # 方法2: 查找包含岗位信息的div/span元素
    log("🔍 方法2: 查找包含岗位信息的HTML元素...")
    
    # 快手招聘的岗位可能以特定格式显示
    html_patterns = [
        # 格式: <div>Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22</div>
        r'<[^>]+>([^<]{20,100}?工程师[^<]{10,80}?\d{4}\.\d{2}\.\d{2})<',
        
        # 格式: <span>岗位名称</span><span>工作地点</span><span>工作经验</span>
        r'<[^>]+>([^<>{5,30}?)<[^>]+>([^<>{2,10}?)<[^>]+>(\d+-\d+年)<[^>]+>(\d{4}\.\d{2}\.\d{2})<',
        
        # 包含【】的格式
        r'>([^>]{10,40}?)【([^】]{2,20}?)】([^>]{5,30}?)(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})<',
    ]
    
    for pattern in html_patterns:
        matches = re.findall(pattern, html)
        if matches:
            log(f"✅ HTML模式匹配: {pattern[:50]}...")
            log(f"   找到 {len(matches)} 个匹配")
            
            for match in matches:
                if isinstance(match, tuple):
                    # 元组匹配
                    position_data = {
                        "rawMatch": str(match),
                        "extractionMethod": "html_pattern",
                        "pattern": pattern[:50]
                    }
                    
                    # 根据匹配长度解析
                    if len(match) >= 1:
                        position_data["positionName"] = match[0] if len(match) > 0 else ""
                    if len(match) >= 2:
                        position_data["positionCategory"] = match[1] if len(match) > 1 else ""
                    if len(match) >= 3:
                        position_data["workLocation"] = match[2] if len(match) > 2 else ""
                    if len(match) >= 4:
                        position_data["workExperience"] = match[3] if len(match) > 3 else ""
                    if len(match) >= 5:
                        position_data["publishTime"] = match[4] if len(match) > 4 else ""
                    
                    positions.append(position_data)
                else:
                    # 字符串匹配
                    position_data = {
                        "rawText": match,
                        "extractionMethod": "html_pattern_single",
                        "pattern": pattern[:50]
                    }
                    positions.append(position_data)
    
    # 方法3: 查找所有包含"工程师"、"开发"等关键词的文本
    log("🔍 方法3: 查找包含岗位关键词的文本...")
    
    # 提取所有文本内容（去除HTML标签）
    text_content = re.sub(r'<[^>]+>', ' ', html)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    # 查找包含岗位关键词的行
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理'
    ]
    
    # 分割文本为行
    lines = text_content.split('. ')  # 按句子分割
    
    for line in lines:
        line = line.strip()
        if len(line) < 30:
            continue
        
        # 检查是否包含岗位关键词
        has_keyword = any(keyword in line for keyword in position_keywords)
        has_date = re.search(r'\d{4}\.\d{2}\.\d{2}', line)
        
        if has_keyword and has_date:
            # 提取岗位信息
            position_data = extract_from_text_line(line)
            if position_data:
                position_data["extractionMethod"] = "text_analysis"
                positions.append(position_data)
    
    log(f"📊 从HTML中总共提取到 {len(positions)} 个岗位候选")
    return positions


def find_positions_in_data(data: Any, path: str = "") -> List[Dict[str, Any]]:
    """在数据中递归查找岗位信息"""
    positions = []
    
    if isinstance(data, dict):
        # 检查这个字典是否包含岗位信息
        if is_position_data(data):
            positions.append({
                "data": data,
                "path": path,
                "type": "position_object"
            })
        
        # 递归检查所有值
        for key, value in data.items():
            positions.extend(find_positions_in_data(value, f"{path}.{key}"))
    
    elif isinstance(data, list):
        # 检查列表中的每个元素
        for i, item in enumerate(data):
            positions.extend(find_positions_in_data(item, f"{path}[{i}]"))
    
    return positions


def is_position_data(data: Dict[str, Any]) -> bool:
    """检查数据是否包含岗位信息"""
    if not isinstance(data, dict):
        return False
    
    # 检查是否包含岗位相关的字段
    position_fields = ['name', 'title', 'positionName', 'jobTitle', 'position']
    location_fields = ['location', 'workLocation', 'city', 'address']
    experience_fields = ['experience', 'workExperience', 'years']
    time_fields = ['publishTime', 'updateTime', 'createTime']
    
    has_position = any(field in data for field in position_fields)
    has_location = any(field in data for field in location_fields)
    has_experience = any(field in data for field in experience_fields)
    has_time = any(field in data for field in time_fields)
    
    # 如果有岗位名称和其他至少一个字段，认为是岗位数据
    return has_position and (has_location or has_experience or has_time)


def extract_from_text_line(line: str) -> Optional[Dict[str, Any]]:
    """从文本行中提取岗位信息"""
    # 快手招聘的典型格式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    result = {
        "rawText": line[:200],
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": ""
    }
    
    # 1. 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
    if time_match:
        result["publishTime"] = time_match.group(1)
    
    # 2. 提取工作经验
    exp_match = re.search(r'(\d+-\d+年)', line)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    
    # 3. 提取工作地点（城市名）
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安']
    for city in cities:
        if city in line:
            result["workLocation"] = city
            break
    
    # 4. 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', line)
    if category_match:
        result["positionCategory"] = category_match.group(1)
    
    # 5. 提取岗位名称（【】之前的部分）
    if '【' in line:
        before_bracket = line.split('【')[0]
        result["positionName"] = before_bracket.strip()
    else:
        # 尝试提取包含关键词的部分
        for keyword in ['工程师', '开发', '产品', '运营', '经理']:
            if keyword in line:
                start = max(0, line.find(keyword) - 20)
                end = min(len(line), line.find(keyword) + 10)
                result["positionName"] = line[start:end].strip()
                break
    
    # 只有提取到足够信息才返回
    if result["positionName"] or result["workLocation"] or result["workExperience"]:
        return result
    
    return None


def create_standard_position(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_HTML_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
    # 提取信息
    position_name = raw_position.get("positionName", "") or raw_position.get("data", {}).get("name", "") or raw_position.get("data", {}).get("title", "")
    work_location = raw_position.get("workLocation", "") or raw_position.get("data", {}).get("location", "") or raw_position.get("data", {}).get("workLocation", "")
    work_experience = raw_position.get("workExperience", "") or raw_position.get("data", {}).get("experience", "") or raw_position.get("data", {}).get("workExperience", "")
    publish_time = raw_position.get("publishTime", "") or raw_position.get("data", {}).get("publishTime", "") or raw_position.get("data", {}).get("updateTime", "")
    
    # 标准化时间格式
    if publish_time:
        publish_time = publish_time.replace('.', '-').replace('/', '-')
    else:
        publish_time = datetime.now().strftime("%Y-%m-%d")
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": position_name or "快手招聘岗位",
        "workLocation": work_location or "全国",
        "positionCategory": raw_position.get("positionCategory", ""),
        "publishTime": publish_time,
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position_id}",
        "department": "",
        "educationRequirement": "",
        "workExperience": work_experience,
        "jobResponsibilities": "",
        "jobRequirements": "",
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "html_analysis",
        "source": "kuaishou_html",
        
        # 提取信息
        "extractionInfo": {
            "method": raw_position.get("extractionMethod", ""),
            "path": raw_position.get("path", ""),
            "type": raw_position.get("type", "")
        }
    }


def save_analysis_results(positions: List[Dict[str, Any]]) -> Dict[str, str]:
    """保存分析结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存所有提取的原始数据
    raw_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_raw_data_{timestamp}.json")
    
    raw_data = {
        "metadata": {
            "analysisTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "htmlFile": HTML_FILE,
            "totalPositions": len(positions),
            "source": "html_analysis"
        },
        "positions": positions
    }
    
    try:
        with open(raw_data_file, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存原始数据: {raw_data_file}")
    except Exception as e:
        log(f"❌ 保存原始数据失败: {e}")
        raw_data_file = ""
    
    # 2. 保存标准化岗位数据
    standard_positions = []
    for raw_position in positions:
        standard_position = create_standard_position(raw_position)
        standard_positions.append(standard_position)
    
    standard_file = os.path.join(OUTPUT_DIR, f"kuaishou_standard_positions_{timestamp}.json")
    
    standard_data = {
        "metadata": {
            "processTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(standard_positions),
            "source": "html_analysis_standardized"
        },
        "positions": standard_positions
    }
    
    try:
        with open(standard_file, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存标准化数据: {standard_file}")
    except Exception as e:
        log(f"❌ 保存标准化数据失败: {e}")
        standard_file = ""
    
    # 3. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_stats_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in standard_positions]
    work_locations = []
    for p in standard_positions:
        location = p.get("workLocation", "")
        if location and location not in work_locations:
            work_locations.append(location)
    
    stats_data = {
        "metadata": {
            "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(standard_positions),
            "uniquePositionNames": len(set([n for n in position_names if n])),
            "uniqueWorkLocations": len(work_locations)
        },
        "summary": {
            "positionNames": list(set([n for n in position_names if n]))[:20],
            "workLocations": work_locations[:20]
        },
        "extractionMethods": {
            "total": len(positions),
            "byMethod": {}
        }
    }
    
    # 统计提取方法
    for position in positions:
        method = position.get("extractionMethod", "unknown")
        stats_data["extractionMethods"]["byMethod"][method] = stats_data["extractionMethods"]["byMethod"].get(method, 0) + 1
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    return {
        "raw_data": raw_data_file,
        "standard_data": standard_file,
        "statistics": stats_file
    }


def main():
    """主函数"""
    print()
    print("📋 HTML分析流程:")
    print("   1. 加载已保存的HTML文件")
    print("   2. 分析HTML结构，查找岗位数据")
    print("   3. 使用多种方法提取岗位信息")
    print("   4. 标准化提取的数据")
    print("   5. 保存分析结果")
    print()
    
    # 加载HTML文件
    html_content = load_html_file()
    if not html_content:
        print("❌ 无法加载HTML文件")
        return
    
    # 提取岗位数据
    positions = extract_positions_from_html(html_content)
    
    if not positions:
        print("❌ 未从HTML中提取到任何岗位数据")
        return
    
    print(f"✅ 从HTML中提取到 {len(positions)} 个岗位候选")
    print()
    
    # 保存分析结果
    saved_files = save_analysis_results(positions)
    
    print()
    print("📊 分析完成!")
    print(f"   输出目录: {OUTPUT_DIR}")
    
    for file_type, file_path in saved_files.items():
        if file_path:
            print(f"   • {file_type}: {os.path.basename(file_path)}")
    
    print()
    print("💡 下一步:")
    print("   1. 查看原始数据: cat output/ks_html_analysis/kuaishou_raw_data_*.json")
    print("   2. 查看标准化数据: cat output/ks_html_analysis/kuaishou_standard_positions_*.json")
    print("   3. 查看统计报告: cat output/ks_html_analysis/kuaishou_stats_*.json")
    print("   4. 基于分析结果优化爬取策略")
    print()
    
    # 显示一些示例数据
    if positions:
        print("📄 示例数据（前3个）:")
        for i, position in enumerate(positions[:3]):
            print(f"   {i+1}. {position.get('positionName', position.get('rawText', '')[:50])}...")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()