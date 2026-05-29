#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试快手API完整请求（包含签名）
基于你提供的完整请求头信息
"""

import requests
import json
import time

# 使用你提供的完整请求头
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
    # 签名参数（需要从浏览器实时获取）
    "sign": "dabac2d9f1a8c2c8dafb1b1b8492111f3e046a9a05e3db7b8e459ea3d26cbee9",
    "signtimestamp": "1779427015302"
}

# API配置
API_URL = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"

# 请求参数
params = {
    "pageNum": 1,
    "pageSize": 10,
    "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
    "positionNatureCode": "C001",
    "recruitProject": "socialr",
    "workLocationCode": "domestic"
}

print("=" * 70)
print("🔍 测试快手API完整请求（包含签名）")
print("=" * 70)
print(f"API地址: {API_URL}")
print(f"签名时间戳: {headers.get('signtimestamp')}")
print(f"签名: {headers.get('sign')[:20]}...")
print()

try:
    print("📡 发送API请求...")
    start_time = time.time()
    
    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=30
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"✅ 请求完成")
    print(f"   状态码: {response.status_code}")
    print(f"   响应时间: {elapsed_time:.2f}秒")
    print(f"   响应大小: {len(response.text)} 字节")
    print()
    
    # 显示响应头
    print("📋 响应头信息:")
    for key, value in response.headers.items():
        if key.lower() in ['content-type', 'server', 'date', 'x-ksap-request-uuid']:
            print(f"   {key}: {value}")
    
    print()
    
    # 尝试解析JSON
    try:
        data = response.json()
        print("📊 API响应解析:")
        print(f"   错误码: {data.get('code')}")
        print(f"   消息: {data.get('message')}")
        
        if data.get("code") == 0:
            result = data.get("result", {})
            print(f"   总岗位数: {result.get('total', 0)}")
            print(f"   当前页: {result.get('pageNum', 1)}")
            print(f"   每页数量: {result.get('pageSize', 10)}")
            print(f"   总页数: {result.get('pages', 0)}")
            print(f"   获取岗位: {len(result.get('list', []))}")
            
            # 显示前几个岗位
            positions = result.get("list", [])
            if positions:
                print()
                print("📋 岗位示例:")
                for i, position in enumerate(positions[:3], 1):
                    print(f"   {i}. {position.get('name', '未知')} - {position.get('workLocationCode', '未知')}")
            
            print()
            print("🎉 签名有效！API请求成功！")
            
        else:
            print()
            print("❌ API返回错误:")
            print(f"   错误码: {data.get('code')}")
            print(f"   错误消息: {data.get('message')}")
            print()
            print("💡 可能的原因:")
            print("   1. 签名已过期")
            print("   2. Cookie已过期")
            print("   3. 需要重新登录")
            print("   4. API参数错误")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"   响应前200字符: {response.text[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 网络请求失败: {e}")
    
except Exception as e:
    print(f"❌ 未知错误: {e}")

print("=" * 70)

# 提供解决方案
print("\n🔧 解决方案:")
print("1. 实时获取签名: 签名参数(sign, signtimestamp)需要实时生成")
print("2. 使用浏览器自动化: 通过浏览器获取实时签名")
print("3. 模拟浏览器请求: 使用Playwright/Selenium模拟完整请求")
print("4. 分析签名算法: 逆向分析签名生成逻辑")
print()
print("💡 建议方案:")
print("• 方案A: 使用浏览器自动化工具(Playwright)模拟完整浏览器请求")
print("• 方案B: 分析JavaScript代码，实现签名算法")
print("• 方案C: 使用中间人代理捕获实时请求")
print()
print("🚀 推荐实施:")
print("基于夸克项目的经验，建议使用浏览器自动化方案")
print("1. 使用Playwright打开快手招聘网站")
print("2. 自动获取实时Cookie和签名")
print("3. 发送API请求获取数据")
print("4. 处理数据并保存")
print()
print("📋 下一步:")
print("1. 安装浏览器自动化工具: pip install playwright")
print("2. 安装浏览器: python -m playwright install")
print("3. 实现浏览器自动化爬取器")
print("4. 测试并开始爬取")