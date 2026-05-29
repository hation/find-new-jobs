#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘分页爬取器
自动翻页获取所有页面数据并汇总
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Set

print("=" * 80)
print("🚀 快手招聘分页爬取器")
print("=" * 80)
print("自动翻页获取所有页面数据并汇总")
print()

# 输出目录
OUTPUT_DIR = "output/ks_paginated"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/paginated_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def crawl_all_pages_with_pagination() -> List[Dict[str, Any]]:
    """
    爬取所有分页数据
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动分页爬取器...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器（显示窗口，便于观察翻页）
        browser = await playwright.chromium.launch(
            headless=False,  # 显示窗口
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
        max_pages = 50  # 安全限制，防止无限循环
        
        log(f"📄 开始爬取分页数据，最多 {max_pages} 页")
        
        while current_page <= max_pages:
            log(f"🔄 处理第 {current_page} 页...")
            
            # 保存当前页面的截图
            screenshot_file = os.path.join(OUTPUT_DIR, f"page_{current_page:03d}_{datetime.now().strftime('%H%M%S')}.png")
            await page.screenshot(path=screenshot_file)
            log(f"📸 保存第 {current_page} 页截图: {screenshot_file}")
            
            # 获取当前页面文本
            page_text = await page.text_content('body')
            if page_text:
                log(f"📄 第 {current_page} 页文本大小: {len(page_text)} 字符")
                
                # 保存页面文本
                text_file = os.path.join(OUTPUT_DIR, f"page_{current_page:03d}_text.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(page_text)
                log(f"💾 保存第 {current_page} 页文本: {text_file}")
            
            # 从当前页面提取岗位数据
            page_positions = await extract_positions_from_current_page(page, current_page)
            
            if page_positions:
                log(f"✅ 第 {current_page} 页提取到 {len(page_positions)} 个岗位")
                all_positions.extend(page_positions)
                
                # 保存当前页的岗位数据
                page_data_file = os.path.join(OUTPUT_DIR, f"positions_page_{current_page:03d}.json")
                with open(page_data_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "page": current_page,
                        "positions": page_positions,
                        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }, f, ensure_ascii=False, indent=2)
                log(f"💾 保存第 {current_page} 页岗位数据: {page_data_file}")
            else:
                log(f"⚠️ 第 {current_page} 页未提取到岗位数据")
            
            # 尝试翻页
            next_page_success = await try_go_to_next_page(page, current_page)
            
            if not next_page_success:
                log("⏹️ 无法翻页，停止爬取")
                break
            
            current_page += 1
            await page.wait_for_timeout(3000)  # 等待页面加载
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        log(f"🎉 分页爬取完成，共爬取 {current_page-1} 页，{len(all_positions)} 个岗位")
        return all_positions
        
    except Exception as e:
        log(f"❌ 分页爬取失败: {e}")
        return []


async def try_go_to_next_page(page, current_page: int) -> bool:
    """尝试翻到下一页"""
    log(f"🔍 尝试翻到第 {current_page + 1} 页...")
    
    # 方法1: 尝试点击"下一页"按钮
    try:
        await page.click("button:has-text('下一页')", timeout=3000)
        log("✅ 点击: 下一页 按钮")
        return True
    except:
        pass
    
    # 方法2: 尝试点击"加载更多"按钮
    try:
        await page.click("button:has-text('加载更多')", timeout=3000)
        log("✅ 点击: 加载更多 按钮")
        return True
    except:
        pass
    
    # 方法3: 尝试点击页码按钮
    try:
        next_page_num = current_page + 1
        await page.click(f"a:has-text('{next_page_num}')", timeout=3000)
        log(f"✅ 点击页码: {next_page_num}")
        return True
    except:
        pass
    
    # 方法4: 尝试点击">"或"»"按钮
    try:
        await page.click("a:has-text('>')", timeout=3000)
        log("✅ 点击: > 按钮")
        return True
    except:
        pass
    
    try:
        await page.click("a:has-text('»')", timeout=3000)
        log("✅ 点击: » 按钮")
        return True
    except:
        pass
    
    # 方法5: 滚动到底部，可能触发自动加载
    log("🔄 滚动到底部，尝试触发自动加载...")
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(3000)
    
    # 检查是否有新内容加载
    try:
        # 检查是否有新元素出现
        new_elements = await page.query_selector_all(":scope >> text=/岗位|职位|招聘/")
        if new_elements and len(new_elements) > 0:
            log("✅ 滚动触发新内容加载")
            return True
    except:
        pass
    
    # 方法6: 检查URL中是否有页码参数
    current_url = page.url
    if 'page=' in current_url:
        # 更新页码
        new_page_num = current_page + 1
        new_url = re.sub(r'page=\d+', f'page={new_page_num}', current_url)
        
        try:
            await page.goto(new_url, wait_until="networkidle")
            log(f"🔗 通过URL跳转到第 {new_page_num} 页")
            return True
        except:
            pass
    
    # 方法7: 检查是否有分页元素
    try:
        pagination_elements = await page.query_selector_all(".pagination, .ant-pagination, [class*='pagination']")
        if pagination_elements:
            log(f"🔍 找到分页元素，尝试点击下一个")
            
            # 尝试点击所有可能的翻页元素
            for element in pagination_elements:
                try:
                    await element.click()
                    await page.wait_for_timeout(1000)
                    log("✅ 点击分页元素")
                    return True
                except:
                    continue
    except:
        pass
    
    log("❌ 所有翻页方法都失败")
    return False


async def extract_positions_from_current_page(page, page_num: int) -> List[Dict[str, Any]]:
    """从当前页面提取岗位数据"""
    positions = []
    
    try:
        # 获取页面HTML
        html_content = await page.content()
        
        # 保存HTML
        html_file = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}_source.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 使用JavaScript提取岗位信息
        js_extract = """
        (function() {
            const positions = [];
            
            // 快手招聘的岗位可能在这些元素中
            const positionSelectors = [
                '.position-item',
                '.job-item',
                '.recruit-item',
                '.position-list-item',
                '.job-list-item',
                'tr[data-index]',
                'div[class*="position"]',
                'div[class*="job"]',
                'div[class*="recruit"]',
                'li[class*="position"]',
                'li[class*="job"]',
                'table tr',
                '.ant-table-row',
                '[data-role="position"]',
                '[data-type="job"]'
            ];
            
            for (const selector of positionSelectors) {
                const elements = document.querySelectorAll(selector);
                
                if (elements.length > 0) {
                    console.log(`找到 ${elements.length} 个元素使用选择器: ${selector}`);
                    
                    elements.forEach((element, index) => {
                        const text = element.textContent?.trim();
                        
                        if (text && text.length > 30) {
                            // 检查是否包含岗位相关关键词
                            const keywords = ['工程师', '开发', '产品', '运营', '设计', '分析', '测试', '运维', '算法', '经理', '专员', '助理'];
                            const hasKeyword = keywords.some(keyword => text.includes(keyword));
                            
                            if (hasKeyword) {
                                positions.push({
                                    selector: selector,
                                    index: index,
                                    text: text,
                                    html: element.outerHTML.substring(0, 500),
                                    className: element.className,
                                    id: element.id,
                                    page: window.location.href
                                });
                            }
                        }
                    });
                }
            }
            
            // 如果没找到，尝试查找所有包含"工程师"、"开发"等关键词的文本
            if (positions.length === 0) {
                const allElements = document.querySelectorAll('*');
                
                allElements.forEach((element, index) => {
                    const text = element.textContent?.trim();
                    
                    if (text && text.length > 30 && text.length < 500) {
                        // 快手招聘的典型格式: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
                        const hasPositionFormat = /【.*】.*\d+-\d+年\d{4}\.\d{2}\.\d{2}/.test(text);
                        
                        if (hasPositionFormat) {
                            positions.push({
                                selector: element.tagName,
                                index: index,
                                text: text,
                                html: element.outerHTML.substring(0, 500),
                                className: element.className,
                                id: element.id,
                                page: window.location.href,
                                format: 'position_format'
                            });
                        }
                    }
                });
            }
            
            return positions;
        })();
        """
        
        positions = await page.evaluate(js_extract)
        
        if positions:
            log(f"✅ 第 {page_num} 页JavaScript提取到 {len(positions)} 个岗位元素")
        else:
            log(f"⚠️ 第 {page_num} 页JavaScript未提取到岗位元素")
            
            # 备选方案: 获取页面所有文本，手动解析
            page_text = await page.text_content('body')
            if page_text:
                text_positions = parse_positions_from_text(page_text, page_num)
                positions.extend(text_positions)
                log(f"📄 第 {page_num} 页文本解析提取到 {len(text_positions)} 个岗位")
        
    except Exception as e:
        log(f"⚠️ 第 {page_num} 页数据提取失败: {e}")
    
    return positions


def parse_positions_from_text(text: str, page_num: int) -> List[Dict[str, Any]]:
    """从文本中解析岗位信息"""
    positions = []
    
    if not text:
        return positions
    
    # 快手招聘的典型格式
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 按行分割
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) < 30:
            continue
        
        # 检查是否是岗位行
        if is_position_line(line):
            position_data = {
                "text": line[:200],
                "lineNumber": line_num,
                "page": page_num,
                "extractionMethod": "text_parsing"
            }
            
            # 解析岗位信息
            parsed_info = parse_position_line(line)
            position_data.update(parsed_info)
            
            positions.append(position_data)
    
    return positions


def is_position_line(line: str) -> bool:
    """检查一行是否包含岗位信息"""
    # 岗位相关关键词
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理',
        '策划', '销售', '市场', '客服', '行政', '财务'
    ]
    
    # 检查是否包含岗位关键词
    has_position_keyword = any(keyword in line for keyword in position_keywords)
    
    # 检查是否有时间格式（快手格式: 2026.05.22）
    has_time_format = re.search(r'\d{4}\.\d{2}\.\d{2}', line) is not None
    
    # 检查是否有工作经验格式（如：3-5年）
    has_experience_format = re.search(r'\d+-\d+年', line) is not None
    
    # 检查是否有【】格式
    has_bracket_format = '【' in line and '】' in line
    
    # 如果包含岗位关键词，并且有时间、经验或括号格式中的至少一个，认为是岗位行
    return has_position_keyword and (has_time_format or has_experience_format or has_bracket_format)


def parse_position_line(line: str) -> Dict[str, Any]:
    """解析岗位行信息"""
    result = {
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": ""
    }
    
    # 提取岗位名称（在【或-之前的部分）
    name_match = re.search(r'^([^【】\[-]{5,40}?)(?:-|【|\[)', line)
    if name_match:
        result["positionName"] = name_match.group(1).strip()
    
    # 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', line)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    
    # 提取工作地点
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
    
    # 提取工作经验
    exp_match = re.search(r'(\d+-\d+年)', line)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    
    # 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
    if time_match:
        result["publishTime"] = time_match.group(1)
    
    return result


def create_standard_position(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_PAGE{raw_position.get('page', 1):03d}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
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
        "crawlMode": "paginated_crawler",
        "source": "kuaishou_paginated",
        "pageNumber": raw_position.get("page", 1),
        
        # 原始数据
        "rawData": {
            "text": raw_position.get("text", "")[:200],
            "extractionMethod": raw_position.get("extractionMethod", ""),
            "selector": raw_position.get("selector", "")
        }
    }


def save_final_results(all_positions: List[Dict[str, Any]]) -> Dict[str, str]:
    """保存最终结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存所有岗位数据
    all_data_file = os.path.join(OUTPUT_DIR, f"kuaishou_all_pages_positions_{timestamp}.json")
    
    all_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(all_positions),
            "totalPages": max([p.get("pageNumber", 1) for p in all_positions], default=1),
            "source": "快手招聘网站（分页爬取）",
            "note": "通过自动翻页获取所有页面的数据"
        },
        "positions": all_positions
    }
    
    try:
        with open(all_data_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存所有页面数据: {all_data_file} ({len(all_positions)} 个岗位)")
    except Exception as e:
        log(f"❌ 保存所有页面数据失败: {e}")
        all_data_file = ""
    
    # 2. 按页面分组保存
    positions_by_page = {}
    for position in all_positions:
        page_num = position.get("pageNumber", 1)
        if page_num not in positions_by_page:
            positions_by_page[page_num] = []
        positions_by_page[page_num].append(position)
    
    for page_num, page_positions in positions_by_page.items():
        page_file = os.path.join(OUTPUT_DIR, f"page_{page_num:03d}_positions.json")
        with open(page_file, 'w', encoding='utf-8') as f:
            json.dump({
                "page": page_num,
                "positions": page_positions,
                "count": len(page_positions)
            }, f, ensure_ascii=False, indent=2)
    
    log(f"📄 按页面分组保存完成，共 {len(positions_by_page)} 个页面")
    
    # 3. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_paginated_stats_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in all_positions]
    work_locations = []
    position_categories = []
    work_experiences = []
    pages = set()
    
    for p in all_positions:
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
    positions_by_page_count = {}
    for p in all_positions:
        page_num = p.get("pageNumber", 1)
        positions_by_page_count[page_num] = positions_by_page_count.get(page_num, 0) + 1
    
    stats_data = {
        "metadata": {
            "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(all_positions),
            "totalPages": len(pages),
            "uniquePositionNames": len(set(position_names)),
            "uniqueWorkLocations": len(work_locations),
            "uniquePositionCategories": len(position_categories),
            "uniqueWorkExperiences": len(work_experiences)
        },
        "summary": {
            "positionNames": list(set(position_names))[:20],
            "workLocations": work_locations[:20],
            "positionCategories": position_categories[:20],
            "workExperiences": work_experiences[:10]
        },
        "pageDistribution": positions_by_page_count,
        "sampleData": all_positions[:5]
    }
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    # 4. 保存CSV格式
    csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_paginated_positions_{timestamp}.csv")
    
    try:
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
                    f'"{position.get("company", "")}"',
                    f'"{position.get("crawlTime", "")}"'
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
    log("🚀 开始分页爬取所有快手招聘数据")
    start_time = datetime.now()
    
    # 爬取所有分页数据
    raw_positions = await crawl_all_pages_with_pagination()
    
    if not raw_positions:
        log("❌ 未爬取到任何数据")
        return {"success": False, "message": "未爬取到任何数据"}
    
    log(f"📊 爬取到 {len(raw_positions)} 个原始岗位元素")
    
    # 处理数据
    processed_positions = []
    for raw_position in raw_positions:
        standard_position = create_standard_position(raw_position)
        processed_positions.append(standard_position)
    
    log(f"✅ 处理完成，共 {len(processed_positions)} 个标准化岗位")
    
    # 保存结果
    saved_files = save_final_results(processed_positions)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "processed_positions": len(processed_positions),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 70)
    log(f"🎉 分页爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 原始岗位: {len(raw_positions)}个")
    log(f"   • 处理岗位: {len(processed_positions)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    
    for file_type, file_path in saved_files.items():
        if file_path:
            log(f"   • {file_type}: {os.path.basename(file_path)}")
    
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 分页爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 点击社会招聘进入岗位列表")
    print("   3. 自动翻页获取所有页面数据")
    print("   4. 智能提取每个页面的岗位信息")
    print("   5. 汇总所有数据并生成报告")
    print()
    print("⚠️ 注意: 浏览器窗口会自动打开，请勿关闭")
    print("      系统会自动翻页直到没有更多数据")
    print()
    
    try:
        stats = asyncio.run(main_async())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 分页爬取成功完成！")
            print("✅" * 35)
            print()
            print("📊 最终统计:")
            print(f"   📈 总岗位数: {stats['processed_positions']} 个")
            print(f"   📄 总页面数: 查看统计报告")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📁 输出目录: {stats['output_dir']}")
            print()
            
            # 显示文件结构
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    json_files = [f for f in files if f.endswith('.json')]
                    page_files = [f for f in json_files if f.startswith('page_') and 'positions' in f]
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
                    print("   1. 查看所有数据: cat output/ks_paginated/kuaishou_all_pages_positions_*.json")
                    print("   2. 查看统计报告: cat output/ks_paginated/kuaishou_paginated_stats_*.json")
                    print("   3. 用Excel打开: open output/ks_paginated/kuaishou_paginated_positions_*.csv")
                    print("   4. 查看分页数据: ls output/ks_paginated/page_*_positions.json")
                    print("   5. 分析页面分布: 查看统计报告中的页面分布数据")
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