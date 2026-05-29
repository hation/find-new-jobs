#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anti_content参数生成器
基于分析结果尝试生成有效的anti_content参数
"""

import time
import random
import hashlib
import hmac
import base64
import json
import string
from datetime import datetime

class AntiContentGenerator:
    """anti_content参数生成器"""
    
    def __init__(self):
        """初始化"""
        self.version_prefix = "0aqW"
        
        # 可能的密钥（需要逆向工程确定）
        self.possible_secrets = [
            "pdd_recruit_2024",
            "careers_pdd_secret",
            "anti_content_key_2024",
            "pdd_global_hr_secret",
            "recruitment_api_key"
        ]
        
        # 字符集
        self.charset = string.ascii_letters + string.digits
    
    def generate_timestamp(self):
        """生成时间戳"""
        # 毫秒时间戳
        return int(time.time() * 1000)
    
    def generate_random_string(self, length=32):
        """生成随机字符串"""
        return ''.join(random.choices(self.charset, k=length))
    
    def generate_session_id(self):
        """生成会话ID"""
        return f"sess_{random.randint(100000, 999999)}"
    
    def generate_user_id(self):
        """生成用户ID"""
        return f"user_{random.randint(1000, 9999)}"
    
    def generate_request_id(self):
        """生成请求ID"""
        return random.randint(1000000, 9999999)
    
    def hypothesis_1_composite_token(self):
        """假设1: 复合令牌"""
        try:
            # 1. 时间戳
            timestamp = self.generate_timestamp()
            
            # 2. 随机数
            random_str = self.generate_random_string(32)
            
            # 3. 会话ID
            session_id = self.generate_session_id()
            
            # 4. 组合数据
            data = f"{timestamp}_{random_str}_{session_id}"
            
            # 5. 签名（使用HMAC-SHA256）
            secret = self.possible_secrets[0]
            signature = hmac.new(
                secret.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # 6. 最终令牌
            token = f"{self.version_prefix}{data}_{signature}"
            return token
        except Exception as e:
            return f"生成失败: {e}"
    
    def hypothesis_2_encrypted_state(self):
        """假设2: 加密状态"""
        try:
            # 1. 状态数据
            state = {
                "uid": self.generate_user_id(),
                "ts": int(time.time()),  # 秒级时间戳
                "page": "jobs",
                "rid": self.generate_request_id(),
                "ver": "1.0"
            }
            
            # 2. 转换为紧凑JSON
            state_json = json.dumps(state, separators=(',', ':'))
            
            # 3. Base64编码
            state_b64 = base64.b64encode(state_json.encode()).decode()
            
            # 4. 添加随机填充
            random_suffix = self.generate_random_string(16)
            
            # 5. 签名
            data_to_sign = f"{state_b64}_{random_suffix}"
            secret = self.possible_secrets[1]
            signature = hashlib.sha256(
                f"{data_to_sign}_{secret}".encode()
            ).hexdigest()[:32]  # 取前32字符
            
            # 6. 组合
            token = f"{self.version_prefix}{data_to_sign}_{signature}"
            return token
        except Exception as e:
            return f"生成失败: {e}"
    
    def hypothesis_3_request_signature(self):
        """假设3: 请求签名"""
        try:
            # 1. 请求参数
            params = {
                "page": 1,
                "pageSize": 10,
                "t": self.generate_timestamp(),  # 毫秒时间戳
                "r": self.generate_request_id(),
                "job": "",
                "name": "",
                "workLocationList": "[]"
            }
            
            # 2. 排序并拼接
            sorted_params = sorted(params.items())
            param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
            
            # 3. Base64编码
            params_b64 = base64.b64encode(param_str.encode()).decode()
            
            # 4. 添加随机数
            random_str = self.generate_random_string(24)
            
            # 5. HMAC签名
            secret = self.possible_secrets[2]
            data_to_sign = f"{params_b64}_{random_str}"
            signature = hmac.new(
                secret.encode(),
                data_to_sign.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # 6. 组合
            token = f"{self.version_prefix}{data_to_sign}_{signature}"
            return token
        except Exception as e:
            return f"生成失败: {e}"
    
    def hypothesis_4_server_token(self):
        """假设4: 服务器令牌"""
        try:
            # 1. 服务器标识
            server_id = "pdd_server_01"
            
            # 2. 令牌ID
            token_id = f"token_{random.randint(1000000000, 9999999999)}"
            
            # 3. 有效期（未来5分钟）
            expiry = int(time.time()) + 300  # 5分钟后
            
            # 4. 组合数据
            data = f"{server_id}_{token_id}_{expiry}"
            
            # 5. Base64编码
            data_b64 = base64.b64encode(data.encode()).decode()
            
            # 6. 添加版本和随机数
            random_prefix = self.generate_random_string(8)
            
            # 7. 签名
            secret = self.possible_secrets[3]
            signature_input = f"{random_prefix}_{data_b64}"
            signature = hmac.new(
                secret.encode(),
                signature_input.encode(),
                hashlib.sha256
            ).hexdigest()[:40]  # 取前40字符
            
            # 8. 组合
            token = f"{self.version_prefix}{random_prefix}_{data_b64}_{signature}"
            return token
        except Exception as e:
            return f"生成失败: {e}"
    
    def generate_based_on_pattern(self, example_token):
        """基于示例模式生成"""
        try:
            # 分析示例token
            if not example_token.startswith(self.version_prefix):
                return "示例token不以0aqW开头"
            
            # 提取示例的结构
            parts = example_token.split('_')
            if len(parts) < 3:
                return "示例token结构不清晰"
            
            # 创建类似结构
            new_parts = []
            
            # 第一部分：版本+随机
            new_parts.append(f"{self.version_prefix}{self.generate_random_string(5)}")
            
            # 中间部分：类似示例的长度和模式
            for i in range(1, len(parts) - 1):
                example_part = parts[i]
                # 创建类似长度的部分
                new_length = len(example_part)
                new_part = self.generate_random_string(new_length)
                new_parts.append(new_part)
            
            # 最后部分：签名
            secret = self.possible_secrets[4]
            data_to_sign = '_'.join(new_parts)
            signature = hashlib.sha256(
                f"{data_to_sign}_{secret}".encode()
            ).hexdigest()[:64]  # 取前64字符
            
            # 添加签名
            new_parts.append(signature)
            
            # 组合
            token = '_'.join(new_parts)
            return token
        except Exception as e:
            return f"模式生成失败: {e}"
    
    def test_all_hypotheses(self, example_token=None):
        """测试所有假设"""
        print("🔬 测试anti_content生成算法")
        print("="*70)
        
        hypotheses = [
            ("复合令牌", self.hypothesis_1_composite_token),
            ("加密状态", self.hypothesis_2_encrypted_state),
            ("请求签名", self.hypothesis_3_request_signature),
            ("服务器令牌", self.hypothesis_4_server_token)
        ]
        
        results = []
        
        for name, func in hypotheses:
            print(f"\n🔍 测试假设: {name}")
            
            start_time = time.time()
            token = func()
            elapsed = time.time() - start_time
            
            if token.startswith("生成失败"):
                print(f"   ❌ {token}")
                continue
            
            print(f"   ✅ 生成成功")
            print(f"   令牌: {token[:50]}...")
            print(f"   长度: {len(token)} 字符")
            print(f"   用时: {elapsed:.3f} 秒")
            
            # 检查模式
            if token.startswith(self.version_prefix):
                print(f"   ✅ 以{self.version_prefix}开头")
            
            if '_' in token:
                parts = token.split('_')
                print(f"   ✅ 包含{len(parts)}个部分")
            
            results.append((name, token, len(token)))
        
        # 如果提供了示例token，进行模式匹配
        if example_token:
            print(f"\n🔍 基于示例token生成:")
            pattern_token = self.generate_based_on_pattern(example_token)
            
            if not pattern_token.startswith("生成失败"):
                print(f"   ✅ 生成成功")
                print(f"   令牌: {pattern_token[:50]}...")
                print(f"   长度: {len(pattern_token)} 字符")
                
                # 比较相似度
                if len(pattern_token) == len(example_token):
                    print(f"   ✅ 长度匹配")
                
                results.append(("模式匹配", pattern_token, len(pattern_token)))
        
        return results
    
    def validate_with_api(self, token):
        """使用API验证token"""
        print(f"\n🧪 使用API验证token...")
        
        url = "https://careers.pddglobalhr.com/api/recruit/position/list"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "Origin": "https://careers.pddglobalhr.com",
            "Referer": "https://careers.pddglobalhr.com/jobs",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Cookie": "_nano_fp=Xpm8lpgJn0EjXqdaXo_eBA4AmspK5Wx4Oawm5ox~"
        }
        
        payload = {
            "job": "",
            "page": 1,
            "pageSize": 10,
            "name": "",
            "workLocationList": [],
            "anti_content": token
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            print(f"   API响应: 状态码 {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success", False):
                    print(f"   ✅ Token有效!")
                    positions = data.get("result", {}).get("list", [])
                    total = data.get("result", {}).get("total", 0)
                    print(f"      获取数据: {len(positions)} 条，总计 {total} 条")
                    return True
                else:
                    error_code = data.get("errorCode")
                    error_msg = data.get("errorMsg", "未知错误")
                    print(f"   ❌ API错误: {error_code} - {error_msg}")
                    return False
            else:
                print(f"   ❌ HTTP错误: {response.status_code}")
                if response.text:
                    print(f"      错误信息: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"   ❌ 验证失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 anti_content参数生成器")
    print("="*70)
    
    # 创建生成器
    generator = AntiContentGenerator()
    
    # 示例token（用于模式匹配）
    example_token = "0aqWfxUkM_VegaLQeEi6XnDAVD1OIVUYtueGzwqpFKt5IJyiknd5jfd5bHj4-fpySTqFxfYnKHyFolYimTqFbKkKOxSXE_eaG8sYvTQ8n0wYlGwqlYvaOYuyOUpvcCwJlYpxnd9aOGnYnVOKngZPS1fTFl5k7k-PEcsI7iRz7kQdItRIkL2VKkoeSfMEF-RueDjVMAWp7IQ9-29adiePvG2y40Wy0dWEsT2OD9VfYvNluFrOydCjlZuYiZnwuTmPNdE_yuZfYnrzugildFrEjT2QDnKTYAzJi0gwON92274ginp5YtZ7ZKyPV1qGEPtyHJq0sqYPV1dg5TqbjQA6gyuubOGogJ0tyYNgNcYdCnHLUIPzU-2sZkwLvM1QvEstvkkRE11IkSsBDzLqESLtxMJnurYRLUbr9P09g5AATFS21GCX"
    
    print(f"📋 示例token分析:")
    print(f"   长度: {len(example_token)} 字符")
    print(f"   开头: {example_token[:10]}")
    print(f"   结尾: {example_token[-10:]}")
    print(f"   下划线数量: {example_token.count('_')}")
    print(f"   连字符数量: {example_token.count('-')}")
    
    # 测试所有假设
    print(f"\n" + "="*70)
    results = generator.test_all_hypotheses(example_token)
    
    # 验证最佳候选
    print(f"\n" + "="*70)
    print("🧪 验证生成的token")
    print("="*70)
    
    if results:
        # 选择最像的token（长度最接近）
        best_candidate = None
        best_length_diff = float('inf')
        
        for name, token, length in results:
            length_diff = abs(length - len(example_token))
            if length_diff < best_length_diff:
                best_length_diff = length_diff
                best_candidate = (name, token, length)
        
        if best_candidate:
            name, token, length = best_candidate
            print(f"\n🎯 最佳候选: {name}")
            print(f"   令牌: {token[:50]}...")
            print(f"   长度: {length} 字符 (差异: {best_length_diff})")
            
            # 验证
            is_valid = generator.validate_with_api(token)
            
            if is_valid:
                print(f"\n✅ 成功! 找到了有效的anti_content生成算法!")
                print(f"   算法: {name}")
                print(f"   token: {token}")
                
                # 保存成功的结果
                import os
                output_dir = "output/successful_tokens"
                os.makedirs(output_dir, exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_file = os.path.join(output_dir, f"valid_token_{timestamp}.txt")
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    f.write(f"生成时间: {datetime.now().isoformat()}\n")
                    f.write(f"算法: {name}\n")
                    f.write(f"token: {token}\n")
                    f.write(f"长度: {len(token)} 字符\n")
                    f.write(f"验证状态: 有效\n")
                
                print(f"\n📁 结果已保存: {result_file}")
            else:
                print(f"\n❌ 生成的token无效")
                print(f"   需要进一步分析或调整算法")
        else:
            print("❌ 没有生成有效的候选token")
    else:
        print("❌ 所有假设都失败")
    
    print(f"\n" + "="*70)
    print("💡 下一步建议:")
    print("   1. 分析更多实际token样本")
    print("   2. 逆向工程JavaScript生成代码")
    print("   3. 尝试不同的签名算法和密钥")
    print("   4. 考虑使用浏览器自动化获取有效token")
    print("="*70)

if __name__ == "__main__":
    main()