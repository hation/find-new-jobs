#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘API手动验证脚本
按照夸克规范：手动验证API，确保参数正确
"""

import json
import requests
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def verify_with_full_headers():
    """使用完整请求头验证API"""
    
    api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    
    # 完整的请求头（从你的信息中提取）
    headers = {
        ":authority": "zhaopin.meituan.com",
        ":method": "POST",
        ":path": "/api/official/job/getJobList",
        ":scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "content-length": "444",  # 注意：这个需要根据实际数据调整
        "content-type": "application/json",
        "cookie": "com.sankuai.recruitment.official.website_strategy=; _lxsdk_cuid=19e3f8d1caf13-0185d95410131b8-17525631-13c680-19e3f8d1cb0c8; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; weixinType=1; logan_session_token=mnv6s1i0i01o1e3c16ld; _lxsdk_s=19e4b11b608-d33-e63-cb8%7C%7C27",
        "origin": "https://zhaopin.meituan.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
        "sec-ch-ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    print("🔍 使用完整请求头验证API")
    print("=" * 60)
    
    # 尝试不同的请求体格式
    test_bodies = [
        {
            "name": "尝试1: 观察到的格式",
            "body": {}  # 空对象，观察实际请求
        },
        {
            "name": "尝试2: 基础参数",
            "body": {
                "cityList": ["001019002"],
                "jfJgList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "page": 1,
                "pageSize": 10,
                "sortField": "updateTime",
                "sortOrder": "desc"
            }
        },
        {
            "name": "尝试3: 字符串格式",
            "body": {
                "cityList": "001019002",
                "jfJgList": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
                "page": 1,
                "pageSize": 10
            }
        },
        {
            "name": "尝试4: 最小参数",
            "body": {
                "cityList": "001019002",
                "page": 1,
                "pageSize": 10
            }
        }
    ]
    
    for test in test_bodies:
        print(f"\n📋 {test['name']}")
        print(f"📦 请求体: {json.dumps(test['body'], ensure_ascii=False)}")
        
        try:
            # 更新content-length
            body_json = json.dumps(test['body'])
            headers["content-length"] = str(len(body_json))
            
            response = requests.post(
                api_url,
                headers=headers,
                data=body_json,
                timeout=10
            )
            
            print(f"📥 响应状态: {response.status_code}")
            print(f"📋 响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"📊 响应JSON:")
                    print(f"  状态码: {result.get('code', '无')}")
                    print(f"  消息: {result.get('message', '无')}")
                    
                    if result.get('code') == 200:
                        print("✅ API请求成功!")
                        data = result.get('data', {})
                        print(f"  数据字段: {list(data.keys())}")
                        return test['body']  # 返回成功的格式
                    else:
                        print(f"❌ API返回错误: {result.get('message')}")
                except json.JSONDecodeError:
                    print(f"📄 响应文本: {response.text[:500]}...")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"💥 请求异常: {str(e)}")
    
    return None


def analyze_error_pattern():
    """分析错误模式"""
    print("\n" + "=" * 60)
    print("🔧 错误模式分析")
    print("=" * 60)
    
    print("观察到的问题:")
    print("1. ❌ 所有请求都返回: '请求参数格式不正确！'")
    print("2. ✅ HTTP状态码: 200 (网络请求成功)")
    print("3. ❌ API状态码: 不是200 (业务逻辑失败)")
    
    print("\n💡 可能的原因:")
    print("1. 🔐 认证问题: Cookie可能已过期或需要特定格式")
    print("2. 📝 参数格式: 需要特定的参数格式或字段名")
    print("3. 🕒 时间戳: 可能需要时间戳或签名")
    print("4. 🔄 会话状态: 需要先访问页面建立会话")
    
    print("\n🔍 建议的解决方案:")
    print("1. 📋 手动访问美团招聘网站")
    print("2. 🖥️ 在浏览器中应用筛选条件")
    print("3. 🔧 打开开发者工具 -> Network")
    print("4. 📡 找到getJobList请求")
    print("5. 📋 复制完整的Request Payload")
    print("6. 🔄 使用完全相同的参数测试")
    
    return None


def test_with_session():
    """测试先建立会话"""
    print("\n" + "=" * 60)
    print("🔄 测试先建立会话")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. 先访问主页
    print("1. 📄 访问美团招聘主页...")
    try:
        home_response = session.get("https://zhaopin.meituan.com", timeout=10)
        print(f"   ✅ 主页访问成功: {home_response.status_code}")
        print(f"   🍪 获取Cookie: {len(session.cookies)} 个")
    except Exception as e:
        print(f"   ❌ 主页访问失败: {str(e)}")
        return None
    
    # 2. 访问筛选页面
    print("\n2. 🔍 访问筛选页面...")
    filter_url = "https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001"
    try:
        filter_response = session.get(filter_url, timeout=10)
        print(f"   ✅ 筛选页面访问成功: {filter_response.status_code}")
        print(f"   📏 页面大小: {len(filter_response.text)} 字节")
    except Exception as e:
        print(f"   ❌ 筛选页面失败: {str(e)}")
        return None
    
    # 3. 尝试API请求
    print("\n3. 📡 尝试API请求...")
    api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    
    # 使用session的headers
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": filter_url,
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # 尝试不同的参数
    test_params = [
        {"cityList": "001019002", "page": 1, "pageSize": 10},
        {"cityList": ["001019002"], "page": 1, "pageSize": 10},
        {}
    ]
    
    for params in test_params:
        print(f"\n   📦 测试参数: {json.dumps(params)}")
        try:
            response = session.post(
                api_url,
                headers=headers,
                json=params,
                timeout=10
            )
            
            print(f"   📥 响应: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📊 结果: {result.get('message', '无消息')}")
                
                if result.get('code') == 200:
                    print("   ✅ API请求成功!")
                    data = result.get('data', {})
                    print(f"     数据字段: {list(data.keys())}")
                    return params
        except Exception as e:
            print(f"   ❌ 请求失败: {str(e)}")
    
    return None


def main():
    """主函数"""
    print("🚀 美团招聘API手动验证")
    print("按照夸克规范：先手动验证，再自动化")
    print("=" * 60)
    
    # 方法1: 使用完整请求头
    print("\n🔧 方法1: 使用完整请求头验证")
    successful_format = verify_with_full_headers()
    
    if successful_format:
        print("\n" + "=" * 60)
        print("🎉 验证成功!")
        print("=" * 60)
        print(f"📋 成功格式: {json.dumps(successful_format, ensure_ascii=False)}")
        return successful_format
    
    # 方法2: 建立会话
    print("\n🔧 方法2: 建立会话后验证")
    successful_format = test_with_session()
    
    if successful_format:
        print("\n" + "=" * 60)
        print("🎉 验证成功!")
        print("=" * 60)
        print(f"📋 成功格式: {json.dumps(successful_format, ensure_ascii=False)}")
        return successful_format
    
    # 方法3: 分析错误
    print("\n🔧 方法3: 错误分析")
    analyze_error_pattern()
    
    print("\n" + "=" * 60)
    print("⚠️ 所有验证方法失败")
    print("=" * 60)
    
    print("\n💡 按照夸克规范，下一步:")
    print("1. 📋 手动在浏览器中测试API")
    print("2. 🔍 获取准确的请求参数")
    print("3. 📝 记录成功案例")
    print("4. 🔄 更新爬取器代码")
    
    return None


if __name__ == "__main__":
    result = main()
    
    if result:
        # 保存成功格式
        with open("verified_api_format.json", "w", encoding="utf-8") as f:
            json.dump({
                "verified_time": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "successful_format": result,
                "api_url": "https://zhaopin.meituan.com/api/official/job/getJobList",
                "note": "手动验证成功的参数格式"
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 验证结果已保存: verified_api_format.json")
    else:
        print(f"\n📝 请手动验证API并记录成功格式")