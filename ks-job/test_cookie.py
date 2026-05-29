#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试快手API Cookie有效性
使用你提供的真实Cookie进行测试
"""

import requests
import json
import time

# 使用你提供的真实Cookie（从之前的请求头中提取）
COOKIE = "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjEwZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E"

# API配置
API_URL = "https://zhaopin.kuaishou.cn/recruit/e/api/v1/open/positions/simple"

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Referer": "https://zhaopin.kuaishou.cn/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Cookie": COOKIE
}

# 请求参数
params = {
    "pageNum": 1,
    "pageSize": 5,
    "positionCategoryCode": "J0005,J0004,J0013,J0006,J0014",
    "positionNatureCode": "C001",
    "recruitProject": "socialr",
    "workLocationCode": "domestic"
}

print("=" * 70)
print("🔍 测试快手API Cookie有效性")
print("=" * 70)
print(f"API地址: {API_URL}")
print(f"Cookie长度: {len(COOKIE)} 字符")
print(f"包含accessproxy_session: {'accessproxy_session' in COOKIE}")
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
            print("🎉 Cookie有效！API请求成功！")
            
        else:
            print()
            print("❌ API返回错误:")
            print(f"   错误码: {data.get('code')}")
            print(f"   错误消息: {data.get('message')}")
            print()
            print("💡 可能的原因:")
            print("   1. Cookie已过期")
            print("   2. 需要重新登录")
            print("   3. API参数错误")
            print("   4. 签名验证失败")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"   响应前200字符: {response.text[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 网络请求失败: {e}")
    
except Exception as e:
    print(f"❌ 未知错误: {e}")

print("=" * 70)

# 提供下一步建议
print("\n💡 下一步建议:")
print("1. 如果Cookie有效: 更新 config/.env 中的 KS_COOKIE_PLACEHOLDER")
print("2. 如果Cookie无效: 重新获取有效的Cookie")
print("3. 测试命令: python3 test_cookie.py")
print("4. 开始爬取: python3 src/ks_api_crawler.py")