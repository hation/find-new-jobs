#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的快手API签名参数
使用刚刚提供的有效签名
"""

import requests
import json
import time
from datetime import datetime

# 使用你提供的新参数
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Cookie": "aliyungf_tc=62d111759197e609997a914760f88ccc44c00ef73b2f542817802af91250a937; accessproxy_session=01b7eac0ccce9f49aa335ac52039ec8a825379cdb3EAIiE3poYW9waW4ua3VhaXNob3UuY24KJGJiODA2NjMzLTVmODgtNGI5Yy1iM2QyLTBlMjE0ZmI1NGEzZioVEhFVTkFVVEhPUklaRURfVVNFUgoAGLHJ1Of+Mw==; apdid=1e615e70-2858-4116-bd0e-5e461bd10eb4cc68ec35bc432b6780dc98e63f48cce7:1779186916:1; weblogger_did=web_754734862580340E",
    "Host": "zhaopin.kuaishou.cn",
    "Pragma": "no-cache",
    "Referer": "https://zhaopin.kuaishou.cn/",
    "Sec-Ch-Ua": "\"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\", \"Not/A)Brand\";v=\"99\"",
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": "\"macOS\"",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    # 新的签名参数
    "sign": "540d4202e9f24585e677f861a0171e56893ae1f5a90558d5320c7a829acd648e",
    "signtimestamp": "1779440014248"
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
print("🔍 测试新的快手API签名参数")
print("=" * 70)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"签名时间戳: {headers['signtimestamp']}")
print(f"签名: {headers['sign'][:20]}...")
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
    
    # 解析JSON响应
    try:
        data = response.json()
        print("📊 API响应解析:")
        print(f"   错误码: {data.get('code')}")
        print(f"   消息: {data.get('message')}")
        
        if data.get("code") == 0:
            result = data.get("result", {})
            total = result.get('total', 0)
            page_num = result.get('pageNum', 1)
            page_size = result.get('pageSize', 10)
            total_pages = result.get('pages', 0)
            positions = result.get('list', [])
            
            print(f"   总岗位数: {total}")
            print(f"   当前页: {page_num}")
            print(f"   每页数量: {page_size}")
            print(f"   总页数: {total_pages}")
            print(f"   获取岗位: {len(positions)}")
            print()
            
            if positions:
                print("🎉 签名有效！API请求成功！")
                print()
                print("📋 岗位示例:")
                for i, position in enumerate(positions[:3], 1):
                    print(f"  {i}. {position.get('name', '未知')} - {position.get('workLocationCode', '未知')}")
                
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
                print("🎉 签名有效！可以开始真实数据爬取！")
                
            else:
                print("⚠️ API返回成功但未获取到岗位数据")
                
        else:
            print()
            print("❌ API返回错误:")
            print(f"   错误码: {data.get('code')}")
            print(f"   错误消息: {data.get('message')}")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        print(f"   响应前200字符: {response.text[:200]}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ 网络请求失败: {e}")
    
except Exception as e:
    print(f"❌ 未知错误: {e}")

print("=" * 70)