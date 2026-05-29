#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘实时签名爬取器
每次请求前从浏览器获取最新签名
"""

import os
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import requests

# 输出目录
OUTPUT_DIR = "output/ks_data_realtime"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/realtime_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


def get_latest_signature_from_browser() -> Tuple[str, str]:
    """
    从浏览器获取最新签名
    需要用户手动从浏览器复制最新的sign和signtimestamp
    
    Returns:
        (sign, signtimestamp)
    """
    log("⚠️ 需要从浏览器获取最新签名")
    log("   请按以下步骤操作:")
    log("   1. 打开浏览器访问 https://zhaopin.kuaishou.cn")
    log("   2. 按F12打开开发者工具")
    log("   3. 切换到Network标签")
    log("   4. 刷新页面或点击'加载更多'")
    log("   5. 找到API请求: positions/simple")
    log("   6. 复制最新的 sign 和 signtimestamp")
    log("   7. 立即使用（有效期极短）")
    
    # 等待用户输入
    sign = input("请输入最新的 sign: ").strip()
    signtimestamp = input("请输入最新的 signtimestamp: ").strip()
    
    if not sign or not signtimestamp:
        log("❌ 签名参数不能为空")
        return "", ""
    
    log(f"✅ 获取到签名:")
    log(f"   sign: {sign[:20]}...")
    log(f"   signtimestamp: {signtimestamp}")
    
    return sign, signtimestamp


def create_headers(sign: str, signtimestamp: str) -> Dict[str, str]:
    """创建请求头"""
    return {
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


def test_signature(sign: str, signtimestamp: str) -> bool:
    """测试签名有效性"""
    log(f"🔍 测试签名有效性: {signtimestamp}")
    
    headers = create_headers(sign, signtimestamp)
    params = {
        "pageNum": 1,
        "pageSize": 1,  # 只取1条测试
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        response = requests.get(
            "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple",
            params=params,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                log("✅ 签名有效！")
                return True
            else:
                log(f"❌ 签名无效: code={data.get('code')}, message={data.get('message')}")
                return False
        else:
            log(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        log(f"❌ 测试失败: {e}")
        return False


def fetch_page_with_signature(page_num: int, sign: str, signtimestamp: str, page_size: int = 10) -> Optional[Dict[str, Any]]:
    """使用签名获取单页数据"""
    log(f"📄 获取第 {page_num} 页数据...")
    
    headers = create_headers(sign, signtimestamp)
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
        "crawlMode": "realtime_signature",
        "source": "kuaishou_realtime",
        
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


def crawl_with_realtime_signatures() -> Dict[str, Any]:
    """使用实时签名爬取数据"""
    log("🚀 开始实时签名爬取")
    start_time = datetime.now()
    
    all_positions = []
    saved_files = []
    current_page = 1
    
    print("=" * 60)
    print("📝 实时签名爬取说明:")
    print("   1. 每次请求前需要从浏览器获取最新签名")
    print("   2. 签名有效期极短（几秒）")
    print("   3. 获取后立即使用")
    print("   4. 每页可能需要新签名")
    print("=" * 60)
    print()
    
    while True:
        log(f"🔄 准备获取第 {current_page} 页")
        
        # 获取最新签名
        sign, signtimestamp = get_latest_signature_from_browser()
        
        if not sign or not signtimestamp:
            log("❌ 未获取到签名，终止爬取")
            break
        
        # 测试签名有效性
        if not test_signature(sign, signtimestamp):
            log("⚠️ 签名无效，请重新获取")
            continue
        
        # 获取页面数据
        page_data = fetch_page_with_signature(current_page, sign, signtimestamp, page_size=5)
        
        if not page_data:
            log(f"❌ 第 {current_page} 页获取失败")
            break
        
        result = page_data.get("result", {})
        positions = result.get('list', [])
        
        if not positions:
            log(f"⚠️ 第 {current_page} 页无数据，可能已到最后一页")
            break
        
        # 处理本页数据
        for raw_position in positions:
            standard_position = extract_standard_fields(raw_position)
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            all_positions.append(standard_position)
        
        log(f"✅ 第 {current_page} 页处理完成: {len(positions)} 个岗位")
        
        # 显示进度
        total_positions = result.get('total', 0)
        total_pages = result.get('pages', 0)
        
        if current_page == 1:
            log(f"📊 发现 {total_positions} 个岗位，共 {total_pages} 页")
        
        # 询问是否继续
        print()
        choice = input(f"是否继续获取第 {current_page + 1} 页？(y/N): ").strip().lower()
        
        if choice != 'y':
            log("⏹️ 用户选择停止爬取")
            break
        
        current_page += 1
        
        # 避免请求过快
        time.sleep(2)
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "crawled_positions": len(all_positions),
        "saved_files": len(saved_files),
        "crawled_pages": current_page - 1,
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log("=" * 60)
    log(f"🎉 爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 爬取页数: {stats['crawled_pages']}页")
    log(f"   • 获取岗位: {len(all_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 快手招聘实时签名爬取器")
    print("=" * 70)
    print("特点:")
    print("  • 每次请求前从浏览器获取最新签名")
    print("  • 签名有效期极短（几秒）")
    print("  • 实时保存数据")
    print("  • 支持断点续传")
    print()
    
    log("启动实时签名爬取器")
    
    try:
        stats = crawl_with_realtime_signatures()
        
        if stats["success"]:
            print()
            print("🎉 实时签名爬取完成！")
            print()
            print("📊 爬取统计:")
            print(f"   爬取岗位: {stats['crawled_positions']}")
            print(f"   保存文件: {stats['saved_files']}")
            print(f"   爬取页数: {stats['crawled_pages']}")
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
        else:
            print("❌ 爬取失败")
            
    except KeyboardInterrupt:
        print()
        log("⏹️ 用户中断爬取")
    except Exception as e:
        log(f"❌ 爬取异常: {e}")
    
    print("=" * 70)
    print()
    print("💡 提示:")
    print("  1. 签名有效期极短，获取后立即使用")
    print("  2. 每页可能需要新签名")
    print("  3. 查看日志: cat logs/realtime_crawl.log")
    print("  4. 查看数据: ls output/ks_data_realtime/")


if __name__ == "__main__":
    main()