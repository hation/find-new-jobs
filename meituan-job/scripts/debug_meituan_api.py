#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘API调试脚本
分析API请求参数格式
"""

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_different_formats():
    """测试不同的请求参数格式"""
    
    api_url = "https://zhaopin.meituan.com/api/official/job/getJobList"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://zhaopin.meituan.com",
        "Referer": "https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
        "Sec-Ch-Ua": '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Priority": "u=1, i"
    }
    
    # 测试不同的参数格式
    test_cases = [
        {
            "name": "格式1: 完整参数",
            "data": {
                "cityList": "001019002",
                "jfJgList": "11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001",
                "page": 1,
                "pageSize": 10,
                "sortField": "updateTime",
                "sortOrder": "desc"
            }
        },
        {
            "name": "格式2: 简化参数",
            "data": {
                "cityList": "001019002",
                "jfJgList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "page": 1,
                "pageSize": 10
            }
        },
        {
            "name": "格式3: 基础参数",
            "data": {
                "cityList": ["001019002"],
                "jfJgList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "page": 1,
                "pageSize": 10
            }
        },
        {
            "name": "格式4: 字符串数组",
            "data": {
                "cityList": "001019002",
                "jfJgList": ["11002_-1", "11003_-1", "11005_-1", "11007_-1", "11010_1101001"],
                "page": 1,
                "pageSize": 10
            }
        },
        {
            "name": "格式5: 观察网络请求",
            "data": {}  # 空数据，用于观察
        }
    ]
    
    print("🔍 测试美团API参数格式")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases):
        print(f"\n📋 测试用例 {i+1}: {test_case['name']}")
        
        if test_case['data']:
            print(f"📦 请求数据: {json.dumps(test_case['data'], ensure_ascii=False)}")
            
            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=test_case['data'],
                    timeout=10
                )
                
                print(f"📥 响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        print(f"📊 响应数据:")
                        print(f"  状态码: {result.get('code', '无')}")
                        print(f"  消息: {result.get('message', '无')}")
                        
                        if result.get('code') == 200:
                            data = result.get('data', {})
                            print(f"✅ API请求成功!")
                            print(f"  数据字段: {list(data.keys())}")
                            if 'list' in data:
                                print(f"  岗位数量: {len(data['list'])}")
                                if data['list']:
                                    first_job = data['list'][0]
                                    print(f"  示例岗位: {first_job.get('jobName', '未知')}")
                            return test_case['data']  # 返回成功的格式
                        else:
                            print(f"❌ API返回错误")
                    except:
                        print(f"📄 响应文本: {response.text[:200]}...")
                else:
                    print(f"❌ HTTP错误")
                    
            except Exception as e:
                print(f"💥 请求异常: {str(e)}")
        else:
            print("👀 请观察浏览器网络请求中的实际参数格式")
            print("💡 打开浏览器开发者工具 -> Network -> 查看请求Payload")
    
    return None


def analyze_network_request():
    """分析网络请求格式"""
    print("\n" + "=" * 60)
    print("📡 网络请求分析")
    print("=" * 60)
    
    print("根据你的请求头信息，分析:")
    print("1. ✅ API地址: https://zhaopin.meituan.com/api/official/job/getJobList")
    print("2. ✅ 请求方法: POST")
    print("3. ✅ Content-Type: application/json")
    print("4. ✅ Referer: 包含筛选参数")
    print("5. ❓ 请求参数格式: 需要确定")
    
    print("\n💡 建议:")
    print("1. 打开美团招聘网站")
    print("2. 按F12打开开发者工具")
    print("3. 切换到Network标签")
    print("4. 刷新页面或应用筛选")
    print("5. 找到getJobList请求")
    print("6. 查看Request Payload")
    
    print("\n🔍 可能的参数格式:")
    print("1. cityList: 字符串 '001019002' 或数组 ['001019002']")
    print("2. jfJgList: 字符串 '11002_-1,11003_-1,...' 或数组")
    print("3. page: 数字 1")
    print("4. pageSize: 数字 10")
    
    return None


def main():
    """主函数"""
    print("🚀 美团招聘API参数调试")
    print("按照夸克规范：先调试参数，再执行爬取")
    print("=" * 60)
    
    # 测试不同格式
    successful_format = test_different_formats()
    
    if successful_format:
        print("\n" + "=" * 60)
        print("🎉 找到成功的参数格式!")
        print("=" * 60)
        print(f"📋 成功格式: {json.dumps(successful_format, ensure_ascii=False)}")
        
        # 保存成功格式
        with open("successful_api_format.json", "w", encoding="utf-8") as f:
            json.dump(successful_format, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 成功格式已保存: successful_api_format.json")
        print("💡 现在可以更新爬取器使用这个格式")
    else:
        print("\n" + "=" * 60)
        print("⚠️ 所有格式测试失败")
        print("=" * 60)
        
        # 分析网络请求
        analyze_network_request()
        
        print("\n🔧 下一步:")
        print("1. 手动查看浏览器网络请求")
        print("2. 获取准确的请求参数格式")
        print("3. 更新爬取器参数")
        print("4. 重新测试")


if __name__ == "__main__":
    main()