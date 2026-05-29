#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团API完整请求头测试
使用你提供的完整请求头信息
"""

import json
import requests
import time

def test_with_provided_headers():
    """使用提供的完整请求头测试"""
    
    api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    
    # 你提供的完整请求头（去除HTTP/2伪头部）
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "content-length": "444",  # 关键：444字节
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
    
    print("🔍 使用完整请求头测试美团API")
    print("=" * 60)
    print(f"📡 API地址: {api_url}")
    print(f"📋 请求头数量: {len(headers)}")
    print(f"📏 Content-Length: {headers['content-length']} 字节")
    print("=" * 60)
    
    # 尝试不同的请求体（基于444字节长度猜测）
    test_cases = [
        {
            "name": "猜测1: 完整参数格式",
            "body": {
                "cityList": "001019002",
                "jfJgList": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
                "page": 1,
                "pageSize": 10,
                "sortField": "updateTime",
                "sortOrder": "desc",
                "timestamp": int(time.time() * 1000)
            }
        },
        {
            "name": "猜测2: 数组格式",
            "body": {
                "cityList": ["001019002"],
                "jfJgList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "page": 1,
                "pageSize": 10,
                "sort": "updateTime_desc"
            }
        },
        {
            "name": "猜测3: 简写格式",
            "body": {
                "city": "001019002",
                "types": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
                "p": 1,
                "size": 10
            }
        },
        {
            "name": "猜测4: 带签名的格式",
            "body": {
                "params": {
                    "cityCode": "001019002",
                    "categoryList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                    "pageNo": 1,
                    "pageSize": 10
                },
                "sign": "mock_signature_placeholder",
                "t": int(time.time() * 1000)
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 测试: {test['name']}")
        
        # 计算实际长度
        body_json = json.dumps(test['body'], ensure_ascii=False, separators=(',', ':'))
        actual_length = len(body_json.encode('utf-8'))
        
        print(f"📦 请求体: {body_json[:100]}...")
        print(f"📏 实际长度: {actual_length} 字节")
        print(f"🎯 目标长度: 444 字节")
        
        # 调整content-length
        headers["content-length"] = str(actual_length)
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=body_json,
                timeout=10
            )
            
            print(f"📥 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"📊 响应消息: {result.get('message', '无消息')}")
                    
                    if result.get('code') == 200:
                        print("✅ API请求成功!")
                        data = result.get('data', {})
                        print(f"📋 数据字段: {list(data.keys())}")
                        if 'list' in data:
                            print(f"📊 岗位数量: {len(data['list'])}")
                            if data['list']:
                                first_job = data['list'][0]
                                print(f"👤 示例岗位: {first_job.get('jobName', '未知')}")
                        return test['body']
                    else:
                        print(f"❌ API错误: {result.get('code')} - {result.get('message')}")
                except json.JSONDecodeError:
                    print(f"📄 响应文本: {response.text[:200]}...")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"💥 请求异常: {str(e)}")
    
    return None

def analyze_content_length():
    """分析444字节的请求体内容"""
    print("\n" + "=" * 60)
    print("🔍 分析444字节请求体")
    print("=" * 60)
    
    print("📏 Content-Length: 444 字节")
    print("💡 这意味着请求体大约有444个字符（UTF-8编码）")
    
    # 猜测可能的参数结构
    base_params = {
        "cityList": "001019002",  # 11字符
        "jfJgList": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",  # 约55字符
        "page": 1,  # 1字符
        "pageSize": 10,  # 2字符
        "sortField": "updateTime",  # 10字符
        "sortOrder": "desc",  # 4字符
        "timestamp": 1747861234567  # 13字符
    }
    
    base_json = json.dumps(base_params, ensure_ascii=False, separators=(',', ':'))
    print(f"\n📋 基础参数JSON长度: {len(base_json.encode('utf-8'))} 字节")
    print(f"📦 基础参数: {base_json}")
    
    # 计算还差多少
    remaining = 444 - len(base_json.encode('utf-8'))
    print(f"📊 还差 {remaining} 字节")
    
    print("\n💡 可能包含的额外字段:")
    print("1. 🔑 签名字段 (sign/signature): 约64-128字符")
    print("2. 🆔 用户ID或设备ID: 约20-40字符")
    print("3. 📍 位置或IP信息: 约20-50字符")
    print("4. 🔧 版本或渠道信息: 约10-30字符")
    
    return None

def main():
    """主函数"""
    print("🚀 美团API完整请求头测试")
    print("按照夸克规范：使用准确请求头信息")
    print("=" * 60)
    
    # 测试完整请求头
    successful_body = test_with_provided_headers()
    
    if successful_body:
        print("\n" + "=" * 60)
        print("🎉 测试成功!")
        print("=" * 60)
        print(f"📋 成功请求体: {json.dumps(successful_body, ensure_ascii=False)}")
        
        # 保存成功格式
        with open("meituan_exact_body.json", "w", encoding="utf-8") as f:
            json.dump({
                "discovery_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "api_url": "https://zhaopin.meituan.com/api/official/job/getJobList",
                "successful_body": successful_body,
                "headers_used": "provided_by_user",
                "note": "使用完整请求头测试成功的参数格式"
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 成功格式已保存: meituan_exact_body.json")
        
        print("\n🎯 下一步:")
        print("1. 🔄 使用此格式更新爬取器")
        print("2. 🧪 进行单页测试验证")
        print("3. 📊 开始完整数据爬取")
        
        return successful_body
    else:
        print("\n" + "=" * 60)
        print("⚠️ 所有猜测格式测试失败")
        print("=" * 60)
        
        # 分析444字节长度
        analyze_content_length()
        
        print("\n🔧 按照夸克规范，需要:")
        print("1. 📋 获取准确的请求体内容")
        print("2. 🔍 查看浏览器中的Request Payload")
        print("3. 📝 复制完整的JSON参数")
        
        print("\n💡 请告诉我:")
        print("1. 完整的Request Payload（JSON格式）")
        print("2. 或截图显示参数内容")
        print("3. 或描述444字节的具体内容")
        
        return None

if __name__ == "__main__":
    result = main()
    
    if not result:
        print("\n" + "=" * 60)
        print("📋 需要准确参数信息")
        print("=" * 60)
        print("💡 请提供美团API的准确请求参数格式")
        print("🔍 在浏览器中查看: Network -> getJobList -> Request Payload")