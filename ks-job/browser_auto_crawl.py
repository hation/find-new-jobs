#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘浏览器自动化爬取器
使用Playwright自动获取实时签名并爬取数据
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests

print("=" * 70)
print("🚀 快手招聘浏览器自动化爬取器")
print("=" * 70)
print("使用Playwright自动获取实时签名，解决签名过期问题")
print()

# 输出目录
OUTPUT_DIR = "output/ks_browser_auto"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/browser_auto_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def get_signature_via_playwright() -> Optional[Tuple[str, str, Dict[str, Any]]]:
    """
    使用Playwright获取实时签名和数据
    
    Returns:
        (sign, signtimestamp, api_data) 或 None
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器...")
        
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
        
        # 访问快手招聘网站
        log("🌐 访问快手招聘网站...")
        await page.goto("https://zhaopin.kuaishou.cn", wait_until="networkidle")
        
        # 等待页面加载
        await page.wait_for_timeout(3000)
        log("✅ 页面加载完成")
        
        # 监听API请求
        captured_data = {
            "sign": "",
            "signtimestamp": "",
            "api_data": None,
            "headers": {}
        }
        
        def handle_response(response):
            """处理API响应"""
            try:
                url = response.url
                if "positions/simple" in url:
                    # 获取请求头
                    request = response.request
                    headers = request.headers
                    
                    sign = headers.get("sign", "")
                    signtimestamp = headers.get("signtimestamp", "")
                    
                    if sign and signtimestamp:
                        captured_data["sign"] = sign
                        captured_data["signtimestamp"] = signtimestamp
                        captured_data["headers"] = dict(headers)
                        
                        # 尝试获取响应数据
                        try:
                            api_data = response.json()
                            captured_data["api_data"] = api_data
                            log(f"📡 捕获API响应: {url}")
                            log(f"   签名: {sign[:20]}...")
                            log(f"   时间戳: {signtimestamp}")
                        except:
                            pass
            except Exception as e:
                log(f"⚠️ 处理响应失败: {e}")
        
        # 监听响应
        page.on("response", handle_response)
        
        # 方法1: 滚动触发API请求
        log("🔄 滚动页面触发API请求...")
        await page.evaluate("window.scrollTo(0, 1000)")
        await page.wait_for_timeout(2000)
        
        # 方法2: 点击可能的加载按钮
        try:
            load_more_selectors = [
                "button:has-text('加载更多')",
                "button:has-text('查看更多')",
                ".load-more",
                ".more-btn"
            ]
            
            for selector in load_more_selectors:
                try:
                    await page.click(selector, timeout=2000)
                    log(f"✅ 点击: {selector}")
                    await page.wait_for_timeout(2000)
                    break
                except:
                    continue
        except:
            log("⚠️ 未找到加载更多按钮")
        
        # 方法3: 直接模拟API请求
        log("📡 直接模拟API请求...")
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
        
        # 使用浏览器发送请求
        response = await page.goto(full_url, wait_until="networkidle")
        
        if response:
            try:
                api_data = await response.json()
                captured_data["api_data"] = api_data
                log("✅ 成功获取API数据")
            except Exception as e:
                log(f"⚠️ 解析API数据失败: {e}")
        
        # 等待更多请求
        await page.wait_for_timeout(5000)
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
        if captured_data["sign"] and captured_data["signtimestamp"]:
            log(f"🎉 成功获取实时签名!")
            log(f"   sign: {captured_data['sign'][:20]}...")
            log(f"   signtimestamp: {captured_data['signtimestamp']}")
            
            return (
                captured_data["sign"],
                captured_data["signtimestamp"],
                captured_data["api_data"]
            )
        else:
            log("❌ 未获取到签名参数")
            return None
            
    except ImportError:
        log("❌ 未安装Playwright，请运行: pip install playwright")
        return None
    except Exception as e:
        log(f"❌ 浏览器自动化失败: {e}")
        return None


def fetch_data_with_signature(sign: str, signtimestamp: str, page_num: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
    """使用签名获取数据"""
    log(f"📄 使用签名获取第 {page_num} 页数据...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E",
        "Host": "zhaopin.kuaishou.cn",
        "Pragma": "no-cache",
        "Referer": "https://zhaopin.kuaishou.cn/",
        "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "sign": sign,
        "signtimestamp": signtimestamp
    }
    
    params = {
        "pageNum": page_num,
        "pageSize": page_size,
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple",
            params=params,
            headers=headers,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0:
                result = data.get("result", {})
                positions = result.get('list', [])
                log(f"✅ 第 {page_num} 页获取成功: {len(positions)} 个岗位, 耗时: {elapsed_time:.2f}秒")
                return data
            else:
                log(f"❌ 第 {page_num} 页API错误: code={data.get('code')}, message={data.get('message')}")
                return None
        else:
            log(f"❌ 第 {page_num} 页HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        log(f"❌ 第 {page_num} 页请求失败: {e}")
        return None


def extract_standard_fields(position: Dict[str, Any], sign: str, signtimestamp: str) -> Dict[str, Any]:
    """提取标准字段"""
    return {
        # 12个核心字段
        "positionId": str(position.get("id", "")),
        "positionName": position.get("name", ""),
        "workLocation": position.get("workLocationCode", ""),
        "positionCategory": position.get("positionCategoryCode", ""),
        "publishTime": position.get("updateTime", ""),
        "detailUrl": f"https://zhaopin.kuaishou.cn/position/{position.get('id', '')}",
        "department": position.get("departmentCode", ""),
        "educationRequirement": position.get("educationLimitCode", ""),
        "workExperience": position.get("workExperienceCode", ""),
        "jobResponsibilities": position.get("description", ""),
        "jobRequirements": position.get("positionDemand", ""),
        "salaryRange": "",
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "browser_auto",
        "source": "kuaishou_browser_auto",
        
        # 签名信息
        "signature": sign[:20] + "..." if sign else "",
        "signatureTimestamp": signtimestamp,
        
        # 原始数据
        "rawData": {
            "levels": position.get("levels", []),
            "workLocationsCode": position.get("workLocationsCode", []),
            "recruitProjectCode": position.get("recruitProjectCode", ""),
            "positionNatureCode": position.get("positionNatureCode", ""),
            "channelCode": position.get("channelCode", "")
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


async def crawl_with_browser_automation() -> Dict[str, Any]:
    """使用浏览器自动化爬取数据"""
    log("🚀 开始浏览器自动化爬取")
    start_time = datetime.now()
    
    # 第一步：通过浏览器获取实时签名
    log("🔄 第一步：通过浏览器获取实时签名...")
    result = await get_signature_via_playwright()
    
    if not result:
        log("❌ 无法获取实时签名")
        return {"success": False, "message": "无法获取实时签名"}
    
    sign, signtimestamp, first_page_data = result
    
    if not sign or not signtimestamp:
        log("❌ 未获取到有效签名")
        return {"success": False, "message": "未获取到有效签名"}
    
    log(f"✅ 获取到实时签名: {signtimestamp}")
    
    # 第二步：使用签名爬取数据
    all_positions = []
    saved_files = []
    
    # 如果浏览器已经获取了第一页数据
    if first_page_data and first_page_data.get("code") == 0:
        result_data = first_page_data.get("result", {})
        positions = result_data.get("list", [])
        total_positions = result_data.get('total', 0)
        total_pages = result_data.get('pages', 0)
        
        log(f"📊 发现 {total_positions} 个岗位，共 {total_pages} 页")
        
        # 处理第一页数据
        for raw_position in positions:
            standard_position = extract_standard_fields(raw_position, sign, signtimestamp)
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            all_positions.append(standard_position)
        
        log(f"✅ 第一页处理完成: {len(positions)} 个岗位")
        
        # 询问是否爬取更多页
        print()
        choice = input(f"是否爬取更多页？共 {total_pages} 页 (y/N): ").strip().lower()
        
        if choice == 'y':
            try:
                max_pages = int(input(f"请输入最大爬取页数（默认{min(5, total_pages)}）: ") or str(min(5, total_pages)))
            except ValueError:
                max_pages = min(5, total_pages)
            
            # 爬取剩余页
            for page_num in range(2, max_pages + 1):
                # 避免请求过快
                time.sleep(2)
                
                # 显示进度
                progress = (page_num - 1) / max_pages * 100
                log(f"📊 进度: {page_num-1}/{max_pages}页 ({progress:.1f}%)")
                
                page_data = fetch_data_with_signature(sign, signtimestamp, page_num, page_size=10)
                
                if not page_data:
                    log(f"⚠️ 第 {page_num} 页获取失败，跳过")
                    continue
                
                page_positions = page_data.get("result", {}).get("list", [])
                
                for raw_position in page_positions:
                    standard_position = extract_standard_fields(raw_position, sign, signtimestamp)
                    filepath = save_position(standard_position)
                    if filepath:
                        saved_files.append(filepath)
                    all_positions.append(standard_position)
                
                log(f"✅ 第 {page_num} 页处理完成: {len(page_positions)} 个岗位")
    else:
        # 如果浏览器没有获取到数据，尝试使用签名获取第一页
        log("🔄 浏览器未获取到数据，尝试使用签名获取...")
        first_page_data = fetch_data_with_signature(sign, signtimestamp, 1, page_size=10)
        
        if not first_page_data:
            log("❌ 无法获取任何数据")
            return {"success": False, "message": "无法获取数据"}
        
        result_data = first_page_data.get("result", {})
        positions = result_data.get("list", [])
        
        if not positions:
            log("❌ 第一页无数据")
            return {"success": False, "message": "第一页无数据"}
        
        # 处理第一页数据
        for raw_position in positions:
            standard_position = extract_standard_fields(raw_position, sign, signtimestamp)
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            all_positions.append(standard_position)
        
        log(f"✅ 第一页处理完成: {len(positions)} 个岗位")
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "crawled_positions": len(all_positions),
        "saved_files": len(saved_files),
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "signature_timestamp": signtimestamp,
        "crawl_mode": "browser_automation"
    }
    
    log("=" * 60)
    log(f"🎉 浏览器自动化爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 获取岗位: {len(all_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log(f"   • 签名时间戳: {signtimestamp}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 浏览器自动化爬取流程:")
    print("   1. 自动打开浏览器访问快手招聘网站")
    print("   2. 自动获取实时签名参数")
    print("   3. 使用签名爬取岗位数据")
    print("   4. 自动保存所有数据")
    print()
    
    try:
        stats = asyncio.run(crawl_with_browser_automation())
        
        if stats.get("success"):
            print()
            print("🎉 浏览器自动化爬取成功！")
            print()
            print("📊 爬取统计:")
            print(f"   爬取岗位: {stats['crawled_positions']}")
            print(f"   保存文件: {stats['saved_files']}")
            print(f"   总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   输出目录: {stats['output_dir']}")
            print(f"   签名时间戳: {stats['signature_timestamp']}")
            print()
            
            # 显示保存的文件
            if os.path.exists(OUTPUT_DIR):
                files = os.listdir(OUTPUT_DIR)
                if files:
                    print("📁 保存的文件:")
                    for i, filename in enumerate(files[:5], 1):
                        print(f"  {i}. {filename}")
                    if len(files) > 5:
                        print(f"  ... 还有 {len(files) - 5} 个文件")
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
    print("  1. 查看数据: ls output/ks_browser_auto/")
    print("  2. 查看日志: cat logs/browser_auto_crawl.log")
    print("  3. 继续爬取: 重新运行此脚本")
    print("  4. 浏览器窗口会自动关闭")
    print()


if __name__ == "__main__":
    main()