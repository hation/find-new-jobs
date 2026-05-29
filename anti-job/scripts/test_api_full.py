#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整API测试 - 使用完整的请求参数
"""

import json
import requests
import sys

print("="*70)
print("🔧 完整API测试")
print("="*70)

# API配置
api_url = "https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Content-Type": "application/json;charset=UTF-8",
    "Accept": "application/json",
    "Origin": "https://talent.antgroup.com",
    "Referer": "https://talent.antgroup.com/",
    "front-user-id": "729d74a1-d280-4486-a5d6-18aa210e4aff43"
}

# Cookies
cookies = {
    "ctoken": "bigfish_ctoken_1a9652509k",
    "SESSION": "OTEzODQxNjhEMzQ4OTdDOTFFNzAwNzMzMEYyMzMyOEI="
}

# 完整的请求体（基于之前确认的格式）
request_body = {
    "regions": "",
    "categories": "97,103,143,124,152,146",
    "subCategories": "97,103,143,124,152,146,98,99,100,101,102,403,404,405,406,104,105,106,107,108,109,110,111,172,474,475,476,477,478,479,480,481,482,483,484,529,757,758,759,763,834,846,847,849,144,145,177,446,447,448,125,126,127,128,129,175,445,716,812,824,825,100000015,100000016,101300030,101300031,101300032,101300033,153,154,155,156,179,461,462,463,464,465,466,467,468,469,470,471,472,473,512,513,147,148,149,150,151,178,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426",
    "bgCode": "",
    "socialQrCode": "",
    "pageIndex": 1,
    "pageSize": 10,
    "channel": "group_official_site",
    "language": "zh"
}

print(f"📡 API端点: {api_url}")
print(f"📋 主要类别: {len(request_body['categories'].split(','))}个")
print(f"📋 子类别: {len(request_body['subCategories'].split(','))}个")

print(f"\n🔗 发送完整请求...")

try:
    # 确保所有字符串都是ASCII安全的
    safe_headers = {}
    for k, v in headers.items():
        safe_headers[str(k).encode('ascii', 'ignore').decode('ascii')] = str(v).encode('ascii', 'ignore').decode('ascii')
    
    safe_cookies = {}
    for k, v in cookies.items():
        safe_cookies[str(k).encode('ascii', 'ignore').decode('ascii')] = str(v).encode('ascii', 'ignore').decode('ascii')
    
    response = requests.post(
        api_url,
        headers=safe_headers,
        cookies=safe_cookies,
        json=request_body,
        timeout=30
    )
    
    print(f"📥 响应状态码: {response.status_code}")
    print(f"📥 响应大小: {len(response.text)}字节")
    
    if response.status_code == 200:
        print("✅ HTTP请求成功")
        
        try:
            data = response.json()
            print(f"📊 JSON解析成功")
            
            # 详细分析响应
            print(f"\n🔍 详细响应分析:")
            print(f"  • success: {data.get('success')}")
            print(f"  • totalCount: {data.get('totalCount')}")
            print(f"  • pageSize: {data.get('pageSize')}")
            print(f"  • currentPage: {data.get('currentPage')}")
            
            content = data.get("content", [])
            print(f"  • content长度: {len(content)}")
            
            if content:
                print(f"\n📋 岗位列表 ({len(content)}个):")
                for i, position in enumerate(content[:3], 1):  # 只显示前3个
                    print(f"  {i}. {position.get('name')}")
                    print(f"     地点: {position.get('workLocations')}")
                    print(f"     部门: {position.get('department')}")
                    print(f"     类别ID: {position.get('categories')}")
                    print()
                
                if len(content) > 3:
                    print(f"  ... 还有{len(content)-3}个岗位")
            
            # 检查错误信息
            if data.get("success") is not True:
                print(f"\n⚠️  API返回警告:")
                print(f"  • errorMsg: {data.get('errorMsg')}")
                print(f"  • errorCode: {data.get('errorCode')}")
            
            if data.get("totalCount", 0) > 0:
                print(f"\n🎉 API测试成功! 找到{data['totalCount']}个岗位")
                print(f"📊 总页数: {(data['totalCount'] + data['pageSize'] - 1) // data['pageSize']}")
            else:
                print(f"\n⚠️  找到0个岗位，可能参数需要调整")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"📝 响应前500字符: {response.text[:500]}")
            
    else:
        print(f"❌ HTTP请求失败")
        print(f"📝 响应前500字符: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("❌ 请求超时")
except requests.exceptions.ConnectionError:
    print("❌ 连接错误")
except Exception as e:
    print(f"❌ 异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)