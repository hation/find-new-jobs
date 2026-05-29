#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快手招聘自动爬取器
使用最新签名立即开始爬取
"""

import requests
import json
import os
import time
from datetime import datetime

print("=" * 70)
print("🚀 快手招聘自动爬取器")
print("=" * 70)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 使用你提供的最新签名（2026-05-22 17:11）
LATEST_SIGN = "e180189d2f126c56a1cff2346bff8df22c6390e51e33cdb98695ac765272036c"
LATEST_TIMESTAMP = "1779441068746"

# API配置
API_URL = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"

# 输出目录
OUTPUT_DIR = "output/ks_auto"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 请求头
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
    "sign": LATEST_SIGN,
    "signtimestamp": LATEST_TIMESTAMP
}

def test_connection():
    """测试连接"""
    print("🔍 测试API连接...")
    
    params = {
        "pageNum": 1,
        "pageSize": 1,
        "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
        "positionNatureCode": "C001",
        "recruitProject": "socialr",
        "workLocationCode": "domestic"
    }
    
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            code = data.get("code")
            message = data.get("message", "")
            
            if code == 0:
                print(f"✅ 连接成功！签名有效")
                return True
            else:
                print(f"❌ 连接失败: code={code}, message={message}")
                print(f"   签名时间戳: {LATEST_TIMESTAMP}")
                print(f"   当前时间: {int(time.time() * 1000)}")
                print(f"   时间差: {int(time.time() * 1000) - int(LATEST_TIMESTAMP)}ms")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 连接异常: {e}")
        return False

def fetch_page(page_num, page_size=5):
    """获取单页数据"""
    print(f"📄 获取第 {page_num} 页...")
    
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
        response = requests.get(API_URL, params=params, headers=headers, timeout=30)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("code") == 0:
                result = data.get("result", {})
                positions = result.get('list', [])
                print(f"✅ 获取成功: {len(positions)} 个岗位, 耗时: {elapsed_time:.2f}秒")
                return data
            else:
                print(f"❌ API错误: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def save_position(position_data):
    """保存岗位数据"""
    position_id = str(position_data.get("id", "unknown"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 标准化数据
    standard_data = {
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
        "company": "快手",
        "crawlTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "crawlMode": "auto",
        "source": "kuaishou_auto",
        "signatureTimestamp": LATEST_TIMESTAMP,
        "signature": LATEST_SIGN[:20] + "..."
    }
    
    filename = f"ks_position_{position_id}_{timestamp}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(standard_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None

def main():
    """主函数"""
    # 测试连接
    if not test_connection():
        print()
        print("⚠️ 签名可能已过期")
        print("💡 解决方案:")
        print("   1. 打开浏览器访问 https://zhaopin.kuaishou.cn")
        print("   2. 获取最新的 sign 和 signtimestamp")
        print("   3. 更新脚本中的 LATEST_SIGN 和 LATEST_TIMESTAMP")
        print("   4. 重新运行脚本")
        return
    
    print()
    print("✅ 连接成功！开始爬取...")
    print()
    
    # 获取第一页数据
    page_data = fetch_page(1, page_size=5)
    
    if not page_data:
        print("❌ 第一页获取失败")
        return
    
    result = page_data.get("result", {})
    positions = result.get('list', [])
    total_positions = result.get('total', 0)
    total_pages = result.get('pages', 0)
    
    print(f"📊 发现 {total_positions} 个岗位，共 {total_pages} 页")
    print()
    
    if not positions:
        print("⚠️ 第一页无数据")
        return
    
    # 保存第一页数据
    saved_files = []
    
    for i, position in enumerate(positions, 1):
        print(f"📝 处理第 {i} 个岗位: {position.get('name', '未知')[:30]}...")
        filepath = save_position(position)
        if filepath:
            saved_files.append(filepath)
    
    print()
    print("=" * 60)
    print("🎉 自动爬取完成！")
    print(f"   获取岗位: {len(positions)} 个")
    print(f"   保存文件: {len(saved_files)} 个")
    print(f"   输出目录: {OUTPUT_DIR}")
    print()
    
    # 显示保存的文件
    if saved_files:
        print("📁 保存的文件:")
        for i, filepath in enumerate(saved_files, 1):
            filename = os.path.basename(filepath)
            print(f"  {i}. {filename}")
    
    print("=" * 60)
    
    # 显示第一个岗位的详细信息
    if positions:
        first_position = positions[0]
        print()
        print("📄 第一个岗位详情:")
        print(f"   ID: {first_position.get('id')}")
        print(f"   名称: {first_position.get('name')}")
        print(f"   地点: {first_position.get('workLocationCode')}")
        print(f"   类别: {first_position.get('positionCategoryCode')}")
        print(f"   工作经验: {first_position.get('workExperienceCode')}")
        print(f"   更新时间: {first_position.get('updateTime')}")
        print(f"   工作职责: {first_position.get('description', '')[:100]}...")
    
    print()
    print("💡 下一步:")
    print("  1. 查看数据: ls output/ks_auto/")
    print("  2. 查看文件内容: cat output/ks_auto/*.json")
    print("  3. 获取最新签名继续爬取")
    print("  4. 使用浏览器自动化方案爬取更多数据")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("⏹️ 用户中断")
    except Exception as e:
        print(f"❌ 程序异常: {e}")