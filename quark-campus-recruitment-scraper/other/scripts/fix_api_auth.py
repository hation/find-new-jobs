#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复API认证：从浏览器获取真实的CSRF令牌和Cookie
"""

import sys
import os
import json
import time
import logging
from typing import Dict, Any, Optional

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_auth_from_browser() -> Dict[str, Any]:
    """
    从浏览器获取认证信息（CSRF令牌和Cookie）
    
    返回：
        {
            "csrf_token": "实际的CSRF令牌",
            "cookies": {"key": "value"},
            "headers": {"User-Agent": "...", "X-CSRF-Token": "..."}
        }
    """
    logger.info("🔧 从浏览器获取认证信息...")
    
    # 方法1：尝试通过JavaScript从页面获取
    js_code = """
    (function() {
        try {
            // 获取CSRF令牌（通常存储在meta标签中）
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            const csrfToken = csrfMeta ? csrfMeta.content : null;
            
            // 获取Cookie
            const cookies = document.cookie;
            
            // 获取当前URL
            const currentUrl = window.location.href;
            
            // 获取页面标题（用于验证）
            const pageTitle = document.title;
            
            // 检查是否在正确的页面
            const isQuarkPage = currentUrl.includes('talent.quark.cn');
            
            return {
                success: true,
                csrfToken: csrfToken,
                cookies: cookies,
                currentUrl: currentUrl,
                pageTitle: pageTitle,
                isQuarkPage: isQuarkPage,
                timestamp: new Date().toISOString()
            };
        } catch(e) {
            return {
                success: false,
                error: e.toString(),
                timestamp: new Date().toISOString()
            };
        }
    })();
    """
    
    # 保存JavaScript代码到临时文件
    temp_js = "/tmp/get_browser_auth.js"
    try:
        with open(temp_js, "w") as f:
            f.write(js_code)
        logger.info(f"✅ 已保存JavaScript代码到: {temp_js}")
    except Exception as e:
        logger.error(f"❌ 保存JavaScript代码失败: {e}")
        return {}
    
    # 方法2：检查浏览器控制台是否有CSRF令牌
    # 在真实的浏览器环境中，我们可以直接执行JavaScript
    
    # 由于OpenClaw环境限制，我们先返回一个简化的响应
    # 在实际环境中，这里应该与浏览器交互
    
    logger.info("⚠️  浏览器交互受限，使用模拟认证信息进行测试...")
    
    # 模拟认证信息（基于之前的测试）
    return {
        "csrf_token": "c6ea8927-62fd-42ab-9eab-d1f3da836dfc",
        "cookies": {
            "SESSION": "example_session_id",
            "XSRF-TOKEN": "b1d5f1971"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://talent.quark.cn",
            "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh",
            "X-Requested-With": "XMLHttpRequest"
        },
        "note": "这是模拟认证信息，实际使用需要从浏览器获取"
    }

def test_api_with_auth(auth_info: Dict[str, Any]) -> bool:
    """
    使用认证信息测试API
    
    参数：
        auth_info: 认证信息字典
        
    返回：
        是否成功
    """
    logger.info("🔧 使用认证信息测试API...")
    
    import requests
    
    api_url = "https://talent.quark.cn/position/search"
    
    # 准备请求参数
    headers = auth_info.get("headers", {})
    cookies = auth_info.get("cookies", {})
    csrf_token = auth_info.get("csrf_token", "")
    
    # 添加CSRF令牌到URL或头信息
    if csrf_token:
        # 方法1：添加到URL参数
        api_url_with_csrf = f"{api_url}?_csrf={csrf_token}"
        logger.info(f"📊 API URL with CSRF: {api_url_with_csrf[:100]}...")
        
        # 方法2：添加到头部
        headers["X-CSRF-Token"] = csrf_token
    
    # 请求参数（已验证的7个筛选类别）
    params = {
        "categories": "97,103,143,152,124,146,492",
        "pageIndex": 1,
        "pageSize": 10
    }
    
    try:
        logger.info(f"📊 发送API请求到: {api_url}")
        logger.info(f"📊 请求参数: {json.dumps(params, ensure_ascii=False)}")
        logger.info(f"📊 请求头: {json.dumps(headers, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        response = requests.post(
            api_url,
            headers=headers,
            cookies=cookies,
            json=params,
            timeout=30
        )
        
        logger.info(f"📊 响应状态码: {response.status_code}")
        logger.info(f"📊 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info(f"✅ API请求成功!")
                logger.info(f"📊 API响应状态码: {data.get('code', 'N/A')}")
                logger.info(f"📊 消息: {data.get('msg', 'N/A')}")
                
                if data.get("code") == 0:
                    positions = data.get("data", {}).get("list", [])
                    total = data.get("data", {}).get("total", 0)
                    logger.info(f"🎉 成功获取 {len(positions)} 个岗位，总计 {total} 个岗位")
                    
                    # 显示前几个岗位
                    for i, pos in enumerate(positions[:3]):
                        logger.info(f"  {i+1}. {pos.get('title', 'N/A')} - {pos.get('location', 'N/A')}")
                    
                    return True
                else:
                    logger.warning(f"⚠️  API业务错误: {data.get('msg', '未知错误')}")
                    
            except Exception as e:
                logger.error(f"❌ JSON解析失败: {e}")
                logger.info(f"📊 原始响应: {response.text[:500]}...")
                
        elif response.status_code == 403:
            logger.error("❌ 认证失败 (403 Forbidden)")
            logger.info("💡 建议：检查CSRF令牌和Cookie是否有效")
            
        elif response.status_code == 405:
            logger.error("❌ 方法不允许 (405 Method Not Allowed)")
            logger.info("💡 建议：尝试不同的请求方法或参数")
            
        else:
            logger.error(f"❌ 请求失败: {response.status_code}")
            logger.info(f"📊 响应内容: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        logger.error("❌ 请求超时")
    except requests.exceptions.ConnectionError:
        logger.error("❌ 连接错误")
    except Exception as e:
        logger.error(f"❌ 请求异常: {e}")
    
    return False

def test_different_auth_strategies():
    """
    测试不同的认证策略
    """
    logger.info("🧪 测试不同的认证策略...")
    
    strategies = [
        {
            "name": "策略1: 基本认证",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://talent.quark.cn",
                "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh"
            },
            "cookies": {},
            "csrf_token": ""
        },
        {
            "name": "策略2: 添加X-Requested-With",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://talent.quark.cn",
                "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh",
                "X-Requested-With": "XMLHttpRequest"
            },
            "cookies": {},
            "csrf_token": ""
        },
        {
            "name": "策略3: 模拟浏览器会话",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Content-Type": "application/json;charset=UTF-8",
                "Origin": "https://talent.quark.cn",
                "Referer": "https://talent.quark.cn/off-campus/position-list?lang=zh",
                "X-Requested-With": "XMLHttpRequest",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br"
            },
            "cookies": {
                "SESSION": "simulated_session",
                "XSRF-TOKEN": "simulated_token"
            },
            "csrf_token": "simulated_csrf_token"
        }
    ]
    
    results = []
    for strategy in strategies:
        logger.info(f"\n📋 测试策略: {strategy['name']}")
        success = test_api_with_auth(strategy)
        results.append((strategy['name'], success))
        
        # 短暂等待，避免请求过快
        time.sleep(2)
    
    return results

def main():
    """主函数"""
    print("🚀 修复API认证测试")
    print("=" * 60)
    
    # 步骤1：从浏览器获取认证信息
    print("\n1. 🔧 尝试从浏览器获取认证信息...")
    auth_info = get_auth_from_browser()
    
    if auth_info:
        print(f"✅ 获取到认证信息")
        print(f"   CSRF令牌: {auth_info.get('csrf_token', 'N/A')[:30]}...")
        print(f"   Cookies数量: {len(auth_info.get('cookies', {}))}")
        print(f"   请求头数量: {len(auth_info.get('headers', {}))}")
    else:
        print("❌ 未能获取认证信息")
    
    # 步骤2：使用获取的认证信息测试API
    print("\n2. 🧪 使用认证信息测试API...")
    if auth_info and auth_info.get("csrf_token"):
        success = test_api_with_auth(auth_info)
        if success:
            print("🎉 API认证修复成功!")
        else:
            print("⚠️  API认证仍然失败，尝试其他策略...")
    
    # 步骤3：测试不同的认证策略
    print("\n3. 🔄 测试不同的认证策略...")
    results = test_different_auth_strategies()
    
    # 步骤4：总结
    print("\n" + "=" * 60)
    print("📊 认证策略测试总结")
    print("=" * 60)
    
    for strategy_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{strategy_name}: {status}")
    
    print("\n💡 下一步建议:")
    
    # 分析结果
    success_count = sum(1 for _, success in results if success)
    if success_count > 0:
        print("1. ✅ 至少有一个认证策略成功，可以继续使用")
        print("2. 🔧 将成功的策略集成到API爬取器中")
        print("3. 🚀 继续使用API优先的爬取方案")
    else:
        print("1. ⚠️  所有认证策略都失败")
        print("2. 🔄 切换到浏览器模式作为备选方案")
        print("3. 📝 记录失败的教训，后续优化API认证")
    
    print("=" * 60)
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)