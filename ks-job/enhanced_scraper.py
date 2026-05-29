#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘增强版爬取器
基于页面爬取的成功经验，增强数据提取和批量处理
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

print("=" * 70)
print("🚀 快手招聘增强版爬取器")
print("=" * 70)
print("基于成功的页面爬取经验，增强数据提取和批量处理")
print()

# 输出目录
OUTPUT_DIR = "output/ks_enhanced"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/enhanced_scraper.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def extract_detailed_positions() -> Optional[List[Dict[str, Any]]]:
    """
    提取详细的岗位信息
    
    Returns:
        详细的岗位数据列表 或 None
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器提取详细数据...")
        
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
        await page.wait_for_timeout(3000)
        
        # 点击"社会招聘"
        try:
            await page.click("a:has-text('社会招聘')", timeout=5000)
            log("✅ 点击: 社会招聘")
            await page.wait_for_timeout(3000)
        except:
            log("⚠️ 未找到社会招聘按钮")
        
        # 滚动加载更多内容
        log("🔄 滚动页面加载更多内容...")
        for i in range(10):  # 滚动10次
            await page.evaluate(f"window.scrollTo(0, {1000 * (i + 1)})")
            await page.wait_for_timeout(1500)
            log(f"📜 滚动 {i+1}/10 次")
        
        # 等待内容加载
        await page.wait_for_timeout(5000)
        
        # 提取页面中的所有文本
        log("🔍 提取页面中的所有文本内容...")
        page_content = await page.content()
        
        # 使用JavaScript提取更详细的数据
        log("🔄 使用JavaScript提取详细数据...")
        
        js_extract_script = """
        // 提取页面中的所有岗位信息
        const positions = [];
        
        // 查找所有包含岗位信息的元素
        const allElements = document.querySelectorAll('div, span, li, td, tr, a, p');
        
        allElements.forEach((element, index) => {
            const text = element.textContent?.trim();
            
            // 如果文本包含岗位相关关键词且有一定长度
            if (text && text.length > 20) {
                const keywords = ['工程师', '开发', '产品', '运营', '设计', '分析', '测试', '运维', '算法'];
                const hasKeyword = keywords.some(keyword => text.includes(keyword));
                
                if (hasKeyword) {
                    // 提取可能的岗位信息
                    const positionInfo = {
                        index: index,
                        text: text,
                        html: element.outerHTML.substring(0, 500),
                        tagName: element.tagName,
                        className: element.className,
                        id: element.id,
                        rect: element.getBoundingClientRect()
                    };
                    
                    positions.push(positionInfo);
                }
            }
        });
        
        // 去重（基于文本内容）
        const uniquePositions = [];
        const seenTexts = new Set();
        
        positions.forEach(pos => {
            const normalizedText = pos.text.replace(/\\s+/g, ' ').trim();
            if (!seenTexts.has(normalizedText)) {
                seenTexts.add(normalizedText);
                uniquePositions.push(pos);
            }
        });
        
        return uniquePositions;
        """
        
        js_result = await page.evaluate(js_extract_script)
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if js_result and len(js_result) > 0:
            log(f"🎉 成功提取到 {len(js_result)} 条详细数据")
            return js_result
        else:
            log("❌ 未提取到详细数据")
            return None
            
    except ImportError:
        log("❌ 未安装Playwright，请运行: pip install playwright")
        return None
    except Exception as e:
        log(f"❌ 详细数据提取失败: {e}")
        return None


def parse_position_text(text: str) -> Dict[str, Any]:
    """
    解析岗位文本，提取结构化信息
    
    Args:
        text: 原始岗位文本
        
    Returns:
        结构化的岗位信息
    """
    # 初始化结果
    result = {
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": "",
        "department": "",
        "educationRequirement": "",
        "jobResponsibilities": "",
        "jobRequirements": ""
    }
    
    # 清理文本
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # 尝试提取岗位名称（通常在最前面）
    name_patterns = [
        r'^([^【】\[\]0-9]{5,30}?)(?:工程师|开发|产品|运营|设计|分析|测试|运维|算法|经理|专员|助理)',
        r'([^【】\[\]]+?)(?:工程师|开发|产品|运营)',
        r'职位名称[：:]\s*([^\n]+)',
        r'岗位[：:]\s*([^\n]+)'
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["positionName"] = match.group(1).strip()
            break
    
    # 尝试提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', clean_text)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    
    # 尝试提取工作地点
    location_patterns = [
        r'工作地点[：:]\s*([^\n]+)',
        r'地点[：:]\s*([^\n]+)',
        r'([北京上海广州深圳杭州成都武汉南京西安苏州重庆天津]{2,10})'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["workLocation"] = match.group(1).strip()
            break
    
    # 尝试提取工作经验
    experience_patterns = [
        r'工作年限[：:]\s*([^\n]+)',
        r'经验[：:]\s*([^\n]+)',
        r'(\d+[-~]?\d*年)'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["workExperience"] = match.group(1).strip()
            break
    
    # 尝试提取发布时间
    time_patterns = [
        r'更新时间[：:]\s*([^\n]+)',
        r'发布时间[：:]\s*([^\n]+)',
        r'(\d{4}\.\d{2}\.\d{2})',
        r'(\d{4}-\d{2}-\d{2})'
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["publishTime"] = match.group(1).strip()
            break
    
    # 尝试提取部门信息
    department_patterns = [
        r'部门[：:]\s*([^\n]+)',
        r'事业部[：:]\s*([^\n]+)',
        r'线[：:]\s*([^\n]+)'
    ]
    
    for pattern in department_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["department"] = match.group(1).strip()
            break
    
    # 尝试提取学历要求
    education_patterns = [
        r'学历[：:]\s*([^\n]+)',
        r'教育[：:]\s*([^\n]+)',
        r'(本科|硕士|博士|大专|高中)'
    ]
    
    for pattern in education_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["educationRequirement"] = match.group(1).strip()
            break
    
    # 工作职责和任职要求（简化处理）
    if len(clean_text) > 100:
        result["jobResponsibilities"] = clean_text[:300]
        result["jobRequirements"] = clean_text[300:600] if len(clean_text) > 600 else ""
    
    return result


def create_standard_position(raw_data: Dict[str, Any], parsed_info: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_data)) % 10000:04d}"
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": parsed_info["positionName"] or "未知岗位",
        "workLocation": parsed_info["workLocation"] or "未知地点",
        "positionCategory": parsed_info["positionCategory"] or "",
        "publishTime": parsed_info["publishTime"] or datetime.now().strftime("%Y-%m-%d"),
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position_id}",
        "department": parsed_info["department"] or "",
        "educationRequirement": parsed_info["educationRequirement"] or "",
        "workExperience": parsed_info["workExperience"] or "",
        "jobResponsibilities": parsed_info["jobResponsibilities"] or "",
        "jobRequirements": parsed_info["jobRequirements"] or "",
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "enhanced_scraper",
        "source": "kuaishou_enhanced",
        
        # 解析信息
        "parsedInfo": parsed_info,
        
        # 原始数据（简化）
        "rawData": {
            "text": raw_data.get("text", "")[:500],
            "index": raw_data.get("index", 0)
        }
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


def save_batch_report(positions: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """保存批量报告"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"ks_batch_report_{timestamp}.json"
    report_path = os.path.join(OUTPUT_DIR, report_file)
    
    report_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "outputDir": OUTPUT_DIR,
            "stats": stats
        },
        "summary": {
            "positionNames": [p.get("positionName", "") for p in positions],
            "workLocations": list(set([p.get("workLocation", "") for p in positions if p.get("workLocation")])),
            "positionCategories": list(set([p.get("positionCategory", "") for p in positions if p.get("positionCategory")]))
        },
        "positions": positions[:50]  # 只保存前50个岗位的详细信息
    }
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        log(f"📊 保存批量报告: {report_file}")
        return report_path
    except Exception as e:
        log(f"❌ 保存报告失败: {e}")
        return ""


async def enhanced_crawl() -> Dict[str, Any]:
    """增强版爬取"""
    log("🚀 开始增强版爬取")
    start_time = datetime.now()
    
    # 提取详细数据
    raw_positions = await extract_detailed_positions()
    
    if not raw_positions:
        log("❌ 无法提取详细数据")
        return {"success": False, "message": "无法提取详细数据"}
    
    log(f"📊 提取到 {len(raw_positions)} 条原始数据")
    
    # 处理数据
    processed_positions = []
    saved_files = []
    
    for i, raw_position in enumerate(raw_positions, 1):
        if i % 10 == 0:
            log(f"📝 处理进度: {i}/{len(raw_positions)}")
        
        try:
            # 解析文本
            parsed_info = parse_position_text(raw_position.get("text", ""))
            
            # 创建标准化岗位
            standard_position = create_standard_position(raw_position, parsed_info)
            
            # 保存数据
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            
            processed_positions.append(standard_position)
            
        except Exception as e:
            log(f"⚠️ 处理第 {i} 条数据失败: {e}")
            continue
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    # 生成统计
    position_names = [p.get("positionName", "") for p in processed_positions]
    work_locations = list(set([p.get("workLocation", "") for p in processed_positions if p.get("workLocation")]))
    position_categories = list(set([p.get("positionCategory", "") for p in processed_positions if p.get("positionCategory")]))
    
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "processed_positions": len(processed_positions),
        "saved_files": len(saved_files),
        "elapsed_time": elapsed_time,
        "unique_position_names": len(set(position_names)),
        "unique_work_locations": len(work_locations),
        "unique_position_categories": len(position_categories),
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_mode": "enhanced"
    }
    
    # 保存批量报告
    report_path = save_batch_report(processed_positions, stats)
    
    log("=" * 60)
    log(f"🎉 增强版爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 原始数据: {len(raw_positions)}条")
    log(f"   • 处理岗位: {len(processed_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 唯一岗位名: {len(set(position_names))}个")
    log(f"   • 工作地点: {', '.join(work_locations[:5])}{'...' if len(work_locations) > 5 else ''}")
    log(f"   • 岗位类别: {', '.join(position_categories[:5])}{'...' if len(position_categories) > 5 else ''}")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log(f"   • 报告文件: {os.path.basename(report_path) if report_path else '无'}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 增强版爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 提取详细页面数据")
    print("   3. 智能解析岗位信息")
    print("   4. 批量保存标准化数据")
    print("   5. 生成数据报告")
    print()
    
    try:
        stats = asyncio.run(enhanced_crawl())
        
        if stats.get("success"):
            print()
            print("🎉 增强版爬取成功！")
            print()
            print("📊 爬取统计:")
            print(f"   原始数据: {stats['raw_positions']}条")
            print(f"   处理岗位: {stats['processed_positions']}个")
            print(f"   保存文件: {stats['saved_files']}个")
            print(f"   唯一岗位名: {stats['unique_position_names']}个")
            print(f"   工作地点: {stats['unique_work_locations']}个")
            print(f"   岗位类别: {stats['unique_position_categories']}个")
            print(f"   总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   输出目录: {stats['output_dir']}")
            print()
            
            # 显示保存的文件
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    json_files = [f for f in files if f.endswith('.json')]
                    report_files = [f for f in json_files if 'report' in f]
                    position_files = [f for f in json_files if 'position' in f]
                    
                    if report_files:
                        print("📁 报告文件:")
                        for filename in report_files[:3]:
                            print(f"  • {filename}")
                    
                    if position_files:
                        print(f"📁 岗位文件: {len(position_files)} 个")
                        if position_files:
                            print(f"  示例: {position_files[0]}")
                            if len(position_files) > 1:
                                print(f"        ... 还有 {len(position_files) - 1} 个文件")
        else:
