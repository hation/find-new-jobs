#!/usr/bin/env python3
"""
一键解决方案：处理__zp_stoken__过期问题
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def run_cmd(cmd, description=None, capture_output=True):
    """运行命令并显示结果"""
    if description:
        print(f"🔧 {description}...")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            env={**os.environ, "PATH": "/Users/xingan/Library/Python/3.12/bin:" + os.environ.get("PATH", "")}
        )
        
        if description and not capture_output:
            print()  # 添加空行
        
        return result
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return subprocess.CompletedProcess(cmd, 1, "", str(e))

def check_status():
    """检查当前状态"""
    print("📊 检查当前状态")
    print("-" * 40)
    
    result = run_cmd(["boss", "status"], "检查登录状态", capture_output=True)
    
    if result.returncode == 0:
        print(result.stdout)
        
        # 尝试解析JSON获取详细信息
        try:
            for line in result.stdout.split('\n'):
                if line.strip().startswith('{'):
                    data = json.loads(line.strip())
                    if data.get("ok"):
                        status_data = data.get("data", {})
                        authenticated = status_data.get("authenticated", False)
                        message = status_data.get("message", "")
                        
                        if authenticated:
                            return True, "✅ 登录状态正常"
                        elif "__zp_stoken__" in message:
                            return False, "❌ __zp_stoken__已过期"
                        else:
                            return False, f"⚠️  其他问题: {message}"
        except:
            pass
        
        # 检查文本输出
        if "__zp_stoken__" in result.stdout:
            return False, "❌ __zp_stoken__已过期"
        elif "✅ 已登录" in result.stdout:
            return True, "✅ 登录状态正常"
        else:
            return False, "⚠️  状态不确定"
    
    return False, "❌ 状态检查失败"

def login_workflow():
    """登录工作流程"""
    print("🔐 登录工作流程")
    print("-" * 40)
    
    # 1. 登出
    result = run_cmd(["boss", "logout"], "清除旧登录状态", capture_output=False)
    
    # 2. 提示用户登录
    print("\n📱 请在浏览器中登录BOSS直聘")
    print("   1. 打开: https://www.zhipin.com")
    print("   2. 使用手机号或微信登录")
    print("   3. 登录成功后，按回车继续...")
    input()
    
    # 3. 提取浏览器cookie
    print("\n🔄 提取浏览器cookie...")
    result = run_cmd(["boss", "login", "--cookie-source", "chrome"], "提取浏览器cookie", capture_output=False)
    
    if result.returncode == 0:
        print("✅ 登录成功")
        return True
    else:
        print("❌ 登录失败")
        return False

def immediate_operations():
    """立即执行操作（在token有效期内）"""
    print("🚀 立即执行操作")
    print("-" * 40)
    
    operations = [
        (["boss", "search", "AI", "--city", "深圳", "--page", "1"], "搜索深圳AI岗位（第1页）"),
        (["boss", "search", "AI", "--city", "深圳", "--page", "2"], "搜索深圳AI岗位（第2页）"),
    ]
    
    all_results = []
    
    for i, (cmd, desc) in enumerate(operations, 1):
        print(f"\n{i}. {desc}")
        result = run_cmd(cmd, None, capture_output=True)
        
        if result.returncode == 0:
            print("✅ 成功")
            
            # 尝试提取JSON数据
            try:
                for line in result.stdout.split('\n'):
                    if line.strip().startswith('{'):
                        data = json.loads(line.strip())
                        if data.get("ok"):
                            all_results.append(data)
                            break
            except:
                print("⚠️  无法解析JSON数据")
        else:
            print("❌ 失败")
            
            # 检查是否__zp_stoken__过期
            if "__zp_stoken__" in (result.stdout + result.stderr):
                print("💡 提示: __zp_stoken__可能已过期，请重新登录")
                return False, all_results
            
            # 短暂延迟
            time.sleep(1)
    
    return True, all_results

def save_results(results, base_dir=None):
    """保存结果到文件"""
    if not results:
        return
    
    if base_dir is None:
        base_dir = Path.home() / "招聘数据" / time.strftime("%Y%m%d_%H%M%S")
    
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 保存数据到: {base_dir}")
    
    # 保存搜索数据
    for i, data in enumerate(results, 1):
        file_path = base_dir / f"search_page_{i}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  📄 {file_path.name}")
    
    # 尝试获取职位详情
    if results and len(results) > 0:
        first_result = results[0]
        job_list = first_result.get("data", {}).get("jobList", [])
        
        if job_list:
            print("\n📋 获取职位详情...")
            details_dir = base_dir / "job_details"
            details_dir.mkdir(exist_ok=True)
            
            # 获取前3个职位详情
            for i in range(min(3, len(job_list))):
                job_idx = i + 1
                print(f"  获取职位 #{job_idx}...")
                
                result = run_cmd(["boss", "show", str(job_idx)], None, capture_output=True)
                
                if result.returncode == 0:
                    detail_file = details_dir / f"job_{job_idx}_detail.txt"
                    with open(detail_file, 'w', encoding='utf-8') as f:
                        f.write(result.stdout)
    
    return base_dir

def create_quick_script(output_dir):
    """创建快速执行脚本"""
    script_content = f'''#!/bin/bash
echo "🚀 快速执行脚本 - 基于 {time.strftime('%Y-%m-%d %H:%M:%S')} 的数据"
echo "=========================================="

# 设置路径
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

DATA_DIR="{output_dir}"

echo "📁 数据目录: $DATA_DIR"
echo ""

# 统计职位数量
echo "📊 数据统计:"
for json_file in "$DATA_DIR"/search_page_*.json; do
    if [ -f "$json_file" ]; then
        count=$(python3 -c "
import json
try:
    with open('$json_file', 'r', encoding='utf-8') as f:
        data = json.load(f)
    jobs = data.get('data', {{}}).get('jobList', [])
    print(len(jobs))
except:
    print(0)
" 2>/dev/null)
        echo "  $(basename $json_file): $count 个职位"
    fi
done

echo ""
echo "📋 可用命令:"
echo "  # 查看原始数据"
echo "  cat $DATA_DIR/search_page_1.json | jq '.'"
echo ""
echo "  # 提取职位名称和薪资"
echo "  cat $DATA_DIR/search_page_1.json | jq -r '.data.jobList[] | \"\\(.jobName) - \\(.salaryDesc)\"'"
echo ""
echo "  # 查看职位详情"
echo "  cat $DATA_DIR/job_details/job_1_detail.txt"
echo ""
echo "🔧 重新搜索:"
echo "  boss logout"
echo "  # 1. 浏览器登录 https://www.zhipin.com"
echo "  # 2. 执行: boss login --cookie-source chrome"
echo "  # 3. 立即执行: boss search AI --city 深圳 --page 1"
'''

    script_path = output_dir / "quick_summary.sh"
    script_path.write_text(script_content, encoding="utf-8")
    script_path.chmod(0o755)
    
    return script_path

def main():
    """主函数"""
    print("🎯 BOSS直聘 __zp_stoken__ 一键解决方案")
    print("=" * 60)
    
    # 检查状态
    status_ok, status_msg = check_status()
    print(f"\n状态: {status_msg}")
    
    if not status_ok or "__zp_stoken__" in status_msg:
        print("\n" + "=" * 60)
        print("🔧 需要执行登录流程")
        
        # 执行登录
        if not login_workflow():
            print("\n❌ 登录失败，请手动处理")
            return 1
    else:
        print("\n✅ 状态正常，可以直接执行操作")
    
    # 立即执行操作
    print("\n" + "=" * 60)
    success, results = immediate_operations()
    
    if not success:
        print("\n❌ 操作执行失败")
        return 1
    
    # 保存结果
    if results:
        output_dir = save_results(results)
        
        # 创建快速脚本
        script_path = create_quick_script(output_dir)
        
        print("\n" + "=" * 60)
        print("🎉 完成！")
        print(f"\n📁 数据目录: {output_dir}")
        print(f"📝 总结脚本: {script_path}")
        print(f"\n💡 下次可以直接运行: sh {script_path}")
    else:
        print("\n⚠️  未获取到数据")
    
    print("\n📋 最佳实践总结:")
    print("1. ✅ 登录后立即执行所有需要登录的操作")
    print("2. ✅ 使用 --json 参数保存结构化数据")
    print("3. ✅ 批量处理减少API调用")
    print("4. ✅ 及时导出数据避免丢失")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())