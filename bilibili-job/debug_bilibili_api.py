#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站API调试脚本
用于调试API请求问题
"""

import requests
import json
import time
from datetime import datetime

def debug_api_request():
    """调试API请求"""
    
    print("=" * 70)
    print("🔍 B站API调试脚本")
    print("=" * 70)
    
    # 基础配置
    base_url = "https://jobs.bilibili.com"
    api_endpoint = "/api/srs/position/positionList"
    api_url = f"{base_url}{api_endpoint}"
    
    # 请求头（从你提供的headers）
    headers = {
        "authority": "jobs.bilibili.com",
        "method": "POST",
        "path": "/api/srs/position/positionList",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "content-length": "265",
        "content-type": "application/json",
        "cookie": "CURRENT_FNVAL=4048; buvid3=5D4FF9D2-A1C1-DCAD-8082-AB4C544E714000840infoc; b_nut=1771296600; _uuid=423969C4-C232-C364-3AFF-2AC10F1ADFF2C01646infoc; buvid_fp=6672304e623983edfd6286c07cb4dd77; buvid4=DE2608B1-2645-F0C8-D0B6-D11118FC8FFB02410-026021710-JsiGD1Ff0mxSW/UEw4D/Cw%3D%3D; CURRENT_QUALITY=0; rpdid=|(kY)lRkJl))0J'u~~~klu)|); bsource=search_baidu",
        "lunar-id": f"lunar-{int(time.time() * 1000)}-7446043945710",
        "origin": "https://jobs.bilibili.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "x-appkey": "ops.ehr-api.auth",
        "x-channel": "social",
        "x-csrf": "9741c476-d601-4c6d-8996-6a3912e0c0da",
        "x-usertype": "2"
    }
    
    # 请求数据（从你提供的payload）
    request_data = {
        "pageSize": 10,
        "pageNum": 1,
        "positionName": "",
        "postCode": ["03", "05", "11", "08", "07"],
        "postCodeList": ["03", "05", "11", "08", "07"],
        "workLocationList": [],
        "workTypeList": ["3"],
        "positionTypeList": ["3"],
        "deptCodeList": [],
        "recruitType": 0,
        "practiceTypes": [],
        "onlyHotRecruit": 0
    }
    
    print(f"🌐 API地址: {api_url}")
    print(f"📋 请求方法: POST")
    print(f"📊 请求头数量: {len(headers)}")
    print(f"📦 请求数据大小: {len(json.dumps(request_data))} 字节")
    print()
    
    # 尝试几种不同的请求方式
    
    print("🧪 测试1: 原始请求（无ajSessionId）")
    try:
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data,
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        print(f"  响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  响应码: {data.get('code')}")
                print(f"  消息: {data.get('message')}")
                
                if data.get("code") == 0:
                    print("  ✅ 请求成功！")
                    jobs = data.get("data", {}).get("list", [])
                    print(f"  获取岗位数: {len(jobs)}")
                    
                    if jobs:
                        print("  📋 岗位样本:")
                        for i, job in enumerate(jobs[:3], 1):
                            print(f"    {i}. {job.get('positionName')} - {job.get('workLocation')}")
                else:
                    print(f"  ❌ API错误: {data.get('message')}")
                    
            except json.JSONDecodeError as e:
                print(f"  ❌ JSON解析错误: {e}")
                print(f"  原始响应: {response.text[:500]}")
        else:
            print(f"  ❌ HTTP错误: {response.status_code}")
            print(f"  错误响应: {response.text[:500]}")
            
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
    
    print()
    
    # 测试2: 尝试添加空的ajSessionId
    print("🧪 测试2: 添加空的ajSessionId")
    try:
        request_data_with_session = request_data.copy()
        request_data_with_session["ajSessionId"] = ""
        
        response = requests.post(
            api_url,
            headers=headers,
            json=request_data_with_session,
            timeout=10
        )
        
        print(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  响应码: {data.get('code')}")
            print(f"  消息: {data.get('message')}")
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
    
    print()
    
    # 测试3: 尝试从Cookie中提取可能的session id
    print("🧪 测试3: 分析Cookie")
    cookie_str = headers.get("cookie", "")
    cookies = {}
    for cookie in cookie_str.split(";"):
        if "=" in cookie:
            key, value = cookie.strip().split("=", 1)
            cookies[key] = value
            print(f"  🍪 {key}: {value[:50]}..." if len(value) > 50 else f"  🍪 {key}: {value}")
    
    print()
    
    # 测试4: 尝试访问首页获取session
    print("🧪 测试4: 访问首页")
    try:
        home_response = requests.get(
            "https://jobs.bilibili.com",
            headers={
                "User-Agent": headers["user-agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            timeout=10
        )
        
        print(f"  首页状态码: {home_response.status_code}")
        print(f"  首页Cookie: {home_response.cookies}")
        
        # 检查是否有Set-Cookie头
        if 'set-cookie' in home_response.headers:
            print(f"  📨 Set-Cookie头: {home_response.headers['set-cookie'][:200]}...")
        
    except Exception as e:
        print(f"  ❌ 首页访问异常: {e}")
    
    print()
    print("=" * 70)
    print("📋 调试总结")
    print("=" * 70)
    
    print("可能的问题和解决方案:")
    print("1. ❌ ajSessionId不能为空 - API需要有效的session id")
    print("2. 💡 解决方案:")
    print("   a) 从浏览器获取最新的ajSessionId")
    print("   b) 先访问首页获取session")
    print("   c) 检查Cookie中是否有session相关信息")
    print("   d) 可能需要先调用其他API获取session")
    
    print()
    print("🔧 建议的下一步:")
    print("1. 使用浏览器开发者工具查看最新的API请求")
    print("2. 检查Network标签中的请求详情")
    print("3. 获取最新的ajSessionId值")
    print("4. 更新配置文件中的参数")
    
    print()
    print("💡 快速获取ajSessionId的方法:")
    print("1. 打开 https://jobs.bilibili.com")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Network标签")
    print("4. 刷新页面")
    print("5. 找到 positionList 请求")
    print("6. 查看Request Payload中的ajSessionId值")

if __name__ == "__main__":
    debug_api_request()