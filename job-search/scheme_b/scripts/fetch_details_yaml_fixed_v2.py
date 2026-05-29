#!/usr/bin/env python3
"""
方案B - 智能获取详情脚本 (支持YAML格式)
修复boss命令输出YAML而不是JSON的问题
"""

import subprocess
import json
import os
import time
import sys
from pathlib import Path
import yaml  # 新增：支持YAML解析

def get_workspace_path():
    """获取工作空间路径"""
    # 1. 优先使用环境变量
    workspace = os.environ.get('SCHEME_B_WORKSPACE')
    if workspace and os.path.exists(workspace):
        print(f"💡 使用环境变量指定目录: {workspace}")
        return workspace
    
    # 2. 新的默认路径：技能目录下的output文件夹
    skill_output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'output'
    )
    if os.path.exists(skill_output_path):
        print(f"💡 使用技能输出目录: {skill_output_path}")
        return skill_output_path

    # 3. 旧的默认路径（向后兼容）
    old_default_path = os.path.expanduser("~/招聘数据/方案B_立即执行_20260515_010114")
    if os.path.exists(old_default_path):
        print(f"💡 使用旧默认目录: {old_default_path}")
        return old_default_path

    # 4. 当前目录
    current_dir = os.getcwd()
    if os.path.exists(os.path.join(current_dir, 'all_security_ids_final.txt')):
        print(f"💡 使用当前目录: {current_dir}")
        return current_dir

    print("❌ 找不到工作目录")
    print("💡 建议设置:")
    print("   1. 环境变量: export SCHEME_B_WORKSPACE=\"/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output\"")
    print("   2. 或确保技能output目录存在")
    sys.exit(1)

def parse_yaml_output(output):
    """解析YAML格式的输出"""
    try:
        # boss命令输出以"data:"开头，是YAML格式
        if output.startswith('data:'):
            # 解析YAML
            data = yaml.safe_load(output)
            
            # 转换为与之前JSON格式兼容的结构
            result = {
                "ok": True,
                "schema_version": "1",
                "data": data
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            # 如果不是YAML格式，尝试作为JSON解析
            return output
    except Exception as e:
        print(f"   ⚠️  YAML解析失败: {e}")
        # 返回原始输出
        return output

def main():
    print("🚀 方案B - 智能获取详情脚本 (支持YAML格式 v2.0)")
    print("=" * 60)
    print("💡 修复: 支持boss命令的YAML输出格式")
    print("💡 保守策略: 获取失败就停止，立即进入汇总")
    print("💡 停止条件: 连续失败2次或达到最大尝试次数")
    print("💡 目标: 最大化token利用，避免无效尝试")
    print("=" * 60)
    
    # 获取工作目录
    workspace = get_workspace_path()
    os.chdir(workspace)
    print(f"📁 工作目录: {workspace}")
    
    # 检查boss命令是否可用
    print(f"🔍 检查boss命令...")
    try:
        result = subprocess.run(['boss', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ boss命令可用: {result.stdout.strip()}")
        else:
            print(f"⚠️  boss命令返回非零状态: {result.stderr}")
    except FileNotFoundError:
        print("❌ boss命令未安装或不在PATH中")
        print("💡 请安装: pip install git+https://github.com/zouzhifeng/boss-cli.git")
        sys.exit(1)

    # 读取所有security_id
    print(f"\n📋 读取security_id...")
    security_ids = []
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 处理格式: security_id|职位名称|页码
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            security_ids.append(security_id)
                else:
                    # 如果没有|分隔符，直接使用
                    if len(line) > 100:
                        security_ids.append(line)

    print(f"   总security_id数: {len(security_ids)}")
    
    # 读取已获取记录
    fetched_file = 'fetched_security_ids.txt'
    fetched_ids = set()
    if os.path.exists(fetched_file):
        with open(fetched_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 与security_ids读取逻辑保持一致：处理|分隔符
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 1:
                        security_id = parts[0].strip()
                        if security_id and len(security_id) > 100:
                            fetched_ids.add(security_id)
                else:
                    # 如果没有|分隔符，直接使用（但需要验证长度）
                    if len(line) > 100:
                        fetched_ids.add(line)

        print(f"   已获取记录: {len(fetched_ids)} 个")
    else:
        print("   没有已获取记录文件,将创建新文件")

    # 找到未获取的
    unfetched = [sid for sid in security_ids if sid not in fetched_ids]
    print(f"   未获取的security_id: {len(unfetched)} 个")

    if not unfetched:
        print("🎉 所有security_id都已获取")
        return

    print(f"\n🚀 开始智能获取详情(支持YAML格式)...")
    print("=" * 60)
    print("💡 支持YAML格式: 修复boss命令输出问题")
    print("💡 token有效期:约3-5分钟，立即执行")
    print("💡 停止条件: 连续失败2次")
    print("=" * 60)

    max_attempts = 10  # 最大尝试次数
    success_count = 0
    fail_count = 0
    skipped_count = 0
    
    for i, security_id in enumerate(unfetched[:max_attempts]):
        print(f"\n📋 尝试获取第 {i+1} 个(总第 {781778904022 + i} 个)")
        print(f"   security_id: {security_id[:30]}...")
        
        # 跳过已知有问题的第一个security_id
        if security_id.startswith('157gfiaER1wka'):
            print(f"   ⚠️  跳过已知有问题的security_id")
            skipped_count += 1
            continue

        try:
            # 执行boss detail命令
            print(f"   执行命令: boss detail ...")
            result = subprocess.run(
                ['boss', 'detail', security_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"❌ 命令执行失败")
                print(f"   错误输出: {result.stderr[:100] if result.stderr else '空'}")
                fail_count += 1
                
                # 检查是否token过期
                if "token" in result.stderr.lower() or "登录" in result.stderr:
                    print(f"💡 可能token已过期，建议重新登录: boss login")
                    break
                    
                continue
            
            # 处理输出
            output = result.stdout
            
            # 尝试解析为YAML
            try:
                parsed_output = parse_yaml_output(output)
                
                # 保存详情文件
                detail_dir = "职位详情"
                os.makedirs(detail_dir, exist_ok=True)
                
                # 生成文件名
                timestamp = int(time.time() * 1000)
                filename = os.path.join(detail_dir, f"detail_{len(fetched_ids)+success_count+1}_{timestamp}.json")
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(parsed_output)
                
                print(f"   ✅ 保存到: {filename}")
                
                # 记录已获取
                with open(fetched_file, 'a', encoding='utf-8') as f:
                    f.write(f"{security_id}|YAML修复版获取\n")
                
                success_count += 1
                print(f"   💡 进度: 已尝试{i+1}次，成功{success_count}个，失败{fail_count}个")
                
                # 短暂等待，避免请求过快
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ 处理输出失败: {e}")
                print(f"   输出前100字符: {output[:100]}")
                fail_count += 1
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  命令超时")
            fail_count += 1
        except Exception as e:
            print(f"❌ 执行错误: {e}")
            fail_count += 1
        
        # 检查停止条件
        if fail_count >= 2:
            print(f"💡 连续失败{fail_count}次，可能token已过期，停止获取")
            break
        
        # 如果已达到目标（再获取7个），也可以停止
        if success_count >= 7:
            print(f"🎯 已达到目标（再获取7个），停止获取")
            break

    print(f"\n{'=' * 60}")
    print(f"📊 获取统计:")
    print(f"   尝试获取: {max_attempts} 个")
    print(f"   ✅ 成功: {success_count} 个")
    print(f"   ❌ 失败: {fail_count} 个")
    print(f"   ⚠️  跳过: {skipped_count} 个(已知问题)")
    
    if success_count > 0:
        print(f"\n✅ 成功获取{success_count}个新详情")
        print(f"🎯 当前总计: {len(fetched_ids)+success_count}/150 ({int((len(fetched_ids)+success_count)*100/150)}%)")
    else:
        print(f"\n⚠️  未获取到新详情，可能原因:")
        print(f"   1. token已过期 (需要重新登录)")
        print(f"   2. boss命令输出格式变化")
        print(f"   3. 网络连接问题")
    
    print(f"\n✅ 脚本执行完成")
    print(f"💡 下次使用: python3 fetch_details_yaml_fixed_v2.py")

if __name__ == "__main__":
    main()