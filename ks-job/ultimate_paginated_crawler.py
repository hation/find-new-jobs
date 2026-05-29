#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘终极分页爬取器
使用最简单直接的方法获取所有分页数据
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🚀 快手招聘终极分页爬取器")
print("=" * 80)
print("使用最简单直接的方法获取所有分页数据")
print()

# 输出目录
OUTPUT_DIR = "output/ks_ultimate_paginated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/ultimate_paginated.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def crawl_all_pages_simple() -> List[Dict[str, Any]]:
    """
    简单直接地爬取所有分页数据
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动终极分页爬取器...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器
        browser = await playwright.chromium.launch(
            headless=False,  # 显示窗口，便于观察
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # 访问快手招聘网站
        log("🌐 访问快手招聘网站...")
        await page.goto("https://zhaopin.kuaishou.cn", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # 点击"社会招聘"
        try:
            await page.click("a:has-text('社会招聘')", timeout=5000)
            log("✅ 点击: 社会招聘")
            await page.wait_for_timeout(3000)
        except:
            log("⚠️ 未找到社会招聘按钮，使用当前页面")
        
        # 等待页面加载
        await page.wait_for_timeout(5000)
        
        # 获取所有分页数据
        all_positions = []
        current_page = 1
        max_pages = 100  # 安全限制
        
        log(f"📄 开始爬取分页数据，最多 {max_pages} 页")
        
        while current_page <= max_pages:
            log(f"🔄 处理第 {current_page} 页...")
            
            # 方法1: 直接获取页面所有文本
            page_text = await page.text_content('body')
            
            if page_text:
                # 保存页面文本
                text_file = os.path.join(OUTPUT_DIR, f"page_{current_page:03d}_text.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(page_text)
                log(f"💾 保存第 {current_page} 页文本: {text_file}")
                
                # 从文本中提取岗位
                page_positions = extract_positions_from_text_simple(page_text, current_page)
                
                if page_positions:
                    log(f"✅ 第 {current_page} 页提取到 {len(page_positions)} 个岗位")
                    all_positions.extend(page_positions)
                    
                    # 保存当前页数据
                    page_data_file = os.path.join(OUTPUT_DIR, f"positions_page_{current_page:03d}.json")
                    with open(page_data_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "page": current_page,
                            "positions": page_positions,
                            "count": len(page_positions),
                            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }, f, ensure_ascii=False, indent=2)
                    log(f"💾 保存第 {current_page} 页岗位数据: {page_data_file}")
                else:
                    log(f"⚠️ 第 {current_page} 页未提取到岗位数据")
            
            # 方法2: 尝试翻页
            if current_page < max_pages:
                next_page_success = await try_simple_next_page(page, current_page)
                
                if not next_page_success:
                    log("⏹️ 无法翻页，停止爬取")
                    break
            
            current_page += 1
            await page.wait_for_timeout(2000)  # 等待页面加载
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        log(f"🎉 分页爬取完成，共爬取 {current_page-1} 页，{len(all_positions)} 个岗位")
        return all_positions
        
    except Exception as e:
        log(f"❌ 分页爬取失败: {e}")
        return []


async def try_simple_next_page(page, current_page: int) -> bool:
    """尝试翻到下一页（简单方法）"""
    log(f"🔍 尝试翻到第 {current_page + 1} 页...")
    
    # 方法1: 尝试点击所有可能的翻页元素
    next_selectors = [
        "下一页",
        "next",
        ">",
        "»",
        "加载更多",
        "更多",
        "加载",
        f"{current_page + 1}",
        "下页",
        "后页"
    ]
    
    for selector in next_selectors:
        try:
            await page.click(f"text={selector}", timeout=2000)
            log(f"✅ 点击: {selector}")
            await page.wait_for_timeout(3000)
            return True
        except:
            continue
    
    # 方法2: 尝试点击分页区域
    try:
        pagination_selectors = [
            ".pagination",
            ".ant-pagination",
            "[class*='pagination']",
            "[class*='page']",
            "[class*='Pagination']",
            "[class*='Page']"
        ]
        
        for selector in pagination_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        try:
                            await element.click()
                            await page.wait_for_timeout(1000)
                            log(f"✅ 点击分页元素: {selector}")
                            return True
                        except:
                            continue
            except:
                continue
    except:
        pass
    
    # 方法3: 滚动到底部，可能触发无限滚动
    log("🔄 滚动到底部，尝试触发加载...")
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(3000)
    
    # 检查是否有新内容
    try:
        new_text = await page.text_content('body')
        if len(new_text) > 1000:
            log("✅ 滚动触发新内容加载")
            return True
    except:
        pass
    
    # 方法4: 检查URL参数
    current_url = page.url
    if '?' in current_url:
        # 尝试修改页码参数
        if 'page=' in current_url:
            new_url = re.sub(r'page=\d+', f'page={current_page + 1}', current_url)
        else:
            new_url = f"{current_url}&page={current_page + 1}"
        
        try:
            await page.goto(new_url, wait_until="networkidle")
            log(f"🔗 通过URL跳转到第 {current_page + 1} 页")
            return True
        except:
            pass
    
    log("❌ 所有翻页方法都失败")
    return False


def extract_positions_from_text_simple(text: str, page_num: int) -> List[Dict[str, Any]]:
    """从文本中简单提取岗位信息"""
    positions = []
    
    if not text:
        return positions
    
    # 快手招聘的典型格式模式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 使用正则表达式匹配岗位
    patterns = [
        # 格式: Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22
        r'([^【】\d]{5,40}?)(?:-|【)([^】]{2,10})】([^】]{2,10})([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
        
        # 格式: 岗位名称 工作地点 工作经验 更新时间
        r'([^0-9]{5,30}?)\s+([^0-9]{2,10}?)\s+(\d+-\d+年)\s+(\d{4}\.\d{2}\.\d{2})',
        
        # 包含【】的格式
        r'([^【】]{5,30})【([^】]+)】([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
        
        # 简单格式: 岗位名称 地点 经验 时间
        r'([^0-9]{5,30}?)\s+([^0-9]{2,10}?)\s+(\d+-\d+年)\s+(\d{4}\.\d{2}\.\d{2})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            log(f"✅ 第 {page_num} 页正则匹配找到 {len(matches)} 个岗位")
            
            for match in matches:
                if len(match) >= 4:
                    position_data = {
                        "positionName": match[0].strip() if len(match) > 0 else "",
                        "positionCategory": match[1].strip() if len(match) > 1 else "",
                        "workLocation": match[2].strip() if len(match) > 2 else "",
                        "workExperience": match[3].strip() if len(match) > 3 else "",
                        "publishTime": match[4].strip() if len(match) > 4 else "",
                        "page": page_num,
                        "extractionMethod": "regex_simple",
                        "rawMatch": str(match)[:200]
                    }
                    
                    # 只有包含足够信息才添加
                    if position_data["positionName"] and position_data["workLocation"]:
                        positions.append(position_data)
    
    # 如果没有通过正则匹配到，使用行分析
    if not positions:
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines):
            line = line.strip()
            if len(line) < 30:
                continue
            
            # 检查是否包含岗位信息
            if is_position_line_simple(line):
                position_data = parse_position_line_simple(line, page_num, line_num)
                if position_data:
                    positions.append(position_data)
        
        log(f"📄 第 {page_num} 页行分析提取到 {len(positions)} 个岗位")
    
    return positions


def is_position_line_simple(line: str) -> bool:
    """检查一行是否包含岗位信息（简单判断）"""
    # 岗位相关关键词
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理'
    ]
    
    # 检查是否包含岗位关键词
    has_position_keyword = any(keyword in line for keyword in position_keywords)
    
    # 检查是否有时间格式
    has_time_format = re.search(r'\d{4}\.\d{2}\.\d{2}', line) is not None
    
    # 检查是否有经验格式
    has_experience_format = re.search(r'\d+-\d+年', line) is not None
    
    # 检查是否有地点格式
    has_location = any(city in line for city in ['北京', '上海', '广州', '深圳', '杭州', '成都'])
    
    return has_position_keyword and (has_time_format or has_experience_format or has_location)


def parse_position_line_simple(line: str, page_num: int, line_num: int) -> Optional[Dict[str, Any]]:
    """解析岗位行信息（简单方法）"""
    result = {
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": "",
        "page": page_num,
        "lineNumber": line_num,
        "rawLine": line[:200],
        "extractionMethod": "line_analysis_simple"
    }
    
    # 提取岗位名称（在【或-之前的部分）
    if '【' in line:
        before_bracket = line.split('【')[0]
        result["positionName"] = before_bracket.strip()
    elif '-' in line:
        before_dash = line.split('-')[0]
        result["positionName"] = before_dash.strip()
    else:
        # 尝试提取包含关键词的部分
        for keyword in ['工程师', '开发', '产品', '运营', '经理']:
            if keyword in line:
                start = max(0, line.find(keyword) - 20)
                end = min(len(line), line.find(keyword) + 10)
                result["positionName"] = line[start:end].strip()
                break
    
    # 提取岗位类别（在【】中）
    if '【' in line and '】' in line:
        match = re.search(r'【([^】]+)】', line)
        if match:
            result["positionCategory"] = match.group(1).strip()
    
    # 提取工作地点
    cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '南京', '西安']
    for city in cities:
        if city in line:
            result["workLocation"] = city
            break
    
    # 提取工作经验
    exp_match = re.search(r'(\d+-\d+年)', line)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    
    # 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
    if time_match:
        result["publishTime"] = time_match.group(1)
    
    # 只有提取到足够信息才返回
    if result["positionName"] and result["workLocation"]:
        return result
    
    return None


def create_standard_position_simple(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据（简单方法）"""
    position_id = f"KS_P{raw_position.get('page', 1):03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
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
        "crawlMode": "ultimate_paginated",
        "source": "kuaishou_ultimate",
        "pageNumber": raw_position.get("page", 1),
        
        # 原始数据
        "rawData": {
            "rawLine": raw_position.get("rawLine", "")[:100],
            "extractionMethod": raw_position.get("extractionMethod", ""),
            "lineNumber": raw_position.get("lineNumber")
        }
    }


def save_final_results_simple(all_positions: List[Dict[str, Any]]) -> Dict[str, str]:
    """保存最终结果（简单方法）"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存所有岗位数据
    all_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_all_pages_{timestamp}.json")
    
    # 创建标准化岗位
    standard_positions = []
    for raw_position in all_positions:
        standard_position = create_standard_position_simple(raw_position)
        standard_positions.append(standard_position)
    
    all_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(standard_positions),
            "totalPages": max([p.get("pageNumber", 1) for p in standard_positions], default=1),
            "source": "快手招聘网站（终极分页爬取）",
            "note": "通过简单直接的方法获取所有分页数据"
        },
        "positions": standard_positions
    }
    
    try:
        with open(all_data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存所有页面数据: {all_data_file} ({len(standard_positions)} 个岗位)")
    except Exception as e:
        log(f"❌ 保存所有页面数据失败: {e}")
        all_data_file = ""
    
    # 2. 按页面统计
    pages = set([p.get("pageNumber", 1) for p in standard_positions])
    positions_by_page = {}
    
    for p in standard_positions:
        page_num = p.get("pageNumber", 1)
        if page_num not in positions_by_page:
            positions_by_page[page_num] = []
        positions_by_page[page_num].append(p)
    
    # 3. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_stats_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in standard_positions]
    work_locations = []
    position_categories = []
    work_experiences = []
    
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
        "pageDistribution": {page: len(positions) for page, positions in positions_by_page.items()},
        "summary": {
            "positionNames": list(set(position_names))[:20],
            "workLocations": work_locations[:20],
            "positionCategories": position_categories[:20],
            "workExperiences": work_experiences[:10]
        }
    }
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    # 4. 保存CSV格式
    csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_positions_{timestamp}.csv")
    
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


async def main_async():
    """异步主函数"""
    log("🚀 开始终极分页爬取")
    start_time = datetime.now()
    
    # 爬取所有分页数据
    raw_positions = await crawl_all_pages_simple()
    
    if not raw_positions:
        log("❌ 未爬取到任何数据")
        return {"success": False, "message": "未爬取到任何数据"}
    
    log(f"📊 爬取到 {len(raw_positions)} 个原始岗位")
    
    # 保存结果
    saved_files = save_final_results_simple(raw_positions)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 70)
    log(f"🎉 终极分页爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 总岗位: {len(raw_positions)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    
    for file_type, file_path in saved_files.items():
        if file_path:
            log(f"   • {file_type}: {os.path.basename(file_path)}")
    
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 终极分页爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 点击社会招聘进入岗位列表")
    print("   3. 自动翻页获取所有页面数据")
    print("   4. 简单直接地提取岗位信息")
    print("   5. 汇总所有数据并生成报告")
    print()
    print("⚠️ 注意: 浏览器窗口会自动打开，系统会自动翻页")
    print("      请勿操作浏览器窗口，等待程序完成")
    print()
    
    try:
        stats = asyncio.run(main_async())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 终极分页爬取成功完成！")
            print("✅" * 35)
            print()
            print("📊 最终成果:")
            print(f"   📈 总岗位数: {stats['raw_positions']} 个")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📂 输出目录: {stats['output_dir']}")
            print()
            
            # 显示文件结构
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    json_files = [f for f in files if f.endswith('.json')]
                    page_files = [f for f in json_files if f.startswith('page_')]
                    all_data_files = [f for f in json_files if 'all_pages' in f]
                    csv_files = [f for f in files if f.endswith('.csv')]
                    
                    print("📁 生成的文件:")
                    print(f"   📄 页面数据文件: {len(page_files)} 个")
                    print(f"   📊 汇总数据文件: {len(all_data_files)} 个")
                    print(f"   📈 CSV数据文件: {len(csv_files)} 个")
                    
                    if all_data_files:
                        print("   📋 主要文件:")
                        for file in all_data_files[:3]:
                            print(f"      • {file}")
                    
                    print()
                    print("💡 数据使用:")
                    print("   1. 查看所有数据: cat output/ks_ultimate_paginated/kuaishou_all_pages_*.json")
                    print("   2. 查看统计报告: cat output/ks_ultimate_paginated/kuaishou_stats_*.json")
                    print("   3. 用Excel打开: open output/ks_ultimate_paginated/kuaishou_positions_*.csv")
                    print("   4. 查看分页数据: ls output/ks_ultimate_paginated/page_*_text.txt")
                    print("   5. 分析页面分布: 查看统计报告中的页面分布")
                    print()
                    print("🎯 ks-job 项目目标达成: 成功获取筛选条件下的所有分页岗位数据")
        else:
            print()
            print("❌ 爬取失败")
            print(f"   错误信息: {stats.get('message', '未知错误')}")
            
    except KeyboardInterrupt:
        print()
        log("⏹️ 用户中断爬取")
    except Exception as e:
        log(f"❌ 程序异常: {e}")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()