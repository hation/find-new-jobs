#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘直接Playwright爬取器
直接使用浏览器获取数据，无需处理签名
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

print("=" * 70)
print("🚀 快手招聘直接Playwright爬取器")
print("=" * 70)
print("直接使用浏览器获取数据，绕过签名验证")
print()

# 输出目录
OUTPUT_DIR = "output/ks_direct_playwright"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/direct_playwright_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


async def get_data_directly_via_playwright() -> Optional[Dict[str, Any]]:
    """
    直接使用Playwright获取数据
    
    Returns:
        API数据 或 None
    """
    try:
        from playwright.async_api import async_playwright
        
        log("🔄 启动Playwright浏览器直接获取数据...")
        
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
        
        # 直接访问API URL（带参数）
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
        
        log(f"🌐 直接访问API: {full_url}")
        
        # 设置请求头（模拟浏览器）
        await page.set_extra_http_headers({
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
            "Sec-Fetch-Site": "same-origin"
        })
        
        # 访问API
        response = await page.goto(full_url, wait_until="networkidle")
        
        if response:
            log(f"✅ API响应状态: {response.status}")
            
            # 获取响应内容
            try:
                content = await response.text()
                data = json.loads(content)
                
                if data.get("code") == 0:
                    log("🎉 成功获取API数据！")
                    return data
                else:
                    log(f"❌ API错误: code={data.get('code')}, message={data.get('message')}")
                    return None
            except json.JSONDecodeError as e:
                log(f"❌ JSON解析失败: {e}")
                log(f"   响应内容: {content[:500]}")
                return None
            except Exception as e:
                log(f"❌ 获取响应失败: {e}")
                return None
        else:
            log("❌ 无响应")
            return None
        
        # 关闭浏览器
        await browser.close()
        await playwright.stop()
        
    except ImportError:
        log("❌ 未安装Playwright，请运行: pip install playwright")
        return None
    except Exception as e:
        log(f"❌ 浏览器自动化失败: {e}")
        return None


def extract_standard_fields(position: Dict[str, Any]) -> Dict[str, Any]:
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
        "crawlMode": "direct_playwright",
        "source": "kuaishou_direct_playwright",
        
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


async def crawl_directly_with_playwright() -> Dict[str, Any]:
    """直接使用Playwright爬取数据"""
    log("🚀 开始直接Playwright爬取")
    start_time = datetime.now()
    
    # 获取数据
    api_data = await get_data_directly_via_playwright()
    
    if not api_data:
        log("❌ 无法获取数据")
        return {"success": False, "message": "无法获取数据"}
    
    result = api_data.get("result", {})
    positions = result.get("list", [])
    total_positions = result.get('total', 0)
    total_pages = result.get('pages', 0)
    
    log(f"📊 发现 {total_positions} 个岗位，共 {total_pages} 页")
    
    if not positions:
        log("❌ 未获取到岗位数据")
        return {"success": False, "message": "未获取到岗位数据"}
    
    # 保存数据
    saved_files = []
    
    for i, raw_position in enumerate(positions, 1):
        log(f"📝 处理第 {i} 个岗位: {raw_position.get('name', '未知')[:30]}...")
        standard_position = extract_standard_fields(raw_position)
        filepath = save_position(standard_position)
        if filepath:
            saved_files.append(filepath)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "total_positions": total_positions,
        "crawled_positions": len(positions),
        "saved_files": len(saved_files),
        "total_pages": total_pages,
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_mode": "direct_playwright"
    }
    
    log("=" * 60)
    log(f"🎉 直接Playwright爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 获取岗位: {len(positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log(f"   • 总岗位数: {total_positions}")
    log(f"   • 总页数: {total_pages}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print()
    print("📋 直接Playwright爬取流程:")
    print("   1. 自动打开浏览器")
    print("   2. 直接访问快手API")
    print("   3. 获取岗位数据")
    print("   4. 自动保存所有数据")
    print()
    
    try:
        stats = asyncio.run(crawl_directly_with_playwright())
        
        if stats.get("success"):
            print()
            print("🎉 直接Playwright爬取成功！")
            print()
            print("📊 爬取统计:")
            print(f"   总岗位数: {stats['total_positions']}")
            print(f"   爬取岗位: {stats['crawled_positions']}")
            print(f"   保存文件: {stats['saved_files']}")
            print(f"   总页数: {stats['total_pages']}")
            print(f"   总用时: {stats['elapsed_time']:.2f}秒")
            print(f"   输出目录: {stats['output_dir']}")
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
            
            # 显示第一个岗位的详细信息
            if stats['crawled_positions'] > 0:
                print()
                print("📄 第一个岗位详情:")
                # 这里可以添加显示第一个岗位的代码
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
    print("  1. 查看数据: ls output/ks_direct_playwright/")
    print("  2. 查看日志: cat logs/direct_playwright_crawl.log")
    print("  3. 继续爬取: 重新运行此脚本")
    print("  4. 浏览器窗口会自动关闭")
    print()


if __name__ == "__main__":
    main()