#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘页面爬取器
使用Playwright访问网站页面，从页面中提取数据
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 70)
print("🚀 快手招聘页面爬取器")
print("=" * 70)
print("使用Playwright访问网站页面，从页面中提取数据")
print("绕过API签名验证")
print()

# 输出目录
OUTPUT_DIR = "output/ks_page_scraper"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/page_scraper.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def scrape_data_from_page() -> Optional[List[Dict[str, Any]]]:
    """
    从页面中爬取数据
    
    Returns:
        岗位数据列表 或 None
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器访问页面...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器（显示窗口，便于观察）
        browser = await playwright.chromium.launch(
            headless=False,  # 显示浏览器窗口
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        # 创建上下文
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        
        # 创建页面
        page = await context.new_page()
        
        # 访问快手招聘网站首页
        log("🌐 访问快手招聘网站首页...")
        await page.goto("https://zhaopin.kuaishou.cn", wait_until="networkidle")
        
        # 等待页面加载
        await page.wait_for_timeout(5000)
        log("✅ 首页加载完成")
        
        # 方法1: 尝试找到并点击"社会招聘"或"校园招聘"
        try:
            log("🔍 寻找招聘分类...")
            
            # 可能的招聘分类选择器
            recruit_selectors = [
                "a:has-text('社会招聘')",
                "a:has-text('校园招聘')",
                "button:has-text('社会招聘')",
                "button:has-text('校园招聘')",
                ".recruit-tab",
                ".nav-item"
            ]
            
            for selector in recruit_selectors:
                try:
                    await page.click(selector, timeout=3000)
                    log(f"✅ 点击: {selector}")
                    await page.wait_for_timeout(3000)
                    break
                except:
                    continue
        except:
            log("⚠️ 未找到招聘分类按钮")
        
        # 方法2: 滚动页面加载更多内容
        log("🔄 滚动页面加载更多内容...")
        for i in range(5):
            await page.evaluate(f"window.scrollTo(0, {1000 * (i + 1)})")
            await page.wait_for_timeout(2000)
            log(f"📜 滚动 {i+1}/5 次")
        
        # 等待内容加载
        await page.wait_for_timeout(5000)
        
        # 方法3: 尝试从页面中提取数据
        log("🔍 从页面中提取数据...")
        
        # 尝试多种提取方式
        positions = []
        
        # 方式1: 通过CSS选择器提取
        try:
            position_selectors = [
                ".position-item",
                ".job-item",
                ".recruit-item",
                "[class*='position']",
                "[class*='job']",
                "[class*='recruit']"
            ]
            
            for selector in position_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    if elements and len(elements) > 0:
                        log(f"✅ 找到 {len(elements)} 个元素使用选择器: {selector}")
                        
                        for i, element in enumerate(elements[:10]):  # 只取前10个
                            try:
                                # 提取文本内容
                                text = await element.text_content()
                                if text and len(text.strip()) > 10:
                                    position_data = {
                                        "rawText": text.strip(),
                                        "selector": selector,
                                        "index": i
                                    }
                                    positions.append(position_data)
                            except:
                                pass
                        break
                except:
                    continue
        except Exception as e:
            log(f"⚠️ CSS选择器提取失败: {e}")
        
        # 方式2: 通过页面文本提取
        try:
            page_text = await page.text_content()
            if page_text:
                # 查找可能的岗位信息
                position_patterns = [
                    r'岗位名称[：:]\s*([^\n]+)',
                    r'职位[：:]\s*([^\n]+)',
                    r'工作地点[：:]\s*([^\n]+)',
                    r'岗位职责[：:]\s*([^\n]+)',
                    r'任职要求[：:]\s*([^\n]+)'
                ]
                
                for pattern in position_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    if matches:
                        log(f"✅ 正则匹配找到 {len(matches)} 个匹配: {pattern}")
        except Exception as e:
            log(f"⚠️ 页面文本提取失败: {e}")
        
        # 方式3: 通过JavaScript执行提取
        try:
            log("🔄 执行JavaScript提取数据...")
            
            # 尝试执行页面中的JavaScript来获取数据
            js_extract_script = """
            // 尝试获取页面中的数据
            const positions = [];
            
            // 方法1: 查找包含岗位信息的元素
            const positionElements = document.querySelectorAll('[class*="position"], [class*="job"], [class*="recruit"]');
            positionElements.forEach((el, index) => {
                const text = el.textContent?.trim();
                if (text && text.length > 20) {
                    positions.push({
                        index: index,
                        text: text.substring(0, 100),
                        className: el.className,
                        tagName: el.tagName
                    });
                }
            });
            
            // 方法2: 查找包含"岗位"、"职位"等关键词的元素
            const keywords = ['岗位', '职位', '工作地点', '岗位职责', '任职要求'];
            keywords.forEach(keyword => {
                const elements = document.querySelectorAll(`:contains("${keyword}")`);
                elements.forEach((el, index) => {
                    const text = el.textContent?.trim();
                    if (text && text.length > 10) {
                        positions.push({
                            keyword: keyword,
                            text: text.substring(0, 150),
                            index: index
                        });
                    }
                });
            });
            
            return positions;
            """
            
            js_result = await page.evaluate(js_extract_script)
            if js_result and len(js_result) > 0:
                log(f"✅ JavaScript提取到 {len(js_result)} 条数据")
                positions.extend(js_result)
        except Exception as e:
            log(f"⚠️ JavaScript提取失败: {e}")
        
        # 方式4: 截图保存页面
        try:
            screenshot_path = os.path.join(OUTPUT_DIR, "page_screenshot.png")
            await page.screenshot(path=screenshot_path, full_page=True)
            log(f"📸 页面截图保存: {screenshot_path}")
        except Exception as e:
            log(f"⚠️ 截图失败: {e}")
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if positions:
            log(f"🎉 成功从页面中提取到 {len(positions)} 条数据")
            return positions
        else:
            log("❌ 未从页面中提取到数据")
            return None
            
    except ImportError:
        log("❌ 未安装Playwright，请运行: pip install playwright")
        return None
    except Exception as e:
        log(f"❌ 页面爬取失败: {e}")
        return None


def extract_standard_fields(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """从原始数据中提取标准字段"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_data)) % 10000:04d}"
    
    # 尝试从原始文本中提取信息
    raw_text = str(raw_data.get("text", "") or raw_data.get("rawText", ""))
    
    # 简单的信息提取（实际应用中需要更复杂的解析）
    position_name = ""
    work_location = ""
    
    # 尝试提取岗位名称
    name_patterns = [
        r'岗位[：:]\s*([^\n]+)',
        r'职位[：:]\s*([^\n]+)',
        r'([^\n]{5,20})(?:工程师|开发|产品|运营|设计)'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, raw_text)
        if match:
            position_name = match.group(1).strip()
            break
    
    # 尝试提取工作地点
    location_patterns = [
        r'工作地点[：:]\s*([^\n]+)',
        r'地点[：:]\s*([^\n]+)',
        r'(北京|上海|广州|深圳|杭州|成都|武汉|南京|西安)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, raw_text)
        if match:
            work_location = match.group(1).strip()
            break
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": position_name or "未知岗位",
        "workLocation": work_location or "未知地点",
        "positionCategory": "",
        "publishTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "detailUrl": "https://zhaopin.kuaishou.cn",
        "department": "",
        "educationRequirement": "",
        "workExperience": "",
        "jobResponsibilities": raw_text[:500] if raw_text else "",
        "jobRequirements": "",
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "page_scraper",
        "source": "kuaishou_page_scraper",
        
        # 原始数据
        "rawData": raw_data
    }


def save_position(position: Dict[str, Any]) -> str:
    """保存单个岗位数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    position_id = position.get("positionId", "unknown")
    filename = f"ks_position_{position_id}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(position, f, ensure_ascii=False, indent=2)
        
        log(f"💾 保存: {filename}")
        return filepath
    except Exception as e:
        log(f"❌ 保存失败: {e}")
        return ""


async def crawl_from_page() -> Dict[str, Any]:
    """从页面爬取数据"""
    log("🚀 开始页面爬取")
    start_time = datetime.now()
    
    # 从页面中获取数据
    raw_positions = await scrape_data_from_page()
    
    if not raw_positions:
        log("❌ 无法从页面获取数据")
        return {"success": False, "message": "无法从页面获取数据"}
    
    # 处理数据
    saved_files = []
    processed_positions = []
    
    for i, raw_position in enumerate(raw_positions, 1):
        log(f"📝 处理第 {i} 条数据...")
        standard_position = extract_standard_fields(raw_position)
        filepath = save_position(standard_position)
        if filepath:
            saved_files.append(filepath)
        processed_positions.append(standard_position)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "processed_positions": len(processed_positions),
        "saved_files": len(saved_files),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_mode": "page_scraper"
    }
    
    log("=" * 60)
    log(f"🎉 页面爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 原始数据: {len(raw_positions)}条")
    log(f"   • 处理岗位: {len(processed_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 页面爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 从页面中提取岗位信息")
    print("   3. 处理并保存数据")
    print("   4. 自动保存页面截图")
    print()
    
    try:
        stats = asyncio.run(crawl_from_page())
        
        if stats.get("success"):
            print()
            print("🎉 页面爬取成功！")
            print()
            print("📊 爬取统计:")
            print(f"   原始数据: {stats['raw_positions']}条")
            print(f"   处理岗位: {stats['processed_positions']}个")
            print(f"   保存文件: {stats['saved_files']}个")
            print(f"   总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   输出目录: {stats['output_dir']}")
            print()
            
            # 显示保存的文件
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    print("📁 保存的文件:")
                    json_files = [f for f in files if f.endswith('.json')]
                    screenshot_files = [f for f in files if f.endswith('.png')]
                    
                    if json_files:
                        print("  JSON文件:")
                        for i, filename in enumerate(json_files[:3], 1):
                            print(f"    {i}. {filename}")
                        if len(json_files) > 3:
                            print(f"    ... 还有 {len(json_files) - 3} 个JSON文件")
                    
                    if screenshot_files:
                        print("  截图文件:")
                        for filename in screenshot_files:
                            print(f"    • {filename}")
        else:
            print("❌ 爬取失败")
            print(f"   错误信息: {stats.get('message', '未知错误')}")
            
    except KeyboardInterrupt:
        print()
        log("⏹️ 用户中断爬取")
    except Exception as e:
        log(f"❌ 程序异常: {e}")
    
    print()
    print("💡 提示:")
    print("  1. 查看数据: ls output/ks_page_scraper/")
    print("  2. 查看日志: cat logs/page_scraper.log")
    print("  3. 查看截图: open output/ks_page_scraper/page_screenshot.png")
    print("  4. 继续爬取: 重新运行此脚本")
    print()


if __name__ == "__main__":
    main()