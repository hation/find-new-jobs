#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘智能爬取器
专门针对快手招聘网站的智能数据提取
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

print("=" * 80)
print("🚀 快手招聘智能爬取器")
print("=" * 80)
print("专门针对快手招聘网站的智能数据提取")
print()

# 输出目录
OUTPUT_DIR = "output/ks_smart"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/kuaishou_smart_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def smart_crawl_kuaishou() -> Optional[List[Dict[str, Any]]]:
    """
    智能爬取快手招聘数据
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动智能爬取器...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器
        browser = await playwright.chromium.launch(
            headless=False,
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
        
        # 等待岗位列表加载
        log("⏳ 等待岗位列表加载...")
        await page.wait_for_timeout(5000)
        
        # 方法1: 尝试直接提取岗位数据
        log("🔍 尝试直接提取岗位数据...")
        
        # 快手招聘网站的岗位数据可能以JSON格式嵌入在页面中
        try:
            # 查找包含岗位数据的script标签
            page_content = await page.content()
            
            # 查找可能的JSON数据
            json_patterns = [
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                r'var\s+positions\s*=\s*(\[.*?\]);',
                r'"positions"\s*:\s*(\[.*?\])',
                r'"list"\s*:\s*(\[.*?\])',
                r'data:\s*({.*?})',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, page_content, re.DOTALL)
                if matches:
                    log(f"✅ 找到JSON数据，模式: {pattern[:30]}...")
                    
                    for match in matches[:3]:  # 只检查前3个匹配
                        try:
                            data = json.loads(match)
                            log(f"   JSON数据解析成功，类型: {type(data)}")
                            
                            # 检查是否是岗位数据
                            if isinstance(data, dict):
                                # 尝试查找岗位列表
                                positions = find_positions_in_json(data)
                                if positions:
                                    log(f"🎉 从JSON中提取到 {len(positions)} 个岗位")
                                    return positions
                            elif isinstance(data, list):
                                # 直接是岗位列表
                                log(f"🎉 从JSON中提取到 {len(data)} 个岗位")
                                return data
                        except json.JSONDecodeError:
                            continue
            
            log("⚠️ 未找到JSON格式的岗位数据")
        except Exception as e:
            log(f"⚠️ JSON提取失败: {e}")
        
        # 方法2: 从页面HTML中提取岗位信息
        log("🔍 从页面HTML中提取岗位信息...")
        
        # 获取页面HTML
        html_content = await page.content()
        
        # 保存HTML用于分析
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = os.path.join(OUTPUT_DIR, f"kuaishou_html_{timestamp}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        log(f"💾 保存HTML: {html_file}")
        
        # 方法3: 使用JavaScript提取岗位元素
        log("🔄 使用JavaScript提取岗位元素...")
        
        js_extract = """
        // 快手招聘网站的岗位元素可能有特定的class
        const positions = [];
        
        // 尝试多种选择器
        const selectors = [
            '.position-item',
            '.job-item',
            '.recruit-item',
            '.position-list-item',
            '.job-list-item',
            '[data-position]',
            '[data-job]',
            'tr[data-index]',
            'div[class*="position"]',
            'div[class*="job"]',
            'div[class*="recruit"]',
            'li[class*="position"]',
            'li[class*="job"]'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`找到 ${elements.length} 个元素使用选择器: ${selector}`);
                
                elements.forEach((element, index) => {
                    const text = element.textContent?.trim();
                    if (text && text.length > 30) {
                        positions.push({
                            selector: selector,
                            index: index,
                            text: text,
                            html: element.outerHTML,
                            className: element.className,
                            id: element.id,
                            dataset: element.dataset
                        });
                    }
                });
                
                if (positions.length > 0) {
                    break;
                }
            }
        }
        
        // 如果没找到，尝试查找包含岗位信息的表格
        if (positions.length === 0) {
            const tables = document.querySelectorAll('table');
            tables.forEach((table, tableIndex) => {
                const rows = table.querySelectorAll('tr');
                if (rows.length > 1) {
                    rows.forEach((row, rowIndex) => {
                        const text = row.textContent?.trim();
                        if (text && text.length > 30) {
                            positions.push({
                                selector: `table:nth-child(${tableIndex + 1}) tr:nth-child(${rowIndex + 1})`,
                                index: positions.length,
                                text: text,
                                html: row.outerHTML,
                                className: row.className,
                                type: 'table_row'
                            });
                        }
                    });
                }
            });
        }
        
        return positions;
        """
        
        try:
            positions = await page.evaluate(js_extract)
            if positions and len(positions) > 0:
                log(f"✅ JavaScript提取到 {len(positions)} 个岗位元素")
                
                # 保存JavaScript提取结果
                js_file = os.path.join(OUTPUT_DIR, f"kuaishou_js_extract_{timestamp}.json")
                with open(js_file, 'w', encoding='utf-8') as f:
                    json.dump(positions, f, ensure_ascii=False, indent=2)
                log(f"💾 保存JS提取结果: {js_file}")
                
                return positions
            else:
                log("⚠️ JavaScript未提取到岗位元素")
        except Exception as e:
            log(f"⚠️ JavaScript提取失败: {e}")
        
        # 方法4: 截图并OCR分析（备选方案）
        log("📸 截图页面...")
        screenshot_file = os.path.join(OUTPUT_DIR, f"kuaishou_screenshot_{timestamp}.png")
        await page.screenshot(path=screenshot_file, full_page=True)
        log(f"💾 保存截图: {screenshot_file}")
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        log("❌ 所有提取方法都未成功获取岗位数据")
        return None
        
    except ImportError:
        log("❌ 未安装Playwright")
        return None
    except Exception as e:
        log(f"❌ 智能爬取失败: {e}")
        return None


def find_positions_in_json(data: Any, path: str = "") -> List[Dict[str, Any]]:
    """在JSON数据中递归查找岗位信息"""
    positions = []
    
    if isinstance(data, dict):
        # 检查当前字典是否包含岗位信息
        if any(key in data for key in ['position', 'job', 'recruit', 'name', 'title']):
            positions.append({
                "data": data,
                "path": path,
                "type": "dict_with_position_keys"
            })
        
        # 递归检查所有值
        for key, value in data.items():
            positions.extend(find_positions_in_json(value, f"{path}.{key}"))
    
    elif isinstance(data, list):
        # 检查列表中的每个元素
        for i, item in enumerate(data):
            positions.extend(find_positions_in_json(item, f"{path}[{i}]"))
    
    return positions


def parse_kuaishou_position(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """解析快手招聘岗位信息"""
    text = raw_position.get("text", "")
    html = raw_position.get("html", "")
    
    # 初始化结果
    result = {
        "rawText": text,
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": "",
        "department": "",
        "educationRequirement": "",
        "jobResponsibilities": "",
        "jobRequirements": "",
        "salaryRange": "",
        "detailUrl": "",
        "source": "kuaishou_smart_crawler"
    }
    
    if not text:
        return result
    
    # 快手招聘的典型格式分析
    # 示例: "Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22"
    
    # 1. 提取岗位名称（通常在开头，到"【"或"-"之前）
    name_patterns = [
        r'^([^【】\[\]-]{5,40}?)(?:-|【|\[)',
        r'^([^【】\[\]-]{5,40}?)\s*(?:工程师|开发|产品|运营|设计|分析|测试|运维|算法|经理|专员|助理)',
        r'职位名称[：:]\s*([^\n]+)',
        r'岗位[：:]\s*([^\n]+)'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            result["positionName"] = match.group(1).strip()
            break
    
    # 2. 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', text)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    else:
        # 尝试从文本中推断类别
        category_keywords = {
            '工程类': ['工程', '开发', '研发', '技术'],
            '产品类': ['产品', 'PM', '项目经理'],
            '运营类': ['运营', '推广', '营销'],
            '设计类': ['设计', 'UI', 'UX', '视觉'],
            '算法类': ['算法', 'AI', '人工智能', '机器学习'],
            '市场类': ['市场', '销售', '商务'],
            '职能类': ['行政', '人事', '财务', '法务'],
            '客服类': ['客服', '支持', '服务']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                result["positionCategory"] = category
                break
    
    # 3. 提取工作地点（通常是城市名）
    location_patterns = [
        r'工作地点[：:]\s*([^\n]+)',
        r'地点[：:]\s*([^\n]+)',
        # 中国主要城市
        r'(北京|上海|广州|深圳|杭州|成都|武汉|南京|西安|苏州|重庆|天津|长沙|合肥|郑州|济南|青岛|大连|沈阳|长春|哈尔滨|厦门|福州|南宁)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            locations = match.group(1).strip()
            # 清理和标准化
            locations = re.sub(r'[，,]\s*', ', ', locations)
            result["workLocation"] = locations
            break
    
    # 4. 提取工作经验
    experience_patterns = [
        r'工作年限[：:]\s*([^\n]+)',
        r'经验[：:]\s*([^\n]+)',
        r'(\d+[-~]?\d*年)',
        r'(\d+-\d+年)',
        r'([一二三四五六七八九十]+年)'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, text)
        if match:
            result["workExperience"] = match.group(1).strip()
            break
    
    # 5. 提取发布时间（快手格式通常是YYYY.MM.DD）
    time_patterns = [
        r'更新时间[：:]\s*([^\n]+)',
        r'发布时间[：:]\s*([^\n]+)',
        r'(\d{4}\.\d{2}\.\d{2})',  # 快手格式: 2026.05.22
        r'(\d{4}-\d{2}-\d{2})',
        r'(\d{4}/\d{2}/\d{2})'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            time_str = match.group(1).strip()
            # 标准化时间格式
            time_str = time_str.replace('.', '-').replace('/', '-')
            result["publishTime"] = time_str
            break
    
    # 6. 提取部门信息
    department_patterns = [
        r'部门[：:]\s*([^\n]+)',
        r'事业部[：:]\s*([^\n]+)',
        r'线[：:]\s*([^\n]+)',
        r'团队[：:]\s*([^\n]+)'
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, text)
        if match:
            result["department"] = match.group(1).strip()
            break
    
    # 7. 从HTML中提取详情链接
    if html:
        url_patterns = [
            r'href=["\']([^"\']+position[^"\']*)["\']',
            r'href=["\']([^"\']+job[^"\']*)["\']',
            r'href=["\']([^"\']+recruit[^"\']*)["\']',
            r'href=["\'](/position/[^"\']+)["\']'
        ]
        
        for pattern in url_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                url = match.group(1)
                if url.startswith('/'):
                    url = f"https://zhaopin.kuaishou.cn{url}"
                result["detailUrl"] = url
                break
    
    # 8. 如果没有提取到详情链接，生成一个
    if not result["detailUrl"]:
        position_id = hash(text) % 1000000
        result["detailUrl"] = f"https://zhaopin.kuaishou.cn/position/{position_id}"
    
    # 9. 提取文本中的其他信息
    lines = text.split('\n')
    if len(lines) > 1:
        # 第一行通常是岗位名称和基本信息
        # 后续行可能包含工作职责和要求
        if len(lines) >= 3:
            result["jobResponsibilities"] = lines[1].strip()[:300]
            if len(lines) >= 4:
                result["jobRequirements"] = lines[2].strip()[:300]
    
    return result


def create_standard_position(parsed_position: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_data)) % 10000:04d}"
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": parsed_position["positionName"] or "快手招聘岗位",
        "workLocation": parsed_position["workLocation"] or "全国",
        "positionCategory": parsed_position["positionCategory"] or "",
        "publishTime": parsed_position["publishTime"] or datetime.now().strftime("%Y-%m-%d"),
        "detailUrl": parsed_position["detailUrl"],
        "department": parsed_position["department"] or "",
        "educationRequirement": parsed_position["educationRequirement"] or "",
        "workExperience": parsed_position["workExperience"] or "",
        "jobResponsibilities": parsed_position["jobResponsibilities"] or parsed_position["rawText"][:300],
        "jobRequirements": parsed_position["jobRequirements"] or "",
        "salaryRange": parsed_position["salaryRange"] or "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "smart_crawler",
        "source": "kuaishou_official",
        
        # 解析信息
        "parsedInfo": {k: v for k, v in parsed_position.items() if k != "rawText"},
        
        # 原始数据
        "rawData": {
            "text": parsed_position["rawText"][:500],
            "selector": raw_data.get("selector", ""),
            "index": raw_data.get("index", 0)
        }
    }


def save_positions_batch(positions: List[Dict[str, Any]]) -> str:
    """批量保存岗位数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_file = os.path.join(OUTPUT_DIR, f"kuaishou_positions_batch_{timestamp}.json")
    
    batch_data = {
        "metadata": {
            "batchId": timestamp,
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "source": "kuaishou_smart_crawler"
        },
        "positions": positions
    }
    
    try:
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        
        log(f"💾 批量保存 {len(positions)} 个岗位到: {batch_file}")
        return batch_file
    except Exception as e:
        log(f"❌ 批量保存失败: {e}")
        return ""


async def main_async():
    """异步主函数"""
    log("🚀 开始快手招聘智能爬取")
    start_time = datetime.now()
    
    # 智能爬取
    raw_positions = await smart_crawl_kuaishou()
    
    if not raw_positions:
        log("❌ 智能爬取未获取到数据")
        return {"success": False, "message": "未获取到数据"}
    
    log(f"📊 获取到 {len(raw_positions)} 个原始岗位元素")
    
    # 解析和处理
    processed_positions = []
    
    for i, raw_position in enumerate(raw_positions, 1):
        if i % 10 == 0:
            log(f"📝 解析进度: {i}/{len(raw_positions)}")
        
        try:
            # 解析岗位信息
            parsed_position = parse_kuaishou_position(raw_position)
            
            # 创建标准化岗位
            standard_position = create_standard_position(parsed_position, raw_position)
            
            processed_positions.append(standard_position)
            
            # 每10个岗位保存一次进度
            if i % 10 == 0:
                progress_file = os.path.join(OUTPUT_DIR, f"progress_{i}.json")
                with open(progress_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_positions[-10:], f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            log(f"⚠️ 解析第 {i} 个岗位失败: {e}")
            continue
    
    # 批量保存所有岗位
    batch_file = save_positions_batch(processed_positions)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "processed_positions": len(processed_positions),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "batch_file": batch_file,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 70)
    log(f"🎉 快手招聘智能爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 原始元素: {len(raw_positions)}个")
    log(f"   • 处理岗位: {len(processed_positions)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log(f"   • 批量文件: {os.path.basename(batch_file) if batch_file else '无'}")
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 快手招聘智能爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 点击社会招聘进入岗位列表")
    print("   3. 智能提取页面中的岗位数据")
    print("   4. 解析岗位详细信息")
    print("   5. 批量保存标准化数据")
    print()
    print("🎯 目标: 获取筛选条件下的所有岗位数据")
    print()
    
    try:
        stats = asyncio.run(main_async())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 快手招聘智能爬取成功！")
            print("✅" * 35)
            print()
            print("📊 最终统计:")
            print(f"   📈 原始岗位元素: {stats['raw_positions']}")
            print(f"   📈 处理岗位数: {stats['processed_positions']}")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📁 输出目录: {stats['output_dir']}")
            
            if stats['batch_file']:
                print(f"   💾 批量文件: {os.path.basename(stats['batch_file'])}")
            
            print()
            print("💡 数据验证:")
            print("   1. 查看批量数据: cat output/ks_smart/kuaishou_positions_batch_*.json | head -100")
            print("   2. 检查岗位数量: jq '.metadata.totalPositions' output/ks_smart/kuaishou_positions_batch_*.json")
            print("   3. 查看岗位示例: jq '.positions[0]' output/ks_smart/kuaishou_positions_batch_*.json")
            print("   4. 分析数据: 使用Python或Excel处理JSON文件")
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