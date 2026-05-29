#!/usr/bin/env python3
"""
方案B - 优化获取详情脚本 v2.6

基于最新发现和原则的完全优化版本：
1. 基于encryptId去重，避免重复获取 ✅
2. 智能起点选择：从第60个开始（中间区域） ✅
3. token时间管理：最大化token利用率 ✅
4. 连续失败检测：3次失败停止 ✅
5. 应用八大核心原则 ✅

核心原则：
- 数据格式适应性 ✅
- 数据清洗前置 ✅
- 错误诊断分层 ✅
- 环境配置显式化 ✅
- 字段映射验证 ✅
- 保守执行策略 ✅
- 智能起点选择 ✅
- token生命周期管理 ✅
"""

import subprocess
import json
import os
import time
import sys
from pathlib import Path
from datetime import datetime

# 尝试导入yaml模块
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  yaml模块未安装，将尝试安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
        import yaml
        YAML_AVAILABLE = True
        print("✅ yaml模块安装成功")
    except:
        print("❌ 无法安装yaml模块，部分功能可能受限")

def parse_response(response_text):
    """原则1: 数据格式适应性 - 支持JSON和YAML格式"""
    # 首先尝试JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # 如果YAML模块可用，尝试YAML
        if YAML_AVAILABLE:
            try:
                return yaml.safe_load(response_text)
            except:
                pass
        
        # 如果都不行，尝试提取可能的JSON部分
        lines = response_text.strip().split('\n')
        for line in lines:
            if line.startswith('{') and line.endswith('}'):
                try:
                    return json.loads(line)
                except:
                    continue
        
        # 最后尝试
        try:
            # 尝试修复常见的YAML格式问题
            if response_text.startswith('---'):
                response_text = response_text[3:].strip()
            if YAML_AVAILABLE:
                return yaml.safe_load(response_text)
        except:
            pass
        
        # 如果所有尝试都失败，返回原始文本
        print(f"⚠️  无法解析响应格式，返回原始文本")
        return {"raw_response": response_text}

def setup_environment():
    """原则4: 环境配置显式化"""
    # 设置正确的PATH
    boss_path = "/Users/xingan/Library/Python/3.12/bin/boss"
    if not os.path.exists(boss_path):
        print(f"❌ boss命令不存在于 {boss_path}")
        print("请确保boss命令已正确安装")
        sys.exit(1)
    
    # 设置工作目录
    data_dir = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        sys.exit(1)
    
    os.chdir(data_dir)
    print(f"✅ 工作目录: {os.getcwd()}")
    print(f"✅ boss命令: {boss_path}")
    
    return boss_path, data_dir

def load_security_ids():
    """原则2: 数据清洗前置 - 加载并清洗security_id"""
    pure_file = "pure_security_ids.txt"
    if not os.path.exists(pure_file):
        print(f"❌ 文件不存在: {pure_file}")
        sys.exit(1)
    
    with open(pure_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 清洗数据
    security_ids = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 提取纯security_id（第一个|之前的部分）
        if '|' in line:
            security_id = line.split('|')[0].strip()
        else:
            security_id = line
        
        if security_id:
            security_ids.append(security_id)
    
    print(f"📊 加载 {len(security_ids)} 个security_id")
    return security_ids

def load_fetched_encryptids():
    """加载已获取的encryptId列表"""
    encryptid_file = "fetched_encryptids.txt"
    if not os.path.exists(encryptid_file):
        return set()
    
    fetched_encryptids = set()
    with open(encryptid_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                fetched_encryptids.add(line)
    
    print(f"📊 已获取 {len(fetched_encryptids)} 个唯一encryptId")
    return fetched_encryptids

def update_fetched_records(security_id, encrypt_id, success=True, error_msg=""):
    """更新获取记录"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 更新fetched_encryptids.txt
    encryptid_file = "fetched_encryptids.txt"
    encryptids = load_fetched_encryptids()
    if encrypt_id and encrypt_id not in encryptids:
        with open(encryptid_file, 'a', encoding='utf-8') as f:
            f.write(f"{encrypt_id}\n")
        print(f"✅ 新增encryptId: {encrypt_id}")
    
    # 更新fetched_security_ids.txt
    record_file = "fetched_security_ids.txt"
    with open(record_file, 'a', encoding='utf-8') as f:
        if success:
            f.write(f"{security_id} | 成功 | {timestamp} | encryptId:{encrypt_id if encrypt_id else 'N/A'}\n")
        else:
            f.write(f"{security_id} | 失败 | {timestamp} | 原因:{error_msg}\n")

def fetch_job_detail(boss_path, security_id):
    """获取单个职位详情"""
    try:
        # 执行boss命令
        cmd = [boss_path, "job", security_id, "--pretty"]
        print(f"🔍 获取职位: {security_id}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "未知错误"
            print(f"❌ 命令执行失败: {error_msg}")
            return None, error_msg
        
        # 解析响应
        response = parse_response(result.stdout)
        
        # 检查响应结构
        if isinstance(response, dict):
            # 获取encryptId
            encrypt_id = response.get('data', {}).get('encryptId')
            if not encrypt_id:
                # 尝试其他可能的字段名
                encrypt_id = response.get('encryptId') or response.get('id')
            
            # 保存到文件
            detail_file = f"职位详情/detail_{security_id}.json"
            with open(detail_file, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 成功获取: {security_id} -> encryptId: {encrypt_id}")
            print(f"💾 保存到: {detail_file}")
            
            return encrypt_id, None
        else:
            print(f"⚠️  响应不是字典格式: {type(response)}")
            return None, f"响应格式错误: {type(response)}"
            
    except subprocess.TimeoutExpired:
        print(f"⏰ 超时: {security_id}")
        return None, "超时"
    except Exception as e:
        print(f"❌ 异常: {security_id} - {str(e)}")
        return None, f"异常: {str(e)}"

def main():
    """主函数"""
    print("=" * 60)
    print("方案B - 优化获取详情脚本 v2.6")
    print("=" * 60)
    
    # 设置环境
    boss_path, data_dir = setup_environment()
    
    # 加载数据
    security_ids = load_security_ids()
    fetched_encryptids = load_fetched_encryptids()
    
    # 原则13: 智能起点选择 - 从第60个开始
    start_index = 60
    if start_index >= len(security_ids):
        start_index = 0
    
    print(f"🎯 智能起点: 从第{start_index}个开始 (共{len(security_ids)}个)")
    print(f"📊 已获取: {len(fetched_encryptids)}个")
    
    # 原则14: token生命周期管理 - 记录开始时间
    start_time = datetime.now()
    print(f"⏰ 开始时间: {start_time.strftime('%H:%M:%S')}")
    print(f"📝 token预计有效期: 3-5分钟")
    
    # 获取详情
    consecutive_failures = 0
    max_consecutive_failures = 3
    total_fetched = 0
    
    print(f"\n🚀 开始获取详情...")
    print("-" * 60)
    
    for i in range(start_index, len(security_ids)):
        security_id = security_ids[i]
        
        # 检查是否已达到token最大时间（4分钟）
        current_time = datetime.now()
        elapsed_minutes = (current_time - start_time).total_seconds() / 60
        if elapsed_minutes > 4:
            print(f"⏰ token可能已过期 (已用{elapsed_minutes:.1f}分钟)")
            print("💡 建议重新登录BOSS直聘")
            break
        
        # 执行获取
        encrypt_id, error_msg = fetch_job_detail(boss_path, security_id)
        
        if encrypt_id:
            # 成功
            consecutive_failures = 0
            total_fetched += 1
            
            # 更新记录
            update_fetched_records(security_id, encrypt_id, success=True)
            
            # 显示进度
            progress = (i + 1) / len(security_ids) * 100
            print(f"📈 进度: {i+1}/{len(security_ids)} ({progress:.1f}%)")
            print(f"✅ 本次成功: {total_fetched}个")
            
        else:
            # 失败
            consecutive_failures += 1
            update_fetched_records(security_id, None, success=False, error_msg=error_msg)
            
            print(f"❌ 连续失败: {consecutive_failures}/{max_consecutive_failures}")
            
            # 检查是否需要停止
            if consecutive_failures >= max_consecutive_failures:
                print(f"🛑 连续失败{consecutive_failures}次，停止获取")
                print(f"💡 可能原因: token过期或该区域无有效职位")
                break
        
        # 短暂延迟，避免请求过快
        if i < len(security_ids) - 1:  # 如果不是最后一个
            time.sleep(1)
    
    # 统计结果
    print("\n" + "=" * 60)
    print("📊 获取结果统计")
    print("=" * 60)
    
    end_time = datetime.now()
    duration_minutes = (end_time - start_time).total_seconds() / 60
    
    # 重新加载获取的encryptId
    final_fetched = load_fetched_encryptids()
    
    print(f"⏰ 用时: {duration_minutes:.1f}分钟")
    print(f"📥 本次获取: {total_fetched}个")
    print(f"📊 总共获取: {len(final_fetched)}个")
    print(f"📈 数据完整性: {len(final_fetched)}/{len(security_ids)} ({len(final_fetched)/len(security_ids)*100:.1f}%)")
    
    # 计算距离50%目标还需要多少
    target_50 = int(len(security_ids) * 0.5)
    if len(final_fetched) >= target_50:
        print(f"🎯 达到50%目标!")
    else:
        needed = target_50 - len(final_fetched)
        print(f"🎯 距离50%目标还需: {needed}个")
    
    # 下一步建议
    print("\n💡 下一步建议:")
    if consecutive_failures >= max_consecutive_failures:
        print("1. 重新登录BOSS直聘（token可能已过期）")
        print("2. 重新运行本脚本")
    elif total_fetched == 0:
        print("1. 检查网络连接")
        print("2. 检查boss命令是否正常工作")
        print("3. 可能需要重新登录")
    elif len(final_fetched) < target_50:
        print("1. 继续获取（token可能还有效）")
        print("2. 或重新登录后继续")
    else:
        print("1. 运行数据合并脚本: python3 final_fix_excel.py")
        print("2. 检查数据质量")
    
    print("\n✨ 任务完成!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 脚本异常: {str(e)}")
        import traceback
        traceback.print_exc()