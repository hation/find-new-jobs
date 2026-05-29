#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析anti_content生成算法
"""

import os
import re
import json
import time
import requests
from datetime import datetime

def fetch_page_source():
    """获取页面源代码"""
    print("🌐 获取拼多多招聘网站页面源代码...")
    
    url = "https://careers.pddglobalhr.com/jobs"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP错误: {response.status_code}")
            return None
        
        print(f"✅ 成功获取页面源代码")
        print(f"   页面大小: {len(response.text):,} 字符")
        
        return response.text
        
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None

def extract_javascript_files(source):
    """提取JavaScript文件"""
    print("\n🔍 提取JavaScript文件...")
    
    # 查找script标签
    script_pattern = r'<script[^>]*src="([^"]+)"[^>]*>'
    scripts = re.findall(script_pattern, source, re.IGNORECASE)
    
    # 查找内联script
    inline_pattern = r'<script[^>]*>([\s\S]*?)</script>'
    inline_scripts = re.findall(inline_pattern, source, re.IGNORECASE)
    
    print(f"   找到 {len(scripts)} 个外部脚本")
    print(f"   找到 {len(inline_scripts)} 个内联脚本")
    
    # 过滤出可能的anti_content相关脚本
    anti_keywords = ['anti', 'content', 'token', 'sign', 'encrypt', 'decrypt', 'crypto', 'security']
    
    relevant_scripts = []
    
    for script in scripts:
        if any(keyword in script.lower() for keyword in anti_keywords):
            relevant_scripts.append(script)
            print(f"   🔍 相关外部脚本: {script}")
    
    for i, inline in enumerate(inline_scripts[:5]):  # 只检查前5个
        if any(keyword in inline.lower() for keyword in anti_keywords):
            print(f"   🔍 相关内联脚本 #{i+1}: {len(inline)} 字符")
            
            # 提取关键代码片段
            lines = inline.split('\n')
            for j, line in enumerate(lines):
                if any(keyword in line.lower() for keyword in anti_keywords):
                    print(f"     行 {j+1}: {line.strip()[:100]}...")
    
    return scripts, inline_scripts

def analyze_anti_content_patterns(source):
    """分析anti_content模式"""
    print("\n🔬 分析anti_content模式...")
    
    # 查找可能的anti_content生成代码
    patterns = [
        # 变量定义
        r'anti[_\-]?content\s*[:=]\s*["\']?([^"\'\s;]+)["\']?',
        r'AntiContent\s*[:=]\s*["\']?([^"\'\s;]+)["\']?',
        r'antiContent\s*[:=]\s*["\']?([^"\'\s;]+)["\']?',
        
        # 函数调用
        r'(?:generate|create|get|make)Anti[_\-]?Content\s*\([^)]*\)',
        r'anti[_\-]?content\s*=\s*[^(]+\([^)]*\)',
        
        # 加密/签名函数
        r'(?:encrypt|sign|generate|create)[^(]*\([^)]*\)',
        r'function[^{]*anti[^{]*\{',
        
        # 请求头设置
        r'headers\[["\']Anti-Content["\']\]',
        r'Anti-Content["\']?\s*:\s*',
        
        # 常见加密库
        r'crypto-js|jsencrypt|forge|sjcl|bcrypt',
        r'MD5|SHA|AES|RSA|HMAC|Base64',
    ]
    
    findings = []
    
    for pattern in patterns:
        matches = re.findall(pattern, source, re.IGNORECASE)
        if matches:
            findings.append((pattern, matches))
            print(f"   🔍 找到模式: {pattern}")
            for match in matches[:3]:  # 只显示前3个匹配
                print(f"     匹配: {match[:100]}...")
    
    return findings

def extract_api_calls(source):
    """提取API调用信息"""
    print("\n📡 提取API调用信息...")
    
    # 查找fetch/AJAX调用
    fetch_patterns = [
        r'fetch\s*\([^)]*["\']/api/[^"\']*["\'][^)]*\)',
        r'\.ajax\s*\([^)]*["\']/api/[^"\']*["\'][^)]*\)',
        r'axios\s*\.(?:get|post|put|delete)\s*\([^)]*["\']/api/[^"\']*["\'][^)]*\)',
        r'XMLHttpRequest[^;]+open[^;]+["\']/api/[^"\']*["\']',
    ]
    
    api_calls = []
    
    for pattern in fetch_patterns:
        matches = re.findall(pattern, source, re.DOTALL)
        if matches:
            for match in matches:
                api_calls.append(match)
                print(f"   🔍 API调用: {match[:150]}...")
    
    return api_calls

def analyze_network_requests():
    """分析网络请求模式"""
    print("\n🌐 分析网络请求模式...")
    
    # 模拟浏览器请求获取更多信息
    url = "https://careers.pddglobalhr.com/jobs"
    
    session = requests.Session()
    
    # 设置请求头
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    try:
        # 获取初始页面
        print("   获取初始页面...")
        response = session.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # 查找可能的初始化脚本
            init_pattern = r'<script[^>]*>[\s\S]*?window\.(?:init|initialize|load|ready)[\s\S]*?</script>'
            init_scripts = re.findall(init_pattern, response.text, re.IGNORECASE)
            
            if init_scripts:
                print(f"   找到 {len(init_scripts)} 个初始化脚本")
            
            # 查找可能的配置数据
            config_pattern = r'window\.(?:config|CONFIG|settings|SETTINGS)\s*=\s*({[^;]+})'
            config_matches = re.findall(config_pattern, response.text)
            
            if config_matches:
                print(f"   找到配置数据")
                try:
                    config = json.loads(config_matches[0])
                    print(f"   配置键: {list(config.keys())}")
                except:
                    print(f"   配置数据: {config_matches[0][:200]}...")
        
        # 尝试获取JavaScript文件
        print("\n   尝试获取关键JS文件...")
        js_files = [
            "/static/js/",
            "/js/",
            "app.",
            "main.",
            "chunk.",
            "vendor.",
            "runtime."
        ]
        
        for js_pattern in js_files:
            js_pattern_re = f'src="([^"]*{re.escape(js_pattern)}[^"]*\.js)"'
            js_matches = re.findall(js_pattern_re, response.text, re.IGNORECASE)
            
            if js_matches:
                for js_file in js_matches[:2]:  # 只取前2个
                    if js_file.startswith("http"):
                        js_url = js_file
                    else:
                        js_url = f"https://careers.pddglobalhr.com{js_file if js_file.startswith('/') else '/' + js_file}"
                    
                    print(f"   获取JS文件: {js_url}")
                    
                    try:
                        js_response = session.get(js_url, headers=headers, timeout=30)
                        if js_response.status_code == 200:
                            js_content = js_response.text
                            
                            # 查找anti_content相关代码
                            if 'anti' in js_content.lower() or 'content' in js_content.lower():
                                print(f"      ✅ 可能包含anti_content相关代码")
                                
                                # 提取相关行
                                lines = js_content.split('\n')
                                for i, line in enumerate(lines):
                                    if 'anti' in line.lower():
                                        print(f"        行 {i+1}: {line.strip()[:100]}...")
                                        if i < len(lines) - 1:
                                            print(f"        行 {i+2}: {lines[i+1].strip()[:100]}...")
                                        break
                    except:
                        pass
        
        return True
        
    except Exception as e:
        print(f"❌ 网络分析失败: {e}")
        return False

def generate_hypothesis():
    """生成关于anti_content生成算法的假设"""
    print("\n💡 生成算法假设...")
    
    hypotheses = [
        {
            "name": "时间戳+随机数+签名",
            "description": "anti_content可能由时间戳、随机数和签名组成",
            "pattern": "timestamp + random + signature",
            "likely_components": ["时间戳", "随机数", "用户标识", "页面标识", "签名"],
            "generation_method": "可能是客户端生成，包含防重放机制"
        },
        {
            "name": "服务器返回的令牌",
            "description": "anti_content可能是服务器返回的一次性令牌",
            "pattern": "server-generated token",
            "likely_components": ["会话ID", "请求ID", "有效期", "签名"],
            "generation_method": "服务器生成，客户端在请求中携带"
        },
        {
            "name": "加密的用户状态",
            "description": "anti_content可能是加密的用户状态信息",
            "pattern": "encrypted user state",
            "likely_components": ["用户ID", "时间戳", "页面信息", "加密密钥"],
            "generation_method": "AES/RSA加密的用户状态数据"
        },
        {
            "name": "请求签名",
            "description": "anti_content可能是对请求参数的签名",
            "pattern": "request signature",
            "likely_components": ["请求参数", "时间戳", "密钥", "哈希算法"],
            "generation_method": "HMAC-SHA256等签名算法"
        }
    ]
    
    for i, hypothesis in enumerate(hypotheses, 1):
        print(f"\n   {i}. {hypothesis['name']}")
        print(f"      描述: {hypothesis['description']}")
        print(f"      可能组成: {', '.join(hypothesis['likely_components'])}")
        print(f"      生成方法: {hypothesis['generation_method']}")
    
    return hypotheses

def create_test_scripts():
    """创建测试脚本"""
    print("\n🧪 创建测试脚本...")
    
    test_dir = "output/anti_content_tests"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建基本测试脚本
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试anti_content生成假设
"""'''

import time
import random
import hashlib
import hmac
import base64
import json
from datetime import datetime

def hypothesis_1_timestamp_random():
    """假设1: 时间戳+随机数"""
    timestamp = int(time.time() * 1000)  # 毫秒时间戳
    random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    
    # 组合
    combined = f"{timestamp}_{random_str}"
    
    # 可能的签名
    secret = "pdd_secret_key"  # 假设的密钥
    signature = hmac.new(secret.encode(), combined.encode(), hashlib.sha256).hexdigest()
    
    anti_content = f"{combined}_{signature}"
    return anti_content

def hypothesis_2_encrypted_state():
    """假设2: 加密状态"""
    user_state = {
        "user_id": "anonymous",
        "timestamp": int(time.time()),
        "page": "jobs",
        "session_id": f"session_{random.randint(100000, 999999)}"
    }
    
    # 转换为JSON并Base64编码
    state_json = json.dumps(user_state, separators=(',', ':'))
    state_b64 = base64.b64encode(state_json.encode()).decode()
    
    # 添加简单签名
    signature = hashlib.md5(f"{state_b64}_pdd_salt".encode()).hexdigest()[:8]
    
    anti_content = f"{state_b64}_{signature}"
    return anti_content

def hypothesis_3_request_signature():
    """假设3: 请求签名"""
    request_params = {
        "job": "",
        "page": 1,
        "pageSize": 10,
        "name": "",
        "workLocationList": []
    }
    
    # 排序并拼接参数
    sorted_params = sorted(request_params.items())
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 添加时间戳
    timestamp = int(time.time())
    param_str_with_time = f"{param_str}&t={timestamp}"
    
    # 使用HMAC签名
    secret = "pdd_api_secret"
    signature = hmac.new(secret.encode(), param_str_with_time.encode(), hashlib.sha256).hexdigest()
    
    anti_content = f"{timestamp}_{signature}"
    return anti_content

def test_hypotheses():
    """测试所有假设"""
    print("测试anti_content生成假设")
    print("="*60)
    
    hypotheses = [
        ("时间戳+随机数", hypothesis_1_timestamp_random),
        ("加密状态", hypothesis_2_encrypted_state),
        ("请求签名", hypothesis_3_request_signature)
    ]
    
    for name, func in hypotheses:
        print(f"\\n🔍 测试假设: {name}")
        try:
            result = func()
            print(f"   生成结果: {result}")
            print(f"   长度: {len(result)} 字符")
            print(f"   模式: {result[:50]}...")
        except Exception as e:
            print(f"   ❌ 生成失败: {e}")
    
    print("\\n📋 与实际参数对比:")
    print("   实际参数示例: 0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyikn...")
    print("   实际长度: 400+ 字符")
    print("   实际模式: 以'0aqW'开头，包含下划线和连字符")

if __name__ == "__main__":
    test_hypotheses()
"""
    
    test_file = os.path.join(test_dir, "test_hypotheses.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"✅ 测试脚本已创建: {test_file}")
    
    # 创建逆向工程脚本
    reverse_script = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逆向工程anti_content参数
"""

import re
import base64
import json

def analyze_anti_content_structure(anti_content):
    """分析anti_content结构"""
    print(f"分析anti_content结构")
    print(f"参数: {anti_content[:50]}...")
    print(f"长度: {len(anti_content)} 字符")
    
    # 检查字符组成
    char_types = {
        "字母": sum(1 for c in anti_content if c.isalpha()),
        "数字": sum(1 for c in anti_content if c.isdigit()),
        "下划线": anti_content.count('_'),
        "连字符": anti_content.count('-'),
        "点": anti_content.count('.'),
        "其他": len(anti_content) - sum(1 for c in anti_content if c.isalnum() or c in '_-.')
    }
    
    print("\\n字符组成:")
    for char_type, count in char_types.items():
        percentage = count / len(anti_content) * 100
        print(f"   {char_type}: {count} ({percentage:.1f}%)")
    
    # 检查可能的编码
    print("\\n编码分析:")
    
    # Base64检查
    try:
        # 移除可能的签名部分
        parts = anti_content.split('_')
        for part in parts:
            if len(part) % 4 == 0:  # Base64长度通常是4的倍数
                try:
                    decoded = base64.b64decode(part + '=' * (4 - len(part) % 4))
                    if decoded:
                        print(f"   🔍 部分 '{part[:20]}...' 可能是Base64")
                        try:
                            decoded_str = decoded.decode('utf-8')
                            if any(c.isprintable() and not c.isspace() for c in decoded_str):
                                print(f"      解码后: {decoded_str[:100]}...")
                        except:
                            pass
                except:
                    pass
    except:
        pass
    
    # JSON检查
    if '{' in anti_content or '[' in anti_content:
        print("   🔍 可能包含JSON数据")
    
    # 时间戳检查
    import time
    current_timestamp = int(time.time())
    
    # 查找可能的数字时间戳
    numbers = re.findall(r'\\d+', anti_content)
    for num in numbers[:5]:  # 只检查前5个数字
        if len(num) >= 10:  # 时间戳通常10位或13位
            timestamp = int(num[:10]) if len(num) >= 10 else int(num)
            if 1000000000 <= timestamp <= 2000000000:  # 合理的时间戳范围
                from datetime import datetime
                dt = datetime.fromtimestamp(timestamp)
                print(f"   🔍 可能的时间戳: {timestamp} -> {dt}")
    
    return char_types

def reverse_engineer_example():
    """逆向工程示例参数"""
    example = "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX"
    
    print("逆向工程示例anti_content参数")
    print("="*60)
    
    analyze_anti_content_structure(example)
    
    print("\\n💡 观察结果:")
    print("   1. 以'0aqW'开头 - 可能是固定前缀或版本标识")
    print("   2. 包含大量下划线和连字符 - 可能是分隔符")
    print("   3. 长度447字符 - 可能是多个部分的组合")
    print("   4. 字母数字混合 - 可能是Base64编码的数据")
    print("   5. 没有明显的JSON结构 - 可能是二进制数据编码")

if __name__ == "__main__":
    reverse_engineer_example()
"""
    
    reverse_file = os.path.join(test_dir, "reverse_engineer.py")
    with open(reverse_file, 'w', encoding='utf-8') as f:
        f.write(reverse_script)
    
    print(f"✅ 逆向工程脚本已创建: {reverse_file}")
    
    return test_dir

def main():
    """主函数"""
    print("🔬 分析anti_content生成算法")
    print("="*70)
    
    # 1. 获取页面源代码
    source = fetch_page_source()
    if not source:
        print("❌ 无法获取页面源代码")
        return
    
    # 2. 提取JavaScript文件
    scripts, inline_scripts = extract_javascript_files(source)
    
    # 3. 分析anti_content模式
    findings = analyze_anti_content_patterns(source)
    
    # 4. 提取API调用
    api_calls = extract_api_calls(source)
    
    # 5. 分析网络请求
    analyze_network_requests()
    
    # 6. 生成算法假设
    hypotheses = generate_hypothesis()
    
    # 7. 创建测试脚本
    test_dir = create_test_scripts()
    
    # 总结报告
    print("\n" + "="*70)
    print("📊 分析完成报告")
    print("="*70)
    
    print(f"\n📋 分析结果:")
    print(f"   1. 页面源代码: {len(source):,} 字符")
    print(f"   2. JavaScript文件: {len(scripts)} 个外部, {len(inline_scripts)} 个内联")
    print(f"   3. anti_content模式: {len(findings)} 个发现")
    print(f"   4. API调用: {len(api_calls)} 个发现")
    print(f"   5. 算法假设: {len(hypotheses)} 个")
    
    print(f"\n📁 输出文件:")
    print(f"   测试脚本: {test_dir}/test_hypotheses.py")
    print(f"   逆向工程: {test_dir}/reverse_engineer.py")
    
    print(f"\n💡 关键发现:")
    print(f"   1. anti_content可能是客户端生成的防重放令牌")
    print(f"   2. 可能包含时间戳、随机数和签名")
    print(f"   3. 长度400+字符，可能是Base64编码的复合数据")
    print(f"   4. 以'0aqW'开头，可能是版本或类型标识")
    
    print(f"\n🚀 下一步建议:")
    print(f"   1. 运行测试脚本验证假设")
    print(f"   2. 分析更多实际参数样本")
    print(f"   3. 尝试逆向工程生成算法")
    print(f"   4. 实现自动生成anti_content")
    
    print("="*70)

if __name__ == "__main__":
    main()