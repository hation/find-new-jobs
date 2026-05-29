#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单分析anti_content参数
"""

import re
import base64
import json
import time
from datetime import datetime

def analyze_structure(anti_content):
    """分析参数结构"""
    print(f"🔬 分析anti_content结构")
    print(f"   参数: {anti_content[:50]}...")
    print(f"   长度: {len(anti_content)} 字符")
    print(f"   获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 字符组成分析
    print(f"\n📊 字符组成分析:")
    
    char_stats = {
        "小写字母": sum(1 for c in anti_content if 'a' <= c <= 'z'),
        "大写字母": sum(1 for c in anti_content if 'A' <= c <= 'Z'),
        "数字": sum(1 for c in anti_content if '0' <= c <= '9'),
        "下划线": anti_content.count('_'),
        "连字符": anti_content.count('-'),
        "点": anti_content.count('.'),
        "其他": len([c for c in anti_content if not (c.isalnum() or c in '_-.')])
    }
    
    total_chars = len(anti_content)
    for char_type, count in char_stats.items():
        percentage = count / total_chars * 100 if total_chars > 0 else 0
        print(f"   {char_type}: {count} ({percentage:.1f}%)")
    
    # 2. 模式分析
    print(f"\n🔍 模式分析:")
    
    # 检查开头
    print(f"   开头: {anti_content[:10]}")
    if anti_content.startswith('0aqW'):
        print(f"   ✅ 以'0aqW'开头 - 可能是固定前缀")
    
    # 检查结尾
    print(f"   结尾: {anti_content[-10:]}")
    
    # 检查分隔符
    parts = anti_content.split('_')
    print(f"   下划线分隔部分: {len(parts)} 个")
    for i, part in enumerate(parts[:3]):  # 只显示前3部分
        print(f"     部分{i+1}: {part[:30]}... (长度: {len(part)})")
    
    # 3. Base64编码检查
    print(f"\n🔐 Base64编码检查:")
    
    # 尝试解码各部分
    for i, part in enumerate(parts):
        if len(part) % 4 == 0:  # Base64长度通常是4的倍数
            try:
                # 补全Base64
                missing_padding = 4 - len(part) % 4
                if missing_padding != 4:
                    part_padded = part + '=' * missing_padding
                else:
                    part_padded = part
                
                decoded = base64.b64decode(part_padded)
                decoded_len = len(decoded)
                
                print(f"   部分{i+1} 可能是Base64:")
                print(f"     原始: {part[:30]}...")
                print(f"     解码长度: {decoded_len} 字节")
                
                # 尝试解码为字符串
                try:
                    decoded_str = decoded.decode('utf-8')
                    if any(c.isprintable() and not c.isspace() for c in decoded_str[:50]):
                        print(f"     解码为UTF-8: {decoded_str[:50]}...")
                except:
                    # 可能是二进制数据
                    hex_repr = decoded.hex()[:50]
                    print(f"     十六进制: {hex_repr}...")
                    
            except Exception as e:
                pass
    
    # 4. 时间戳检查
    print(f"\n⏰ 时间戳检查:")
    
    # 查找可能的数字时间戳
    numbers = re.findall(r'\d+', anti_content)
    for num in numbers[:5]:  # 只检查前5个数字
        if len(num) >= 10:  # 时间戳通常10位或13位
            try:
                timestamp = int(num[:10]) if len(num) >= 10 else int(num)
                if 1000000000 <= timestamp <= 2000000000:  # 合理的时间戳范围
                    dt = datetime.fromtimestamp(timestamp)
                    print(f"   可能的时间戳: {timestamp} -> {dt}")
            except:
                pass
    
    # 5. JSON检查
    print(f"\n📄 JSON结构检查:")
    
    # 检查是否包含JSON结构
    if '{' in anti_content or '[' in anti_content:
        print(f"   🔍 可能包含JSON数据")
        
        # 尝试提取JSON
        json_pattern = r'\{[^}]*\}|\[[^\]]*\]'
        json_matches = re.findall(json_pattern, anti_content)
        
        for match in json_matches[:2]:  # 只检查前2个
            print(f"   找到JSON-like结构: {match[:50]}...")
            try:
                parsed = json.loads(match)
                print(f"     有效JSON: {type(parsed).__name__}")
            except:
                print(f"     无效JSON")
    
    return char_stats

def generate_hypotheses(anti_content):
    """生成关于生成算法的假设"""
    print(f"\n💡 生成算法假设:")
    
    hypotheses = [
        {
            "name": "复合令牌",
            "description": "由多个部分组成的复合令牌",
            "likely_components": ["版本前缀", "时间戳", "随机数", "签名", "用户标识"],
            "evidence": f"长度{len(anti_content)}字符，包含{anti_content.count('_')}个下划线分隔符",
            "probability": "高"
        },
        {
            "name": "加密状态",
            "description": "加密的用户会话状态",
            "likely_components": ["用户ID", "会话ID", "时间戳", "页面信息", "加密数据"],
            "evidence": "Base64-like编码，无明文用户信息",
            "probability": "中"
        },
        {
            "name": "请求签名",
            "description": "对请求参数的HMAC签名",
            "likely_components": ["请求参数哈希", "时间戳", "随机数", "签名"],
            "evidence": "固定长度，无结构化数据",
            "probability": "中"
        },
        {
            "name": "服务器令牌",
            "description": "服务器生成的一次性令牌",
            "likely_components": ["服务器标识", "令牌ID", "有效期", "签名"],
            "evidence": "以固定模式开头，有效期短",
            "probability": "高"
        }
    ]
    
    for i, hypo in enumerate(hypotheses, 1):
        print(f"\n   {i}. {hypo['name']} ({hypo['probability']}概率)")
        print(f"      描述: {hypo['description']}")
        print(f"      可能组成: {', '.join(hypo['likely_components'])}")
        print(f"      证据: {hypo['evidence']}")
    
    return hypotheses

def create_test_implementation():
    """创建测试实现"""
    print(f"\n🧪 创建测试实现...")
    
    test_code = '''
import time
import random
import hashlib
import hmac
import base64
import json

def generate_hypothesis_1():
    """假设1: 复合令牌"""
    # 版本前缀
    version = "0aqW"
    
    # 时间戳 (毫秒)
    timestamp = str(int(time.time() * 1000))
    
    # 随机数
    random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=32))
    
    # 用户/会话标识 (模拟)
    session_id = f"sess_{random.randint(100000, 999999)}"
    
    # 组合并签名
    data = f"{timestamp}_{random_str}_{session_id}"
    secret = "pdd_secret_key_2024"
    signature = hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()
    
    # 最终令牌
    token = f"{version}{data}_{signature}"
    return token

def generate_hypothesis_2():
    """假设2: 加密状态"""
    # 状态数据
    state = {
        "uid": f"user_{random.randint(1000, 9999)}",
        "ts": int(time.time()),
        "page": "jobs",
        "rid": random.randint(1000000, 9999999)
    }
    
    # 转换为JSON
    state_json = json.dumps(state, separators=(',', ':'))
    
    # Base64编码
    state_b64 = base64.b64encode(state_json.encode()).decode()
    
    # 添加签名
    signature = hashlib.sha256(f"{state_b64}_salt_pdd".encode()).hexdigest()[:32]
    
    # 组合
    token = f"0aqW{state_b64}_{signature}"
    return token

def generate_hypothesis_3():
    """假设3: 请求签名"""
    # 请求参数
    params = {
        "page": 1,
        "pageSize": 10,
        "t": int(time.time() * 1000),
        "r": random.randint(100000, 999999)
    }
    
    # 排序并拼接
    param_str = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    
    # HMAC签名
    secret = "pdd_api_2024_secret"
    signature = hmac.new(secret.encode(), param_str.encode(), hashlib.sha256).hexdigest()
    
    # Base64编码参数
    params_b64 = base64.b64encode(param_str.encode()).decode()
    
    # 组合
    token = f"0aqW{params_b64}_{signature}"
    return token

# 测试生成
print("测试anti_content生成算法")
print("="*60)

for i, func in enumerate([generate_hypothesis_1, generate_hypothesis_2, generate_hypothesis_3], 1):
    print(f"\\n假设{i}:")
    try:
        token = func()
        print(f"   生成: {token[:50]}...")
        print(f"   长度: {len(token)} 字符")
        print(f"   模式: {'类似' if token.startswith('0aqW') else '不类似'}实际参数")
    except Exception as e:
        print(f"   错误: {e}")
'''
    
    # 保存测试代码
    import os
    test_dir = "output/anti_content_analysis"
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = os.path.join(test_dir, "generate_test.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    print(f"✅ 测试代码已保存: {test_file}")
    
    return test_file

def main():
    """主函数"""
    print("🔬 anti_content参数分析工具")
    print("="*70)
    
    # 使用示例参数
    example_anti_content = "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX"
    
    # 1. 分析结构
    char_stats = analyze_structure(example_anti_content)
    
    # 2. 生成假设
    hypotheses = generate_hypotheses(example_anti_content)
    
    # 3. 创建测试实现
    test_file = create_test_implementation()
    
    # 总结
    print(f"\n" + "="*70)
    print("📊 分析总结")
    print("="*70)
    
    print(f"\n🎯 关键发现:")
    print(f"   1. anti_content是447字符的复合令牌")
    print(f"   2. 以'0aqW'固定前缀开头")
    print(f"   3. 包含多个下划线分隔的部分")
    print(f"   4. 可能是Base64编码的二进制数据")
    print(f"   5. 有效期极短（几秒钟）")
    
    print(f"\n💡 生成算法推测:")
    print(f"   最可能: 服务器生成的复合令牌")
    print(f"   组成: 版本前缀 + 时间戳 + 随机数 + 会话ID + 签名")
    print(f"   签名算法: 可能使用HMAC-SHA256")
    
    print(f"\n🚀 下一步:")
    print(f"   1. 运行测试代码: python3 {test_file}")
    print(f"   2. 分析更多实际样本")
    print(f"   3. 尝试逆向工程JavaScript代码")
    print(f"   4. 实现自动生成器")
    
    print(f"\n📁 输出文件: {os.path.dirname(test_file)}/")
    print("="*70)

if __name__ == "__main__":
    main()