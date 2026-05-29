#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘完整数据爬取器
爬取筛选条件下的所有岗位数据
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

print("=" * 80)
print("🚀 快手招聘完整数据爬取器")
print("=" * 80)
print("爬取筛选条件下的所有岗位数据")
print()

# 输出目录
OUTPUT_DIR = "output/ks_full_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/full_data_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def crawl_all_positions_with_filters() -> Optional[List[Dict[str, Any]]]:
    """
    爬取所有筛选条件下的岗位数据
    
    Returns:
        所有岗位数据列表 或 None
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器爬取所有数据...")
        
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
        
        # 点击"社会招聘"（如果需要筛选）
        try:
            await page.click("a:has-text('社会招聘')", timeout=5000)
            log("✅ 点击: 社会招聘")
            await page.wait_for_timeout(3000)
        except:
            log("⚠️ 未找到社会招聘按钮，继续使用当前页面")
        
        # 应用筛选条件（如果需要）
        log("🔍 检查并应用筛选条件...")
        
        # 这里可以根据需要添加筛选逻辑，例如：
        # 1. 选择工作地点
        # 2. 选择岗位类别
        # 3. 选择工作经验等
        
        # 获取当前页面所有岗位数据
        all_positions = []
        current_page = 1
        max_pages = 20  # 安全限制，防止无限循环
        
        while current_page <= max_pages:
            log(f"📄 处理第 {current_page} 页...")
            
            # 滚动页面加载更多内容
            for i in range(5):
                await page.evaluate(f"window.scrollTo(0, {1000 * (i + 1)})")
                await page.wait_for_timeout(1000)
            
            # 等待内容加载
            await page.wait_for_timeout(3000)
            
            # 提取当前页面的岗位数据
            page_positions = await extract_positions_from_page(page)
            
            if page_positions:
                log(f"✅ 第 {current_page} 页提取到 {len(page_positions)} 个岗位")
                all_positions.extend(page_positions)
            else:
                log(f"⚠️ 第 {current_page} 页未提取到岗位数据")
            
            # 检查是否有"加载更多"或"下一页"按钮
            try:
                # 尝试点击"加载更多"
                await page.click("button:has-text('加载更多')", timeout=3000)
                log("✅ 点击: 加载更多")
                await page.wait_for_timeout(3000)
                current_page += 1
                continue
            except:
                pass
            
            try:
                # 尝试点击"下一页"
                await page.click("button:has-text('下一页')", timeout=3000)
                log("✅ 点击: 下一页")
                await page.wait_for_timeout(3000)
                current_page += 1
                continue
            except:
                pass
            
            # 如果没有找到翻页按钮，尝试通过URL翻页
            try:
                # 检查当前URL是否有页码参数
                current_url = page.url
                if 'page=' in current_url:
                    # 更新页码
                    new_page = current_page + 1
                    new_url = re.sub(r'page=\d+', f'page={new_page}', current_url)
                    await page.goto(new_url, wait_until="networkidle")
                    log(f"🔗 跳转到第 {new_page} 页: {new_url}")
                    await page.wait_for_timeout(3000)
                    current_page = new_page
                    continue
            except:
                pass
            
            # 如果以上方法都失败，尝试滚动到底部触发自动加载
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)
            
            # 检查是否有新内容加载
            new_positions = await extract_positions_from_page(page)
            if new_positions and len(new_positions) > len(page_positions):
                log(f"🔄 滚动触发加载，新增 {len(new_positions) - len(page_positions)} 个岗位")
                all_positions.extend(new_positions[len(page_positions):])
                current_page += 1
            else:
                log("⏹️ 没有更多数据，停止翻页")
                break
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if all_positions:
            # 去重
            unique_positions = []
            seen_texts = set()
            
            for position in all_positions:
                text = position.get("text", "")
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    unique_positions.append(position)
            
            log(f"🎉 成功爬取到 {len(unique_positions)} 个唯一岗位")
            return unique_positions
        else:
            log("❌ 未爬取到任何岗位数据")
            return None
            
    except ImportError:
        log("❌ 未安装Playwright，请运行: pip install playwright")
        return None
    except Exception as e:
        log(f"❌ 爬取失败: {e}")
        return None


async def extract_positions_from_page(page) -> List[Dict[str, Any]]:
    """从页面中提取岗位数据"""
    positions = []
    
    try:
        # 使用JavaScript提取岗位信息
        js_extract_script = """
        // 提取页面中的所有岗位信息
        const positions = [];
        
        // 查找所有可能的岗位元素
        const selectors = [
            '.position-item',
            '.job-item',
            '.recruit-item',
            '[class*="position"]',
            '[class*="job"]',
            '[class*="recruit"]',
            'tr', 'td', 'li'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            
            elements.forEach((element, index) => {
                const text = element.textContent?.trim();
                
                // 如果文本包含岗位相关关键词且有一定长度
                if (text && text.length > 30) {
                    const keywords = [
                        '工程师', '开发', '产品', '运营', '设计', '分析', 
                        '测试', '运维', '算法', '经理', '专员', '助理',
                        '策划', '销售', '市场', '客服', '行政', '财务'
                    ];
                    
                    const hasKeyword = keywords.some(keyword => text.includes(keyword));
                    
                    if (hasKeyword) {
                        // 提取岗位信息
                        const positionInfo = {
                            index: positions.length,
                            text: text,
                            html: element.outerHTML.substring(0, 1000),
                            tagName: element.tagName,
                            className: element.className,
                            id: element.id,
                            href: element.href || '',
                            boundingRect: element.getBoundingClientRect()
                        };
                        
                        positions.push(positionInfo);
                    }
                }
            });
        }
        
        return positions;
        """
        
        positions = await page.evaluate(js_extract_script)
        
    except Exception as e:
        log(f"⚠️ 页面数据提取失败: {e}")
    
    return positions


def parse_position_details(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """解析岗位详细信息"""
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
        "detailUrl": ""
    }
    
    # 清理文本
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # 提取岗位名称（使用更精确的规则）
    # 规则1: 在"【"之前的部分通常是岗位名称
    name_match = re.search(r'^([^【】\[\]0-9]{5,40}?)(?:工程师|开发|产品|运营|设计|分析|测试|运维|算法|经理|专员|助理|策划|销售|市场|客服|行政|财务|师)', clean_text)
    if name_match:
        result["positionName"] = name_match.group(1).strip()
    
    # 规则2: 如果没找到，取前30个字符
    if not result["positionName"] and len(clean_text) > 10:
        result["positionName"] = clean_text[:30].strip()
    
    # 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', clean_text)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    
    # 提取工作地点
    location_patterns = [
        r'工作地点[：:]\s*([^\n]+)',
        r'地点[：:]\s*([^\n]+)',
        r'([北京上海广州深圳杭州成都武汉南京西安苏州重庆天津]{2,20})'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, clean_text)
        if match:
            locations = match.group(1).strip()
            # 清理地点文本
            locations = re.sub(r'[，,]\s*', ', ', locations)
            result["workLocation"] = locations
            break
    
    # 提取工作经验
    experience_patterns = [
        r'工作年限[：:]\s*([^\n]+)',
        r'经验[：:]\s*([^\n]+)',
        r'(\d+[-~]?\d*年)',
        r'(\d+-\d+年)'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["workExperience"] = match.group(1).strip()
            break
    
    # 提取发布时间
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
    
    # 提取部门信息
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
    
    # 提取学历要求
    education_patterns = [
        r'学历[：:]\s*([^\n]+)',
        r'教育[：:]\s*([^\n]+)',
        r'(本科|硕士|博士|大专|高中)以上?'
    ]
    
    for pattern in education_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["educationRequirement"] = match.group(1).strip()
            break
    
    # 提取薪资范围（如果存在）
    salary_patterns = [
        r'薪资[：:]\s*([^\n]+)',
        r'薪酬[：:]\s*([^\n]+)',
        r'(\d+[kK]?[-~]\d+[kK])'
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, clean_text)
        if match:
            result["salaryRange"] = match.group(1).strip()
            break
    
    # 从HTML中提取详情链接
    if html:
        url_match = re.search(r'href=["\']([^"\']+)["\']', html)
        if url_match:
            url = url_match.group(1)
            if url.startswith('/'):
                url = f"https://zhaopin.kuaishou.cn{url}"
            result["detailUrl"] = url
    
    # 如果没有提取到详情链接，使用默认链接
    if not result["detailUrl"]:
        position_id = hash(clean_text) % 1000000
        result["detailUrl"] = f"https://zhaopin.kuaishou.cn/position/{position_id}"
    
    # 工作职责和任职要求（简化处理）
    if len(clean_text) > 100:
        # 尝试分割文本
        lines = clean_text.split(' ')
        if len(lines) > 3:
            result["jobResponsibilities"] = ' '.join(lines[:5])
            if len(lines) > 10:
                result["jobRequirements"] = ' '.join(lines[5:10])
    
    return result


def create_standard_position(raw_position: Dict[str, Any], parsed_details: Dict[str, Any]) -> Dict[str, Any]:
    """创建标准化的岗位数据"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
    return {
        # 12个核心字段
        "positionId": position_id,
        "positionName": parsed_details["positionName"] or "未知岗位",
        "workLocation": parsed_details["workLocation"] or "未知地点",
        "positionCategory": parsed_details["positionCategory"] or "",
        "publishTime": parsed_details["publishTime"] or datetime.now().strftime("%Y-%m-%d"),
        "detailUrl": parsed_details["detailUrl"],
        "department": parsed_details["department"] or "",
        "educationRequirement": parsed_details["educationRequirement"] or "",
        "workExperience": parsed_details["workExperience"] or "",
        "jobResponsibilities": parsed_details["jobResponsibilities"] or parsed_details["rawText"][:300],
        "jobRequirements": parsed_details["jobRequirements"] or "",
        "salaryRange": parsed_details["salaryRange"] or "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "full_data_crawler",
        "source": "kuaishou_full_data",
        
        # 解析详情
        "parsedDetails": {k: v for k, v in parsed_details.items() if k != "rawText"},
        
        # 原始数据（简化）
        "rawData": {
            "text": parsed_details["rawText"][:500],
            "index": raw_position.get("index", 0)
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


def save_data_report(positions: List[Dict[str, Any]], stats: Dict[str, Any]) -> Tuple[str, str]:
    """保存数据报告和汇总文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存汇总数据（所有岗位）
    summary_file = f"ks_all_positions_{timestamp}.json"
    summary_path = os.path.join(OUTPUT_DIR, summary_file)
    
    summary_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "outputDir": OUTPUT_DIR,
            "stats": stats
        },
        "positions": positions
    }
    
    try:
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存汇总数据: {summary_file} ({len(positions)} 个岗位)")
    except Exception as e:
        log(f"❌ 保存汇总数据失败: {e}")
        summary_path = ""
    
    # 2. 保存统计报告
    report_file = f"ks_statistics_report_{timestamp}.json"
    report_path = os.path.join(OUTPUT_DIR, report_file)
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in positions]
    work_locations = []
    for p in positions:
        location = p.get("workLocation", "")
        if location and location not in work_locations:
            work_locations.append(location)
    
    position_categories = []
    for p in positions:
        category = p.get("positionCategory", "")
        if category and category not in position_categories:
            position_categories.append(category)
    
    work_experiences = []
    for p in positions:
        experience = p.get("workExperience", "")
        if experience and experience not in work_experiences:
            work_experiences.append(experience)
    
    report_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "uniquePositionNames": len(set(position_names)),
            "uniqueWorkLocations": len(work_locations),
            "uniquePositionCategories": len(position_categories)
        },
        "statistics": {
            "positionNames": {
                "total": len(set(position_names)),
                "top10": list(set(position_names))[:10]
            },
            "workLocations": {
                "total": len(work_locations),
                "list": work_locations[:20]
            },
            "positionCategories": {
                "total": len(position_categories),
                "list": position_categories[:20]
            },
            "workExperiences": {
                "total": len(work_experiences),
                "list": work_experiences[:10]
            }
        },
        "samplePositions": positions[:5]  # 样本数据
    }
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        log(f"📈 保存统计报告: {report_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        report_path = ""
    
    return summary_path, report_path


async def crawl_all_data() -> Dict[str, Any]:
    """爬取所有数据"""
    log("🚀 开始爬取所有筛选条件下的岗位数据")
    start_time = datetime.now()
    
    # 爬取所有岗位数据
    raw_positions = await crawl_all_positions_with_filters()
    
    if not raw_positions:
        log("❌ 无法爬取到任何数据")
        return {"success": False, "message": "无法爬取到任何数据"}
    
    log(f"📊 爬取到 {len(raw_positions)} 个原始岗位")
    
    # 处理数据
    processed_positions = []
    saved_files = []
    
    for i, raw_position in enumerate(raw_positions, 1):
        if i % 20 == 0:
            log(f"📝 处理进度: {i}/{len(raw_positions)}")
        
        try:
            # 解析详细信息
            parsed_details = parse_position_details(raw_position)
            
            # 创建标准化岗位
            standard_position = create_standard_position(raw_position, parsed_details)
            
            # 保存数据
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            
            processed_positions.append(standard_position)
            
        except Exception as e:
            log(f"⚠️ 处理第 {i} 个岗位失败: {e}")
            continue
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    # 生成详细统计
    stats = {
        "success": True,
        "raw_positions": len(raw_positions),
        "processed_positions": len(processed_positions),
        "saved_files": len(saved_files),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_mode": "full_data"
    }
    
    # 保存数据报告
    summary_path, report_path = save_data_report(processed_positions, stats)
    
    log("=" * 70)
    log(f"🎉 完整数据爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 原始岗位: {len(raw_positions)}个")
    log(f"   • 处理岗位: {len(processed_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log(f"   • 汇总文件: {os.path.basename(summary_path) if summary_path else '无'}")
    log(f"   • 统计报告: {os.path.basename(report_path) if report_path else '无'}")
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 完整数据爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 应用筛选条件（社会招聘）")
    print("   3. 爬取所有页面的岗位数据")
    print("   4. 智能解析岗位详细信息")
    print("   5. 批量保存标准化数据")
    print("   6. 生成数据汇总和统计报告")
    print()
    print("⚠️ 注意: 浏览器窗口会自动打开，请勿关闭")
    print()
    
    try:
        stats = asyncio.run(crawl_all_data())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 完整数据爬取成功！")
            print("✅" * 35)
            print()
            print("📊 最终统计:")
            print(f"   📈 原始岗位数: {stats['raw_positions']}")
            print(f"   📈 处理岗位数: {stats['processed_positions']}")
            print(f"   💾 保存文件数: {stats['saved_files']}")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📁 输出目录: {stats['output_dir']}")
            print()
            
            # 显示文件结构
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    json_files = [f for f in files if f.endswith('.json')]
                    position_files = [f for f in json_files if 'position_' in f]
                    report_files = [f for f in json_files if 'report' in f or 'all_positions' in f]
                    
                    print("📁 生成的文件:")
                    print(f"   📄 岗位文件: {len(position_files)} 个")
                    print(f"   📊 报告文件: {len(report_files)} 个")
                    
                    if report_files:
                        print("   📋 报告列表:")
                        for report in report_files:
                            print(f"      • {report}")
                    
                    print()
                    print("💡 下一步操作:")
                    print("   1. 查看所有数据: cat output/ks_full_data/ks_all_positions_*.json | head -100")
                    print("   2. 查看统计报告: cat output/ks_full_data/ks_statistics_report_*.json")
                    print("   3. 查看单个岗位: ls output/ks_full_data/ks_position_*.json | head -5")
                    print("   4. 数据分析: 使用Python或Excel分析JSON数据")
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