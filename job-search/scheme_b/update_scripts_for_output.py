#!/usr/bin/env python3
"""
批量更新技能脚本，使其默认使用技能目录下的output文件夹
"""

import os
import re
from pathlib import Path

def update_workspace_function(filepath):
    """更新单个脚本的get_workspace_path函数"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找get_workspace_path函数
    pattern = r'def get_workspace_path\(\):(.*?)(?=def \w+\(|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print(f"  ⚠️  未找到get_workspace_path函数: {filepath}")
        return False
    
    old_function = match.group(0)
    
    # 新的函数实现
    new_function = '''def get_workspace_path():
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
    print("   1. 环境变量: export SCHEME_B_WORKSPACE=\\"/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output\\"")
    print("   2. 或确保技能output目录存在")
    sys.exit(1)
'''
    
    # 替换函数
    new_content = content.replace(old_function, new_function)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print("🚀 批量更新技能脚本以使用output目录")
    print("=" * 60)
    
    scripts_dir = Path(__file__).parent / "scripts"
    scripts_to_update = [
        "fetch_details_conservative_v2.py",
        "fetch_details_conservative.py", 
        "fetch_details_smart_v2.py",
        "fetch_details_smart_skip.py",
        "fetch_details_yaml_fixed.py",
        "fetch_details_optimized_v2.py",
        "fetch_details_test.py",
        "fetch_details_simple.py",
        "complete_scheme_b_workflow.py",
        "scheme_b_auto_workflow.py",
        "scheme_b_excel_correct_merge_v2.py",
        "scheme_b_excel_merge_fixed.py",
        "scheme_b_excel_merge_simple.py",
        "scheme_b_excel_exporter.py",
        "fix_excel_data.py",
        "check_data_completeness.py"
    ]
    
    updated_count = 0
    for script_name in scripts_to_update:
        script_path = scripts_dir / script_name
        if script_path.exists():
            print(f"\n📝 更新: {script_name}")
            try:
                if update_workspace_function(script_path):
                    print(f"  ✅ 更新成功")
                    updated_count += 1
                else:
                    print(f"  ⚠️  跳过（无get_workspace_path函数）")
            except Exception as e:
                print(f"  ❌ 更新失败: {e}")
        else:
            print(f"\n⚠️  文件不存在: {script_name}")
    
    print(f"\n{'=' * 60}")
    print(f"📊 更新统计:")
    print(f"  • 尝试更新: {len(scripts_to_update)} 个脚本")
    print(f"  • 成功更新: {updated_count} 个脚本")
    
    # 创建环境配置脚本
    print(f"\n🔧 创建环境配置:")
    env_script = scripts_dir.parent / "setup_output_env.sh"
    env_content = '''#!/bin/bash
# 方案B输出目录环境配置

echo "🚀 配置方案B输出目录环境"
echo "=========================================="

# 设置工作目录到技能output目录
export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"

echo "📁 工作目录: $SCHEME_B_WORKSPACE"
echo ""

# 检查目录存在
if [ ! -d "$SCHEME_B_WORKSPACE" ]; then
    echo "❌ 工作目录不存在: $SCHEME_B_WORKSPACE"
    echo "💡 请先创建目录或运行迁移脚本"
    exit 1
fi

echo "✅ 环境配置完成"
echo ""
echo "💡 现在可以直接使用技能脚本:"
echo "  python3 scripts/fetch_details_conservative_v2.py"
echo "  python3 scripts/fetch_details_smart_v2.py"
echo "  python3 scripts/complete_scheme_b_workflow.py"
echo ""
echo "💡 所有输出将保存在: $SCHEME_B_WORKSPACE"
'''
    
    with open(env_script, 'w', encoding='utf-8') as f:
        f.write(env_content)
    os.chmod(env_script, 0o755)
    print(f"  ✅ 创建环境配置脚本: {env_script}")
    
    print(f"\n✅ 批量更新完成!")
    print(f"💡 现在技能脚本默认使用: {scripts_dir.parent / 'output'}")
    print(f"💡 使用命令: . {env_script}")

if __name__ == "__main__":
    main()