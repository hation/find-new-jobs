#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘真实数据爬取器
使用最新的有效签名参数立即开始爬取
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# 使用你提供的最新参数
LATEST_HEADERS = {
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
    # 最新的签名参数
    "sign": "e180189d2f126c56a1cff2346bff8df22c6390e51e33cdb98695ac765272036c",
    "signtimestamp": "1779441068746"
}

# API配置
API_URL = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"

# 输出目录
OUTPUT_DIR = "output/ks_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 日志文件
LOG_FILE = "logs/real_crawl.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    # 写入日志文件
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_message + "\n")


def test_api_connection() -> Optional[Dict[str, Any]]:
    """测试API连接"""
    log("🔍 测试API连接...")
    
    params = {
        "pageNum": 1,
        "pageSize": 5,  # 只取5条测试
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        start_time = time.time()
        response = requests.get(
            API_URL,
            params=params,
            headers=LATEST_HEADERS,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        log(f"✅ 请求完成 - 状态码: {response.status_code}, 耗时: {elapsed_time:.2f}秒")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0:
                result = data.get("result", {})
                total = result.get('total', 0)
                positions = result.get('list', [])
                
                log(f"🎉 API连接成功!")
                log(f"   总岗位数: {total}")
                log(f"   获取岗位: {len(positions)}")
                log(f"   签名时间戳: {LATEST_HEADERS['signtimestamp']}")
                log(f"   签名: {LATEST_HEADERS['sign'][:20]}...")
                
                return data
            else:
                log(f"❌ API业务错误: code={data.get('code')}, message={data.get('message')}")
                return None
        else:
            log(f"❌ HTTP错误: {response.status_code}")
            log(f"   响应内容: {response.text[:200]}")
            return None
            
    except Exception as e:
        log(f"❌ 测试失败: {e}")
        return None


def fetch_page(page_num: int, page_size: int = 10) -> Optional[Dict[str, Any]]:
    """获取单页数据"""
    log(f"📄 获取第 {page_num} 页数据...")
    
    params = {
        "pageNum": page_num,
        "pageSize": page_size,
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=LATEST_HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0:
                result = data.get("result", {})
                positions = result.get('list', [])
                log(f"✅ 第 {page_num} 页获取成功: {len(positions)} 个岗位")
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
    """提取标准字段（12个核心字段）"""
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
        "salaryRange": "",  # 快手API未提供薪资信息
        
        # 附加信息
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "real_time",
        "source": "kuaishou_real",
        
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
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    position_id = position.get("positionId", "unknown")
    filename = f"ks_position_{position_id}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # 保存数据
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(position, f, ensure_ascii=False, indent=2)
        
        return filepath
    except Exception as e:
        log(f"❌ 保存失败: {e}")
        return ""


def crawl_all_pages(max_pages: int = 10) -> Dict[str, Any]:
    """爬取所有页面数据"""
    log(f"🚀 开始爬取所有页面（最大 {max_pages} 页）")
    start_time = datetime.now()
    
    all_positions = []
    saved_files = []
    
    # 先获取第一页了解总页数
    first_page_data = fetch_page(1, 5)  # 第一页只取5条测试
    
    if not first_page_data:
        log("❌ 第一页获取失败，终止爬取")
        return {"success": False, "message": "第一页获取失败"}
    
    result = first_page_data.get("result", {})
    total_positions = result.get('total', 0)
    total_pages = result.get('pages', 0)
    first_page_positions = result.get('list', [])
    
    log(f"📊 发现 {total_positions} 个岗位，共 {total_pages} 页")
    
    # 处理第一页数据
    for raw_position in first_page_positions:
        standard_position = extract_standard_fields(raw_position)
        filepath = save_position(standard_position)
        if filepath:
            saved_files.append(filepath)
        all_positions.append(standard_position)
    
    log(f"✅ 第一页处理完成: {len(first_page_positions)} 个岗位")
    
    # 计算实际要爬取的页数
    actual_pages = min(max_pages, total_pages)
    
    # 爬取剩余页
    for page_num in range(2, actual_pages + 1):
        # 避免请求过快
        time.sleep(2)
        
        # 显示进度
        progress = (page_num - 1) / actual_pages * 100
        log(f"📊 进度: {page_num-1}/{actual_pages}页 ({progress:.1f}%)")
        
        page_data = fetch_page(page_num)
        
        if not page_data:
            log(f"⚠️ 第 {page_num} 页获取失败，跳过")
            continue
        
        page_positions = page_data.get("result", {}).get("list", [])
        
        for raw_position in page_positions:
            standard_position = extract_standard_fields(raw_position)
            filepath = save_position(standard_position)
            if filepath:
                saved_files.append(filepath)
            all_positions.append(standard_position)
        
        log(f"✅ 第 {page_num} 页处理完成: {len(page_positions)} 个岗位")
    
    # 统计信息
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    stats = {
        "success": True,
        "total_positions": total_positions,
        "crawled_positions": len(all_positions),
        "saved_files": len(saved_files),
        "crawled_pages": actual_pages,
        "elapsed_time": elapsed_time,
        "output_dir": OUTPUT_DIR,
        "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "signature_timestamp": LATEST_HEADERS['signtimestamp']
    }
    
    log("=" * 60)
    log(f"🎉 爬取完成!")
    log(f"   • 总用时: {elapsed_time:.2f}秒")
    log(f"   • 爬取页数: {actual_pages}页")
    log(f"   • 获取岗位: {len(all_positions)}个")
    log(f"   • 保存文件: {len(saved_files)}个")
    log(f"   • 输出目录: {OUTPUT_DIR}")
    log("=" * 60)
    
    return stats


def main():
    """主函数"""
    print("=" * 70)
    print("🚀 快手招聘真实数据爬取器")
    print("=" * 70)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"签名时间戳: {LATEST_HEADERS['signtimestamp']}")
    print(f"签名: {LATEST_HEADERS['sign'][:20]}...")
    print()
    
    # 测试API连接
    test_result = test_api_connection()
    
    if not test_result:
        print("❌ API连接测试失败，请检查签名参数")
        return
    
    print()
    print("✅ API连接测试成功！")
    print()
    
    # 询问爬取页数
    try:
        max_pages = input("请输入最大爬取页数（默认5）: ").strip()
        max_pages = int(max_pages) if max_pages else 5
    except ValueError:
        print("⚠️ 输入无效，使用默认值5")
        max_pages = 5
    
    print()
    print(f"🚀 开始爬取 {max_pages} 页数据...")
    print()
    
    # 开始爬取
    stats = crawl_all_pages(max_pages)
    
    if stats["success"]:
        print()
        print("🎉 真实数据爬取完成！")
        print()
        print("📊 爬取统计:")
        print(f"   总岗位数: {stats['total_positions']}")
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
        
        print()
        print("💡 下一步:")
        print("  1. 查看数据文件: ls output/ks_data/")
        print("  2. 查看日志: cat logs/real_crawl.log")
        print("  3. 分析数据: python scripts/analyze_data.py")
        print("  4. 继续爬取: 运行此脚本并输入更大页数")
    else:
        print("❌ 爬取失败，请查看日志文件")
    
    print("=" * 70)


if __name__ == "__main__":
    main()