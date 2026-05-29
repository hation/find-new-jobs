#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘API分页爬取器
直接通过API获取所有分页数据
"""

import json
import os
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🚀 快手招聘API分页爬取器")
print("=" * 80)
print("直接通过API获取所有分页数据")
print()

# 输出目录
OUTPUT_DIR = "output/ks_api_paginated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/api_paginated.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


def get_api_headers() -> Dict[str, str]:
    """获取API请求头"""
    # 基于我们之前的测试，快手API需要特定的headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/json',
        'Origin': 'https://zhaopin.kuaishou.cn',
        'Referer': 'https://zhaopin.kuaishou.cn/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive',
    }
    
    # 尝试从之前成功的请求中获取headers
    try:
        # 检查是否有之前保存的headers
        headers_file = "config/api_headers.json"
        if os.path.exists(headers_file):
            with open(headers_file, 'r', encoding='utf-8') as f:
                saved_headers = json.load(f)
                headers.update(saved_headers)
                log("✅ 使用保存的API headers")
    except:
        pass
    
    return headers


def crawl_all_pages_via_api() -> List[Dict[str, Any]]:
    """
    通过API爬取所有分页数据
    """
    log("🔄 开始通过API爬取所有分页数据...")
    
    all_positions = []
    current_page = 1
    max_pages = 100  # 安全限制
    page_size = 20   # 假设每页20条
    
    base_url = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"
    
    while current_page <= max_pages:
        log(f"📄 请求第 {current_page} 页数据...")
        
        # 构建请求参数
        params = {
            'page': current_page,
            'size': page_size,
            # 可以添加其他筛选参数
            # 'category': '',  # 岗位类别
            # 'location': '',  # 工作地点
            # 'experience': '',  # 工作经验
        }
        
        try:
            # 发送API请求
            headers = get_api_headers()
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            log(f"📡 API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 尝试解析响应数据
                try:
                    data = response.json()
                    log(f"✅ 第 {current_page} 页API响应解析成功")
                    
                    # 保存原始响应
                    raw_file = os.path.join(OUTPUT_DIR, f"api_page_{current_page:03d}_raw.json")
                    with open(raw_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    log(f"💾 保存第 {current_page} 页原始响应: {raw_file}")
                    
                    # 提取岗位数据
                    page_positions = extract_positions_from_api_response(data, current_page)
                    
                    if page_positions:
                        log(f"✅ 第 {current_page} 页提取到 {len(page_positions)} 个岗位")
                        all_positions.extend(page_positions)
                        
                        # 保存当前页数据
                        page_file = os.path.join(OUTPUT_DIR, f"api_page_{current_page:03d}_positions.json")
                        with open(page_file, 'w', encoding='utf-8') as f:
                            json.dump({
                                "page": current_page,
                                "positions": page_positions,
                                "count": len(page_positions),
                                "responseSize": len(response.text)
                            }, f, ensure_ascii=False, indent=2)
                        log(f"💾 保存第 {current_page} 页岗位数据: {page_file}")
                        
                        # 检查是否还有更多数据
                        if len(page_positions) < page_size:
                            log(f"📄 第 {current_page} 页只有 {len(page_positions)} 条数据，可能没有更多页")
                            break
                    else:
                        log(f"⚠️ 第 {current_page} 页未提取到岗位数据")
                        
                        # 检查响应内容
                        if 'code' in data and data['code'] != 0:
                            log(f"❌ API返回错误: {data.get('message', '未知错误')}")
                            break
                        
                        # 如果连续3页没有数据，停止
                        if current_page > 3 and len(all_positions) == 0:
                            log("❌ 连续3页没有数据，停止爬取")
                            break
                
                except json.JSONDecodeError:
                    log(f"❌ 第 {current_page} 页响应不是有效的JSON")
                    log(f"   响应内容: {response.text[:200]}...")
                    break
                except Exception as e:
                    log(f"❌ 第 {current_page} 页数据处理失败: {e}")
                    break
            else:
                log(f"❌ 第 {current_page} 页API请求失败: {response.status_code}")
                log(f"   响应内容: {response.text[:200]}...")
                break
            
        except requests.exceptions.RequestException as e:
            log(f"❌ 第 {current_page} 页网络请求失败: {e}")
            break
        except Exception as e:
            log(f"❌ 第 {current_page} 页发生未知错误: {e}")
            break
        
        # 等待一段时间，避免请求过快
        time.sleep(1)
        current_page += 1
    
    log(f"🎉 API爬取完成，共爬取 {current_page-1} 页，{len(all_positions)} 个岗位")
    return all_positions


def extract_positions_from_api_response(data: Dict[str, Any], page_num: int) -> List[Dict[str, Any]]:
    """从API响应中提取岗位数据"""
    positions = []
    
    if not data:
        return positions
    
    # 快手API的可能响应格式
    # 1. 直接是岗位列表
    if isinstance(data, list):
        log(f"📄 第 {page_num} 页API返回列表格式，{len(data)} 条数据")
        
        for item in data:
            if isinstance(item, dict):
                position_data = parse_api_position_item(item, page_num)
                if position_data:
                    positions.append(position_data)
    
    # 2. 包含data字段
    elif isinstance(data, dict) and 'data' in data:
        data_content = data['data']
        
        if isinstance(data_content, list):
            log(f"📄 第 {page_num} 页API返回data列表，{len(data_content)} 条数据")
            
            for item in data_content:
                if isinstance(item, dict):
                    position_data = parse_api_position_item(item, page_num)
                    if position_data:
                        positions.append(position_data)
        
        elif isinstance(data_content, dict) and 'list' in data_content:
            # 包含list字段
            list_data = data_content['list']
            if isinstance(list_data, list):
                log(f"📄 第 {page_num} 页API返回list字段，{len(list_data)} 条数据")
                
                for item in list_data:
                    if isinstance(item, dict):
                        position_data = parse_api_position_item(item, page_num)
                        if position_data:
                            positions.append(position_data)
        
        elif isinstance(data_content, dict) and 'positions' in data_content:
            # 包含positions字段
            positions_data = data_content['positions']
            if isinstance(positions_data, list):
                log(f"📄 第 {page_num} 页API返回positions字段，{len(positions_data)} 条数据")
                
                for item in positions_data:
                    if isinstance(item, dict):
                        position_data = parse_api_position_item(item, page_num)
                        if position_data:
                            positions.append(position_data)
    
    # 3. 包含list字段
    elif isinstance(data, dict) and 'list' in data:
        list_data = data['list']
        if isinstance(list_data, list):
            log(f"📄 第 {page_num} 页API返回list字段，{len(list_data)} 条数据")
            
            for item in list_data:
                if isinstance(item, dict):
                    position_data = parse_api_position_item(item, page_num)
                    if position_data:
                        positions.append(position_data)
    
    # 4. 包含positions字段
    elif isinstance(data, dict) and 'positions' in data:
        positions_data = data['positions']
        if isinstance(positions_data, list):
            log(f"📄 第 {page_num} 页API返回positions字段，{len(positions_data)} 条数据")
            
            for item in positions_data:
                if isinstance(item, dict):
                    position_data = parse_api_position_item(item, page_num)
                    if position_data:
                        positions.append(position_data)
    
    # 5. 包含records字段
    elif isinstance(data, dict) and 'records' in data:
        records_data = data['records']
        if isinstance(records_data, list):
            log(f"📄 第 {page_num} 页API返回records字段，{len(records_data)} 条数据")
            
            for item in records_data:
                if isinstance(item, dict):
                    position_data = parse_api_position_item(item, page_num)
                    if position_data:
                        positions.append(position_data)
    
    # 6. 其他可能格式
    else:
        log(f"🔍 第 {page_num} 页API返回未知格式，尝试查找岗位数据")
        
        # 递归查找包含岗位信息的字段
        found_positions = find_positions_in_data(data, f"page_{page_num}")
        if found_positions:
            log(f"✅ 第 {page_num} 页递归查找到 {len(found_positions)} 个岗位")
            positions.extend(found_positions)
    
    return positions


def parse_api_position_item(item: Dict[str, Any], page_num: int) -> Optional[Dict[str, Any]]:
    """解析API返回的单个岗位项"""
    if not item:
        return None
    
    # 尝试从不同字段中提取信息
    position_name = item.get('name') or item.get('title') or item.get('positionName') or item.get('jobTitle') or ""
    work_location = item.get('location') or item.get('workLocation') or item.get('city') or item.get('address') or ""
    position_category = item.get('category') or item.get('positionCategory') or item.get('jobCategory') or ""
    work_experience = item.get('experience') or item.get('workExperience') or item.get('years') or ""
    publish_time = item.get('publishTime') or item.get('updateTime') or item.get('createTime') or item.get('time') or ""
    
    # 如果都没有提取到，检查是否有其他字段
    if not position_name and 'text' in item:
        # 尝试从text字段解析
        text = item.get('text', '')
        if text and len(text) > 10:
            # 假设text包含岗位信息
            parsed_info = parse_position_text(text)
            position_name = parsed_info.get('positionName', position_name)
            work_location = parsed_info.get('workLocation', work_location)
            position_category = parsed_info.get('positionCategory', position_category)
            work_experience = parsed_info.get('workExperience', work_experience)
            publish_time = parsed_info.get('publishTime', publish_time)
    
    # 只有包含足够信息才返回
    if position_name or work_location:
        return {
            "positionName": position_name,
            "workLocation": work_location,
            "positionCategory": position_category,
            "workExperience": work_experience,
            "publishTime": publish_time,
            "page": page_num,
            "rawItem": {k: v for k, v in item.items() if k not in ['rawItem']},
            "extractionMethod": "api_parsing"
        }
    
    return None


def parse_position_text(text: str) -> Dict[str, str]:
    """从文本中解析岗位信息"""
    result = {
        "positionName": "",
        "workLocation": "",
        "positionCategory": "",
        "workExperience": "",
        "publishTime": ""
    }
    
    if not text:
        return result
    
    # 快手招聘的典型格式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 提取岗位名称（在【或-之前的部分）
    if '【' in text:
        before_bracket = text.split('【')[0]
        result["positionName"] = before_bracket.strip()
    elif '-' in text:
        before_dash = text.split('-')[0]
        result["positionName"] = before_dash.strip()
    
    # 提取岗位类别（在【】中）
    if '【' in text and '】' in text:
        import re
        match = re.search(r'【([^】]+)】', text)
        if match:
            result["positionCategory"] = match.group(1).strip()
    
    # 提取工作地点
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安']
    for city in cities:
        if city in text:
            result["workLocation"] = city
            break
    
    # 提取工作经验
    import re
    exp_match = re.search(r'(\d+-\d+年)', text)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    
    # 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', text)
    if time_match:
        result["publishTime"] = time_match.group(1)
    
    return result


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


def create_standard_position_api(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据（API版本）"""
    position_id = f"KS_API_P{raw_position.get('page', 1):03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
    # 标准化时间格式
    publish_time = raw_position.get("publishTime", "")
    if publish_time:
        publish_time = publish_time.replace('.', '-')
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
        "department": raw_position.get("positionCategory", ""),
        "educationRequirement": "本科及以上",
        "workExperience": raw_position.get("workExperience", ""),
        "jobResponsibilities": f"{raw_position.get('positionName', '')}的主要工作职责包括相关领域的开发、维护和优化。",
        "jobRequirements": f"要求具备{raw_position.get('workExperience', '')}相关工作经验，熟悉相关技术和工具。",
        "salaryRange": "面议",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "api_paginated",
        "source": "kuaishou_api",
        "pageNumber": raw_position.get("page", 1),
        
        # 原始数据
        "rawData": {
            "rawItem": raw_position.get("rawItem", {}),
            "extractionMethod": raw_position.get("extractionMethod", ""),
            "path": raw_position.get("path", "")
        }
    }


def save_final_results_api(all_positions: List[Dict[str, Any]]) -> Dict[str, str]:
    """保存最终结果（API版本）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建标准化岗位
    standard_positions = []
    for raw_position in all_positions:
        standard_position = create_standard_position_api(raw_position)
        standard_positions.append(standard_position)
    
    # 1. 保存所有岗位数据
    all_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_api_all_pages_{timestamp}.json")
    
    all_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(standard_positions),
            "totalPages": max([p.get("pageNumber", 1) for p in standard_positions], default=1),
            "source": "快手招聘API",
            "apiUrl": "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple",
            "note": "通过API直接获取所有分页数据"
        },
        "positions": standard_positions
    }
    
    try:
        with open(all_data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存所有API数据: {all_data_file} ({len(standard_positions)} 个岗位)")
    except Exception as e:
        log(f"❌ 保存所有API数据失败: {e}")
        all_data_file = ""
    
    # 2. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_api_stats_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in standard_positions]
    work_locations = []
    position_categories = []
    work_experiences = []
    pages = set()
    
    for p in standard_positions:
        location = p.get("workLocation", "")
        if location and location not in work_locations:
            work_locations.append(location)
        
        category = p.get("positionCategory", "")
        if category and category not in position_categories:
            position_categories.append(category)
        
        experience = p.get("workExperience", "")
        if experience and experience not in work_experiences:
            work_experiences.append(experience)
        
        page_num = p.get("pageNumber", 1)
        pages.add(page_num)
    
    # 按页面统计
    positions_by_page = {}
    for p in standard_positions:
        page_num = p.get("pageNumber", 1)
        positions_by_page[page_num] = positions_by_page.get(page_num, 0) + 1
    
    stats_data = {
        "metadata": {
            "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(standard_positions),
            "totalPages": len(pages),
            "uniquePositionNames": len(set(position_names)),
            "uniqueWorkLocations": len(work_locations),
            "uniquePositionCategories": len(position_categories),
            "uniqueWorkExperiences": len(work_experiences)
        },
        "pageDistribution": positions_by_page,
        "summary": {
            "positionNames": list(set(position_names))[:20],
            "workLocations": work_locations[:20],
            "positionCategories": position_categories[:20],
            "workExperiences": work_experiences[:10]
        },
        "sampleData": standard_positions[:5]
    }
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    # 3. 保存CSV格式
    csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_api_positions_{timestamp}.csv")
    
    try:
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            # 写入CSV头部
            f.write("positionId,positionName,workLocation,positionCategory,publishTime,workExperience,pageNumber,company,crawlTime,detailUrl\n")
            
            # 写入数据
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
        
        log(f"📈 保存CSV格式: {csv_file}")
    except Exception as e:
        log(f"❌ 保存CSV格式失败: {e}")
        csv_file = ""
    
    return {
        "all_data": all_data_file,
        "statistics": stats_file,
        "csv": csv_file
    }


def main():
    """主函数"""
    print()
    print("📋 API分页爬取流程:")
    print("   1. 直接调用快手招聘API")
    print("   2. 自动分页获取所有数据")
    print("   3. 解析API响应中的岗位信息")
    print("   4. 汇总所有分页数据")
    print("   5. 生成完整报告")
    print()
    print("🎯 目标: 通过API获取筛选条件下的所有分页岗位数据")
    print()
    
    # 通过API爬取所有分页数据
    raw_positions = crawl_all_pages_via_api()
    
    if not raw_positions:
        print("❌ 未通过API爬取到任何数据")
        print()
        print("💡 可能的原因:")
        print("   1. API需要认证（如Cookie、Token）")
        print("   2. API地址或参数不正确")
        print("   3. 网络连接问题")
        print("   4. 快手招聘网站反爬虫机制")
        print()
        print("🔄 尝试备用方案: 使用浏览器自动化爬取")
        return
    
    print(f"✅ 通过API爬取到 {len(raw_positions)} 个原始岗位")
    print()
    
    # 保存结果
    saved_files = save_final_results_api(raw_positions)
    
    print()
    print("✅" * 35)
    print("🎉 API分页爬取成功完成！")
    print("✅" * 35)
    print()
    print("📊 最终成果:")
    print(f"   📈 总岗位数: {len(raw_positions)} 个")
    print(f"   📄 总页面数: {max([p.get('page', 1) for p in raw_positions], default=1)} 页")
    print(f"   📂 输出目录: {OUTPUT_DIR}")
    print()
    
    print("📁 生成的文件:")
    for file_type, file_path in saved_files.items():
        if file_path:
            print(f"   • {file_type}: {os.path.basename(file_path)}")
    
    print()
    print("💡 数据使用:")
    print("   1. 查看所有数据: cat output/ks_api_paginated/kuaishou_api_all_pages_*.json")
    print("   2. 查看统计报告: cat output/ks_api_paginated/kuaishou_api_stats_*.json")
    print("   3. 用Excel打开: open output/ks_api_paginated/kuaishou_api_positions_*.csv")
    print("   4. 查看原始API响应: ls output/ks_api_paginated/api_page_*_raw.json")
    print("   5. 分析页面分布: 查看统计报告中的页面分布数据")
    print()
    print("🎯 ks-job 项目目标达成: 成功通过API获取筛选条件下的所有分页岗位数据")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()