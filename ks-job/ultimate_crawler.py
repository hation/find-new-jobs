#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘终极爬取器
使用Playwright浏览器自动化，自动获取实时签名
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 70)
print("🚀 快手招聘终极爬取器")
print("=" * 70)
print("使用Playwright浏览器自动化，自动获取实时签名")
print("解决签名过期问题")
print()

# 检查Playwright是否安装
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("❌ 未安装Playwright")
    print("💡 请运行以下命令安装:")
    print("   1. pip install playwright")
    print("   2. python -m playwright install")
    print()

# 输出目录
OUTPUT_DIR = "output/ks_ultimate"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/ultimate_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def get_signature_via_browser() -> Optional[Dict[str, Any]]:
    """
    通过浏览器获取签名和数据
    返回包含签名和数据的字典
    """
    if not PLAYWRIGHT_AVAILABLE:
        log("❌ Playwright未安装，无法使用浏览器自动化")
        return None
    
    log("🔄 启动浏览器获取实时签名...")
    
    try:
        playwright = await async_playwright().start()
        
        # 启动浏览器（显示窗口，便于调试）
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
        
        # 访问快手招聘网站
        log("🌐 访问快手招聘网站...")
        await page.goto("https://zhaopin.kuaishou.cn", wait_until="networkidle")
        
        # 等待页面加载
        await page.wait_for_timeout(3000)
        
        # 监听API请求
        api_data = None
        api_headers = None
        
        def handle_response(response):
            nonlocal api_data, api_headers
            if "positions/simple" in response.url:
                try:
                    api_data = response.json()
                    api_headers = response.request.headers
                    log(f"📡 捕获API响应: {response.url}")
                except:
                    pass
        
        page.on("response", handle_response)
        
        # 尝试触发API请求（通过点击或滚动）
        log("🔄 触发API请求...")
        
        # 方法1: 滚动页面
        await page.evaluate("window.scrollTo(0, 500)")
        await page.wait_for_timeout(2000)
        
        # 方法2: 点击可能的加载按钮
        try:
            await page.click("button:has-text('加载更多')", timeout=5000)
            await page.wait_for_timeout(2000)
        except:
            pass
        
        # 方法3: 直接发送API请求
        api_url = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"
        params = {
            "pageNum": 1,
            "pageSize": 10,
            "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
            "positionNatureCode": "C001",
            "recruitProject": "socialr",
            "workLocationCode": "domestic"
        }
        
        # 构建查询字符串
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{api_url}?{query_string}"
        
        log(f"📡 直接请求API: {full_url}")
        
        # 使用浏览器发送请求
        response = await page.goto(full_url, wait_until="networkidle")
        
        if response:
            try:
                api_data = await response.json()
                api_headers = response.request.headers
                log("✅ 成功获取API数据")
            except:
                log("❌ 无法解析API响应")
        
        # 等待一段时间让请求完成
        await page.wait_for_timeout(5000)
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if api_data and api_headers:
            result = {
                "data": api_data,
                "headers": dict(api_headers),
                "timestamp": int(time.time() * 1000)
            }
            
            # 提取签名
            sign = api_headers.get("sign", "")
            signtimestamp = api_headers.get("signtimestamp", "")
            
            if sign and signtimestamp:
                log(f"✅ 获取到实时签名:")
                log(f"   sign: {sign[:20]}...")
                log(f"   signtimestamp: {signtimestamp}")
            else:
                log("⚠️ 未获取到签名参数")
            
            return result
        else:
            log("❌ 未获取到API数据")
            return None
            
    except Exception as e:
        log(f"❌ 浏览器自动化失败: {e}")
        return None


def extract_positions_from_data(api_result: Dict[str, Any]) -> List[Dict[str, Any]]:
    """从API结果中提取岗位数据"""
    if not api_result:
        return []
    
    data = api_result.get("data", {})
    
    if data.get("code") != 0:
        log(f"❌ API错误: code={data.get('code')}, message={data.get('message')}")
        return []
    
    result = data.get("result", {})
    positions = result.get("list", [])
    
    log(f"📊 提取到 {len(positions)} 个岗位")
    return positions


def save_position(position_data: Dict[str, Any], api_headers: Dict[str, Any]) -> str:
    """保存岗位数据"""
    position_id = str(position_data.get("id", "unknown"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 提取签名
    sign = api_headers.get("sign", "")
    signtimestamp = api_headers.get("signtimestamp", "")
    
    # 标准化数据
    standard_data = {
        # 12个核心字段
        "positionId": position_id,
        "positionName": position_data.get("name", ""),
        "workLocation": position_data.get("workLocationCode", ""),
        "positionCategory": position_data.get("positionCategoryCode", ""),
        "publishTime": position_data.get("updateTime", ""),
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position_id}",
        "department": position_data.get("departmentCode", ""),
        "educationRequirement": position_data.get("educationLimitCode", ""),
        "workExperience": position_data.get("workExperienceCode", ""),
        "jobResponsibilities": position_data.get("description", ""),
        "jobRequirements": position_data.get("positionDemand", ""),
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "browser_automation",
        "source": "kuaishou_browser",
        
        # 签名信息
        "signature": sign[:20] + "..." if sign else "",
        "signatureTimestamp": signtimestamp,
        
        # 原始数据
        "rawData": {
            "levels": position_data.get("levels", []),
            "workLocationsCode": position_data.get("workLocationsCode", []),
            "recruitProjectCode": position_data.get("recruitProjectCode", ""),
            "positionNatureCode": position_data.get("positionNatureCode", ""),
            "channelCode": position_data.get("channelCode", "")
        }
    }
    
    filename = f"ks_position_{position_id}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, ensure_ascii=False, indent=2)
        
        log(f"💾 保存: {filename}")
        return filepath
    except Exception as e:
        log(f"❌ 保存失败: {e}")
        return ""


async def main_async():
    """异步主函数"""
    log("🚀 启动终极爬取器")
    
    # 通过浏览器获取数据
    api_result = await get_signature_via_browser()
    
    if not api_result:
        log("❌ 无法通过浏览器获取数据")
        return
    
    # 提取岗位数据
    positions = extract_positions_from_data(api_result)
    
    if not positions:
        log("❌ 未提取到岗位数据")
        return
    
    # 保存数据
    saved_files = []
    api_headers = api_result.get("headers", {})
    
    for i, position in enumerate(positions, 1):
        log(f"📝 处理第 {i} 个岗位: {position.get('name', '未知')[:30]}...")
        filepath = save_position(position, api_headers)
        if filepath:
            saved_files.append(filepath)
    
    # 显示结果
    log("=" * 60)
    log(f"🎉 爬取完成!")
    log(f"   • 获取岗位: {len(positions)} 个")
    log(f"   • 保存文件: {len(saved_files)} 个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    
    # 显示第一个岗位的详细信息
    if positions:
        first_position = positions[0]
        log("📄 第一个岗位详情:")
        log(f"   ID: {first_position.get('id')}")
        log(f"   名称: {first_position.get('name')}")
        log(f"   地点: {first_position.get('workLocationCode')}")
        log(f"   类别: {first_position.get('positionCategoryCode')}")
    
    log("=" * 60)
    
    # 提供下一步建议
    print()
    print("💡 下一步:")
    print("  1. 查看数据: ls output/ks_ultimate/")
    print("  2. 查看日志: cat logs/ultimate_crawl.log")
    print("  3. 继续爬取: 重新运行此脚本")
    print("  4. 分析数据: 使用其他工具分析JSON文件")
    print()


def main():
    """主函数"""
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ 请先安装Playwright:")
        print("   pip install playwright")
        print("   python -m playwright install")
        return
    
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print()
        log("⏹️ 用户中断")
    except Exception as e:
        log(f"❌ 程序异常: {e}")


if __name__ == "__main__":
    main()