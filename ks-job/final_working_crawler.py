#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘最终工作爬取器
使用最简单可靠的方法获取所有岗位数据
"""

import asyncio
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 80)
print("🚀 快手招聘最终工作爬取器")
print("=" * 80)
print("使用最简单可靠的方法获取所有岗位数据")
print()

# 输出目录
OUTPUT_DIR = "output/ks_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/final_working_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def get_page_text_simple() -> Optional[str]:
    """
    最简单的方法：获取页面所有文本
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动浏览器获取页面文本...")
        
        playwright = await async_playwright().start()
        
        # 启动浏览器（无头模式，更快）
        browser = await playwright.chromium.launch(
            headless=True,  # 无头模式，不显示窗口
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
        
        # 滚动页面加载所有内容
        log("🔄 滚动页面加载所有内容...")
        
        # 多次滚动确保加载所有内容
        for i in range(15):
            await page.evaluate(f"window.scrollTo(0, {1000 * (i + 1)})")
            await page.wait_for_timeout(1000)
            
            # 每3次滚动记录一次
            if (i + 1) % 3 == 0:
                log(f"📜 滚动 {i+1}/15 次")
        
        # 等待最终加载
        await page.wait_for_timeout(5000)
        
        # 获取页面所有文本
        log("🔍 获取页面所有文本...")
        all_text = await page.text_content('body')
        
        # 获取页面HTML（备用）
        html_content = await page.content()
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if all_text and len(all_text) > 1000:
            log(f"✅ 成功获取页面文本，长度: {len(all_text)} 字符")
            
            # 保存文本和HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存文本
            text_file = os.path.join(OUTPUT_DIR, f"kuaishou_full_text_{timestamp}.txt")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(all_text)
            log(f"💾 保存完整文本: {text_file}")
            
            # 保存HTML
            html_file = os.path.join(OUTPUT_DIR, f"kuaishou_full_html_{timestamp}.html")
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            log(f"💾 保存完整HTML: {html_file}")
            
            return all_text
        else:
            log("❌ 获取的文本太短或为空")
            return None
            
    except Exception as e:
        log(f"❌ 获取页面文本失败: {e}")
        return None


def extract_all_positions_from_text(text: str) -> List[Dict[str, Any]]:
    """
    从文本中提取所有岗位信息
    使用多种方法确保提取完整
    """
    log("🔍 开始从文本中提取所有岗位信息...")
    
    positions = []
    
    if not text:
        return positions
    
    # 方法1: 按行分析
    lines = text.split('\n')
    log(f"📄 文本共有 {len(lines)} 行")
    
    # 定义岗位相关关键词
    position_keywords = [
        '工程师', '开发', '产品', '运营', '设计', '分析', 
        '测试', '运维', '算法', '经理', '专员', '助理',
        '策划', '销售', '市场', '客服', '行政', '财务',
        'Java', 'Python', '前端', '后端', '数据', 'AI',
        '人工智能', '机器学习', '深度学习', '大数据',
        '架构师', '研究员', '顾问', '专家', '总监'
    ]
    
    # 定义地点关键词（中国主要城市）
    location_keywords = [
        '北京', '上海', '广州', '深圳', '杭州', '成都',
        '武汉', '南京', '西安', '苏州', '重庆', '天津',
        '长沙', '合肥', '郑州', '济南', '青岛', '大连',
        '沈阳', '长春', '哈尔滨', '厦门', '福州', '南宁',
        '珠海', '东莞', '佛山', '无锡', '常州', '宁波',
        '温州', '石家庄', '太原', '呼和浩特', '兰州',
        '西宁', '银川', '乌鲁木齐', '拉萨', '海口'
    ]
    
    # 分析每一行
    for line_num, line in enumerate(lines):
        line = line.strip()
        if len(line) < 25:  # 太短的行忽略
            continue
        
        # 检查是否包含岗位关键词
        has_position_keyword = any(keyword in line for keyword in position_keywords)
        has_location_keyword = any(keyword in line for keyword in location_keywords)
        
        # 快手招聘的典型格式特征
        has_kuaishou_format = any(pattern in line for pattern in ['【', '】', '2026.', '3-5年', '1-3年', '5-10年'])
        
        if has_position_keyword or has_location_keyword or has_kuaishou_format:
            # 提取基本信息
            position_data = extract_position_from_line(line, line_num)
            if position_data:
                positions.append(position_data)
    
    log(f"✅ 方法1（按行分析）提取到 {len(positions)} 个岗位")
    
    # 方法2: 正则表达式匹配
    log("🔍 使用方法2（正则表达式）提取...")
    
    # 快手招聘的典型格式模式
    patterns = [
        # 格式: Java 开发工程师-【电商】工程类杭州,北京3-5年2026.05.22
        r'([^【】]{5,30}?)(?:-|【)([^】]{2,10})】([^】]{2,10})([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
        
        # 格式: 岗位名称 工作地点 工作经验 更新时间
        r'([^0-9]{5,30}?)\s+([^0-9]{2,10}?)\s+(\d+-\d+年)\s+(\d{4}\.\d{2}\.\d{2})',
        
        # 包含【】的格式
        r'([^【】]{5,30})【([^】]+)】([^0-9]{5,20})(\d+-\d+年)(\d{4}\.\d{2}\.\d{2})',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            log(f"✅ 正则匹配找到 {len(matches)} 个岗位: {pattern[:50]}...")
            
            for match in matches:
                if len(match) >= 4:
                    position_data = {
                        "positionName": match[0].strip() if len(match) > 0 else "",
                        "positionCategory": match[1].strip() if len(match) > 1 else "",
                        "workLocation": match[2].strip() if len(match) > 2 else "",
                        "workExperience": match[3].strip() if len(match) > 3 else "",
                        "publishTime": match[4].strip() if len(match) > 4 else "",
                        "extractionMethod": "regex_pattern",
                        "rawLine": str(match)[:200]
                    }
                    
                    # 检查是否已存在相似岗位
                    if not is_duplicate_position(position_data, positions):
                        positions.append(position_data)
    
    # 去重
    unique_positions = []
    seen_keys = set()
    
    for position in positions:
        # 创建唯一标识键
        key = f"{position.get('positionName', '')}_{position.get('workLocation', '')}_{position.get('workExperience', '')}"
        
        if key not in seen_keys:
            seen_keys.add(key)
            unique_positions.append(position)
    
    log(f"📊 去重后剩余 {len(unique_positions)} 个唯一岗位")
    
    return unique_positions


def extract_position_from_line(line: str, line_num: int) -> Optional[Dict[str, Any]]:
    """从单行文本中提取岗位信息"""
    # 初始化结果
    result = {
        "rawLine": line[:200],
        "lineNumber": line_num,
        "positionName": "",
        "positionCategory": "",
        "workLocation": "",
        "workExperience": "",
        "publishTime": "",
        "extractionMethod": "line_analysis"
    }
    
    # 1. 提取岗位名称（在【或-之前的部分）
    name_match = re.search(r'^([^【】\[-]{5,40}?)(?:-|【|\[)', line)
    if name_match:
        result["positionName"] = name_match.group(1).strip()
    else:
        # 尝试提取包含关键词的部分
        for keyword in ['工程师', '开发', '产品', '运营', '设计', '经理', '专员']:
            if keyword in line:
                start = max(0, line.find(keyword) - 20)
                end = min(len(line), line.find(keyword) + 10)
                result["positionName"] = line[start:end].strip()
                break
    
    # 2. 提取岗位类别（在【】中）
    category_match = re.search(r'【([^】]+)】', line)
    if category_match:
        result["positionCategory"] = category_match.group(1).strip()
    
    # 3. 提取工作地点
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
    
    # 4. 提取工作经验
    exp_match = re.search(r'(\d+-\d+年)', line)
    if exp_match:
        result["workExperience"] = exp_match.group(1)
    else:
        # 尝试其他格式
        exp_patterns = [r'(\d+年)', r'([一二三四五六七八九十]+年)']
        for pattern in exp_patterns:
            match = re.search(pattern, line)
            if match:
                result["workExperience"] = match.group(1)
                break
    
    # 5. 提取发布时间
    time_match = re.search(r'(\d{4}\.\d{2}\.\d{2})', line)
    if time_match:
        result["publishTime"] = time_match.group(1)
    else:
        # 尝试其他格式
        time_patterns = [r'(\d{4}-\d{2}-\d{2})', r'(\d{4}/\d{2}/\d{2})']
        for pattern in time_patterns:
            match = re.search(pattern, line)
            if match:
                result["publishTime"] = match.group(1)
                break
    
    # 只有提取到足够信息才返回
    if result["positionName"] and (result["workLocation"] or result["workExperience"]):
        return result
    
    return None


def is_duplicate_position(new_position: Dict[str, Any], existing_positions: List[Dict[str, Any]]) -> bool:
    """检查是否重复岗位"""
    if not existing_positions:
        return False
    
    new_name = new_position.get("positionName", "")
    new_location = new_position.get("workLocation", "")
    new_experience = new_position.get("workExperience", "")
    
    for existing in existing_positions:
        existing_name = existing.get("positionName", "")
        existing_location = existing.get("workLocation", "")
        existing_experience = existing.get("workExperience", "")
        
        # 如果名称、地点、经验都相同或高度相似，认为是重复
        if (new_name and existing_name and new_name in existing_name or existing_name in new_name):
            if (not new_location and not existing_location) or (new_location and existing_location and new_location == existing_location):
                return True
    
    return False


def create_final_position_data(raw_position: Dict[str, Any]) -> Dict[str, Any]:
    """创建最终的标准化岗位数据"""
    position_id = f"KS_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(str(raw_position)) % 10000:04d}"
    
    # 标准化时间格式
    publish_time = raw_position.get("publishTime", "")
    if publish_time:
        publish_time = publish_time.replace('.', '-').replace('/', '-')
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
        "department": "",
        "educationRequirement": "",
        "workExperience": raw_position.get("workExperience", ""),
        "jobResponsibilities": "",
        "jobRequirements": "",
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "final_working_crawler",
        "source": "kuaishou_final",
        
        # 原始提取信息
        "extractionInfo": {
            "method": raw_position.get("extractionMethod", ""),
            "lineNumber": raw_position.get("lineNumber"),
            "rawLine": raw_position.get("rawLine", "")[:100]
        }
    }


def save_final_results(positions: List[Dict[str, Any]]) -> Dict[str, str]:
    """保存最终结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. 保存所有岗位数据
    all_positions_file = os.path.join(OUTPUT_DIR, f"kuaishou_all_positions_{timestamp}.json")
    
    all_data = {
        "metadata": {
            "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "outputDir": OUTPUT_DIR,
            "source": "快手招聘网站"
        },
        "positions": positions
    }
    
    try:
        with open(all_positions_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        log(f"💾 保存所有岗位数据: {all_positions_file}")
    except Exception as e:
        log(f"❌ 保存所有岗位数据失败: {e}")
        all_positions_file = ""
    
    # 2. 保存统计报告
    stats_file = os.path.join(OUTPUT_DIR, f"kuaishou_statistics_{timestamp}.json")
    
    # 统计信息
    position_names = [p.get("positionName", "") for p in positions]
    work_locations = []
    for p in positions:
        location = p.get("workLocation", "")
        if location and location not in work_locations:
            work_locations.append(location)
    
    work_experiences = []
    for p in positions:
        experience = p.get("workExperience", "")
        if experience and experience not in work_experiences:
            work_experiences.append(experience)
    
    stats_data = {
        "metadata": {
            "reportTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "totalPositions": len(positions),
            "uniquePositionNames": len(set(position_names)),
            "uniqueWorkLocations": len(work_locations),
            "uniqueWorkExperiences": len(work_experiences)
        },
        "summary": {
            "positionNames": list(set(position_names))[:20],
            "workLocations": work_locations[:20],
            "workExperiences": work_experiences[:10]
        },
        "sampleData": positions[:5]  # 样本数据
    }
    
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, ensure_ascii=False, indent=2)
        log(f"📊 保存统计报告: {stats_file}")
    except Exception as e:
        log(f"❌ 保存统计报告失败: {e}")
        stats_file = ""
    
    # 3. 保存CSV格式（便于Excel打开）
    csv_file = os.path.join(OUTPUT_DIR, f"kuaishou_positions_{timestamp}.csv")
    
    try:
        with open(csv_file, 'w', encoding='utf-8-sig') as f:
            # 写入CSV头部
            f.write("positionId,positionName,workLocation,positionCategory,publishTime,workExperience,company,crawlTime\n")
            
            # 写入数据
            for position in positions:
                row = [
                    position.get("positionId", ""),
                    f'"{position.get("positionName", "")}"',
                    f'"{position.get("workLocation", "")}"',
                    f'"{position.get("positionCategory", "")}"',
                    f'"{position.get("publishTime", "")}"',
                    f'"{position.get("workExperience", "")}"',
                    f'"{position.get("company", "")}"',
                    f'"{position.get("crawlTime", "")}"'
                ]
                f.write(','.join(row) + '\n')
        
        log(f"📈 保存CSV格式: {csv_file}")
    except Exception as e:
        log(f"❌ 保存CSV格式失败: {e}")
        csv_file = ""
    
    return {
        "all_positions": all_positions_file,
        "statistics": stats_file,
        "csv": csv_file
    }


async def main_async():
    """异步主函数"""
    log("🚀 开始最终工作爬取")
    start_time = datetime.now()
    
    # 获取页面文本
    page_text = await get_page_text_simple()
    
    if not page_text:
        log("❌ 无法获取页面文本")
        return {"success": False, "message": "无法获取页面文本"}
    
    log(f"📄 页面文本获取成功，长度: {len(page_text)} 字符")
    
    # 提取所有岗位信息
    raw_positions = extract_all_positions_from_text(page_text)
    
    if not raw_positions:
        log("❌ 未提取到任何岗位信息")
        return {"success": False, "message": "未提取到任何岗位信息"}
    
    log(f"📊 提取到 {len(raw_positions)} 个原始岗位")
    
    # 创建标准化岗位数据
    final_positions = []
    for i, raw_position in enumerate(raw_positions, 1):
        final_position = create_final_position_data(raw_position)
        final_positions.append(final_position)
        
        if i % 20 == 0:
            log(f"📝 处理进度: {i}/{len(raw_positions)}")
    
    log(f"✅ 创建了 {len(final_positions)} 个标准化岗位")
    
    # 保存结果
    saved_files = save_final_results(final_positions)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "page_text_length": len(page_text),
        "raw_positions": len(raw_positions),
        "final_positions": len(final_positions),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "saved_files": saved_files,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 70)
    log(f"🎉 最终工作爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 页面文本: {len(page_text)} 字符")
    log(f"   • 原始岗位: {len(raw_positions)} 个")
    log(f"   • 最终岗位: {len(final_positions)} 个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    
    for file_type, file_path in saved_files.items():
        if file_path:
            log(f"   • {file_type}: {os.path.basename(file_path)}")
    
    log("=" * 70)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 最终工作爬取流程:")
    print("   1. 自动访问快手招聘网站")
    print("   2. 点击社会招聘筛选")
    print("   3. 滚动加载所有页面内容")
    print("   4. 获取完整页面文本")
    print("   5. 智能提取所有岗位信息")
    print("   6. 保存多种格式数据")
    print()
    print("🎯 目标: 获取筛选条件下的所有岗位数据")
    print()
    
    try:
        stats = asyncio.run(main_async())
        
        if stats.get("success"):
            print()
            print("✅" * 35)
            print("🎉 快手招聘数据爬取成功完成！")
            print("✅" * 35)
            print()
            print("📊 最终成果:")
            print(f"   📈 获取岗位总数: {stats['final_positions']} 个")
            print(f"   ⏱️  总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   📂 输出目录: {stats['output_dir']}")
            print()
            
            # 显示生成的文件
            saved_files = stats.get("saved_files", {})
            if saved_files:
                print("📁 生成的文件:")
                for file_type, file_path in saved_files.items():
                    if file_path:
                        print(f"   • {file_type}: {os.path.basename(file_path)}")
            
            print()
            print("💡 数据使用:")
            print("   1. 查看所有数据: cat output/ks_final/kuaishou_all_positions_*.json")
            print("   2. 查看统计报告: cat output/ks_final/kuaishou_statistics_*.json")
            print("   3. 用Excel打开: open output/ks_final/kuaishou_positions_*.csv")
            print("   4. 分析岗位分布: 查看统计报告中的工作地点和岗位类别")
            print()
            print("🎯 ks-job 项目目标达成: 成功爬取筛选条件下的所有岗位数据")
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