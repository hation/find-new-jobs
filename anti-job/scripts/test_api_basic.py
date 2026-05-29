#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础API测试 - 验证连接和基本功能
"""

import json
import requests
import sys

print("="*70)
print("🔧 基础API测试")
print("="*70)

# 最简单的API配置
api_url = "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k"

# 使用ASCII-only headers避免编码问题
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json"
}

# 简化的cookies
cookies = {
    "ctoken": "bigfish_ctoken_1a9652509k"
}

# 最小化的请求体
request_body = {
    "regions": "",
    "categories": "97,103,143,124,152,146",
    "subCategories": "97",
    "bgCode": "",
    "socialQrCode": "",
    "pageIndex": 1,
    "pageSize": 5,
    "channel": "group_official_site",
    "language": "zh"
}

print(f"📡 API端点: {api_url}")
print(f"📋 Headers: {len(headers)}个")
print(f"🍪 Cookies: {len(cookies)}个")
print(f"📦 请求体大小: {len(json.dumps(request_body))}字节")

print(f"\n🔗 发送测试请求...")

try:
    # 使用ASCII编码确保安全
    ascii_headers = {}
    for k, v in headers.items():
        ascii_headers[str(k)] = str(v)
    
    response = requests.post(
        api_url,
        headers=ascii_headers,
        cookies=cookies,
        json=request_body,
        timeout=10
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应大小: {len(response.text)}字节")
    
    if response.status_code == 200:
        print("✅ HTTP请求成功")
        
        try:
            data = response.json()
            print(f"📊 JSON解析成功")
            
            # 检查基本结构
            print(f"\n🔍 响应结构:")
            print(f"  • success: {data.get('success')}")
            print(f"  • totalCount: {data.get('totalCount')}")
            print(f"  • pageSize: {data.get('pageSize')}")
            print(f"  • currentPage: {data.get('currentPage')}")
            
            content = data.get("content", [])
            print(f"  • content长度: {len(content)}")
            
            if content:
                print(f"\n🔍 第一个岗位:")
                first = content[0]
                print(f"  • id: {first.get('id')}")
                print(f"  • name: {first.get('name')}")
                print(f"  • workLocations: {first.get('workLocations')}")
            
            # 检查是否有错误信息
            if data.get("success") is not True:
                print(f"\n⚠️  API返回警告:")
                print(f"  • errorMsg: {data.get('errorMsg')}")
                print(f"  • errorCode: {data.get('errorCode')}")
            
            print(f"\n🎉 API测试成功!")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"📝 响应前200字符: {response.text[:200]}")
            
    else:
        print(f"❌ HTTP请求失败")
        print(f"📝 响应: {response.text[:200]}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.ConnectionError:
    print("❌ 连接错误")
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)