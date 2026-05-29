#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘简单完整爬取器
修复JavaScript错误，确保能爬取到数据
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🚀 快手招聘简单完整爬取器")
print("=" * 80)
print("修复JavaScript错误，确保能爬取到数据")
print()

# 输出目录
OUTPUT_DIR = "output/ks_simple_full"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/simple_full_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def simple_crawl_all_data() -> Optional[List[str]]:
    """
    简单的数据爬取：获取页面所有文本
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器（显示窗口）
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
            log("⚠️ 未找到社会招聘按钮")
        
        # 滚动加载内容
        log("🔄 滚动页面加载内容...")
        for i in range(10):
            await page.evaluate(f"window.scrollTo(0, {1000 * (i + 1)})")
            await page.wait_for_timeout(1500)
            log(f"📜 滚动 {i+1}/10 次")
        
        # 等待加载
        await page.wait_for_timeout(5000)
        
        # 方法1: 获取整个页面文本
        log("🔍 获取整个页面文本...")
        all_text = await page.text_content('body')
        
        if all_text:
            log(f"✅ 获取到页面文本，长度: {len(all_text)} 字符")
            
            # 保存原始文本
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            text_file = os.path.join(OUTPUT_DIR, f"ks_page_text_{timestamp}.txt")
            
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(all_text)
            
            log(f"💾 保存页面文本: {text_file}")
        
        # 方法2: 获取页面HTML
        log("🔍 获取页面HTML...")
        html_content = await page.content()
        
        if html_content:
            log(f"✅ 获取到页面HTML，长度: {len(html_content)} 字符")
            
            # 保存HTML
            html_file = os.path.join(OUTPUT_DIR, f"ks_page_html_{timestamp}.html")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            log(f"💾 保存页面HTML: {html_file}")
        
        # 方法3: 截图
        log("📸 截图页面...")
        screenshot_file = os.path.join(OUTPUT_DIR, f"ks_screenshot_{timestamp}.png")
        await page.screenshot(path=screenshot_file, full_page=True)
        log(f"💾 保存截图: {screenshot_file}")
        
        # 方法4: 简单的JavaScript提取（修复语法）
        log("🔄 使用简单JavaScript提取数据...")
        
        # 修复的JavaScript代码
        simple_js = """
        (function() {
            // 收集所有文本节点
            const allTexts = [];
            const walker = document.createTreeWalker(
                document.body,
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text && text.length > 20) {
                    allTexts.push(text);
                }
            }
            
            // 返回结果
            return {
                totalTexts: allTexts.length,
                texts: allTexts.slice(0, 100) // 只取前100个
            };
        })();
        """
        
        try:
            js_result = await page.evaluate(simple_js)
            if js_result:
                log(f"✅ JavaScript提取到 {js_result['totalTexts']} 个文本节点")
                
                # 保存JavaScript提取结果
                js_file = os.path.join(OUTPUT_DIR, f"ks_js_extract_{timestamp}.json")
                with open(js_file, 'w', encoding='utf-8') as f:
                    json.dump(js_result, f, ensure_ascii=False, indent=2)
                
                log(f"💾 保存JS提取结果: {js_file}")
        except Exception as e:
            log(f"⚠️ JavaScript提取失败: {e}")
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        # 返回所有文件路径
        files = []
        if os.path.exists(text_file):
            files.append(text_file)
        if os.path.exists(html_file):
            files.append(html_file)
        if os.path.exists(screenshot_file):
            files.append(screenshot_file)
        if os.path.exists(js_file):
            files.append(js_file)
        
        return files
        
    except Exception as e:
        log(f"❌ 爬取失败: {e}")
        return None


def extract_positions_from_text(text: str) -> List[Dict[str, Any]]:
    """从文本中提取岗位信息"""
    positions = []
    
    if not text:
        return positions
    
    log("🔍 从文本中提取岗位信息...")
    
    # 清理文本
    lines = text.split('\n')
    
    # 定义岗位相关关键词
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理',
        '策划', '销售', '市场', '客服', '行政', '财务',
        'Java', 'Python', '前端', '后端', '数据', 'AI',
        '人工智能', '机器学习', '深度学习', '大数据'
    ]
    
    # 定义地点关键词
    location_keywords = [
        '北京', '上海', '广州', '深圳', '杭州', '成都',
        '武汉', '南京', '西安', '苏州', '重庆', '天津',
        '长沙', '合肥', '郑州', '济南', '青岛', '大连',
        '沈阳', '长春', '哈尔滨', '厦门', '福州', '南宁'
    ]
    
    # 分析每一行
    for line in lines:
        line = line.strip()
        if len(line) < 20:
            continue
        
        # 检查是否包含岗位关键词
        has_position_keyword = any(keyword in line for keyword in position_keywords)
        has_location_keyword = any(keyword in line for keyword in location_keywords)
        
        if has_position_keyword or has_location_keyword:
            # 尝试提取岗位名称
            position_name = ""
            for keyword in position_keywords:
                if keyword in line:
                    # 提取包含关键词的部分
                    start = max(0, line.find(keyword) - 20)
                    end = min(len(line), line.find(keyword) + 30)
                    position_name = line[start:end].strip()
                    break
            
            # 提取工作地点
            work_location = ""
            for keyword in location_keywords:
                if keyword in line:
                    work_location = keyword
                    break
            
            # 提取发布时间（如果有）
            publish_time = ""
            time_patterns = [
                r'(\d{4}\.\d{2}\.\d{2})',
                r'(\d{4}-\d{2}-\d{2})',
                r'(\d{2}/\d{2}/\d{4})'
            ]
            
            for pattern in time_patterns:
                match = re.search(pattern, line)
                if match:
                    publish_time = match.group(1)
                    break
            
            # 提取工作经验
            work_experience = ""
            exp_patterns = [
                r'(\d+[-~]?\d*年)',
                r'(\d+-\d+年)',
                r'([一二三四五六七八九十]+年)'
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, line)
                if match:
                    work_experience = match.group(1)
                    break
            
            # 创建岗位数据
            position_data = {
                "rawText": line[:200],  # 只保存前200个字符
                "positionName": position_name or line[:30],
                "workLocation": work_location,
                "publishTime": publish_time or datetime.now().strftime("%Y-%m-%d"),
                "workExperience": work_experience,
                "extractedTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            positions.append(position_data)
    
    log(f"✅ 从文本中提取到 {len(positions)} 个岗位")
    return positions


def save_positions_to_json(positions: List[Dict[str, Any]]) -> str:
    """保存岗位数据到JSON文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(OUTPUT_DIR, f"ks_extracted_positions_{timestamp}.json")
    
    data = {
        "metadata": {
            "extractTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "source": "text_analysis"
        },
        "positions": positions
    }
    
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        log(f"💾 保存提取的岗位数据: {json_file}")
        return json_file
    except Exception as e:
        log(f"❌ 保存岗位数据失败: {e}")
        return ""


async def main_async():
    """异步主函数"""
    log("🚀 开始简单完整爬取")
    start_time = datetime.now()
    
    # 爬取数据
    files = await simple_crawl_all_data()
    
    if not files:
        log("❌ 爬取失败，无文件生成")
        return {"success": False, "message": "爬取失败"}
    
    log(f"✅ 爬取完成，生成 {len(files)} 个文件")
    
    # 处理文本文件
    text_files = [f for f in files if f.endswith('.txt')]
    if text_files:
        text_file = text_files[0]
        log(f"📄 处理文本文件: {text_file}")
        
        # 读取文本
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # 提取岗位信息
            positions = extract_positions_from_text(text_content)
            
            # 保存岗位数据
            if positions:
                json_file = save_positions_to_json(positions)
                files.append(json_file)
        except Exception as e:
            log(f"⚠️ 处理文本文件失败: {e}")
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "total_files": len(files),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 70)
    log(f"🎉 简单完整爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 生成文件: {len(files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 简单完整爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 点击社会招聘")
    print("   3. 滚动页面加载所有内容")
    print("   4. 保存页面文本、HTML、截图")
    print("   5. 从文本中提取岗位信息")
    print("   6. 保存所有数据")
    print()
    
    try:
        stats = asyncio.run(main_async())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 简单完整爬取成功！")
            print("✅" * 35)
            print()
            print("📊 爬取结果:")
            print(f"   📁 生成文件: {stats['total_files']} 个")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📂 输出目录: {stats['output_dir']}")
            print()
            
            # 显示生成的文件
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    print("📁 生成的文件列表:")
                    
                    # 按类型分组
                    txt_files = [f for f in files if f.endswith('.txt')]
                    html_files = [f for f in files if f.endswith('.html')]
                    json_files = [f for f in files if f.endswith('.json')]
                    png_files = [f for f in files if f.endswith('.png')]
                    
                    if txt_files:
                        print(f"   📄 文本文件 ({len(txt_files)}):")
                        for f in txt_files[:3]:
                            print(f"      • {f}")
                        if len(txt_files) > 3:
                            print(f"      ... 还有 {len(txt_files) - 3} 个")
                    
                    if html_files:
                        print(f"   🌐 HTML文件 ({len(html_files)}):")
                        for f in html_files[:2]:
                            print(f"      • {f}")
                    
                    if json_files:
                        print(f"   📊 JSON文件 ({len(json_files)}):")
                        for f in json_files[:3]:
                            print(f"      • {f}")
                        if len(json_files) > 3:
                            print(f"      ... 还有 {len(json_files) - 3} 个")
                    
                    if png_files:
                        print(f"   📸 截图文件 ({len(png_files)}):")
                        for f in png_files:
                            print(f"      • {f}")
                    
                    print()
                    print("💡 下一步操作:")
                    print("   1. 查看文本内容: cat output/ks_simple_full/*.txt | head -50")
                    print("   2. 查看岗位数据: cat output/ks_simple_full/*.json | head -100")
                    print("   3. 查看截图: open output/ks_simple_full/*.png")
                    print("   4. 分析数据: 使用提取的JSON文件进行分析")
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