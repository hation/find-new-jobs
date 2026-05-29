#!/usr/bin/env python3
"""
将执行目录迁移到技能目录的output文件夹
只复制必要文件，保持结构清晰
"""

import os
import shutil
from pathlib import Path

def main():
    print("🚀 迁移执行目录到技能output文件夹")
    print("=" * 60)
    
    # 源目录和目标目录
    source_dir = Path("/Users/xingan/招聘数据/方案B_立即执行_20260515_010114")
    target_dir = Path("/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output")
    
    print(f"📁 源目录: {source_dir}")
    print(f"📁 目标目录: {target_dir}")
    
    # 确保目标目录存在
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # 定义需要复制的文件类型和目录
    essential_files = [
        # 核心数据文件
        "all_security_ids_final.txt",
        "fetched_security_ids.txt", 
        "fetched_encryptids.txt",
        "深圳_ai.xlsx",
        
        # 搜索数据文件
        "search_page1.json",
        "search_page2.json", 
        "search_page3.json",
        "search_page4.json",
        "search_page5.json",
        "search_page6.json",
        "search_page7.json",
        "search_page8.json",
        "search_page9.json",
        "search_page10.json",
        
        # 重要配置文件
        "data_quality_report.txt",
        "encryptid_based_records.txt",
    ]
    
    essential_dirs = [
        "职位详情",  # 详情文件目录
        "backup_excel_files",  # Excel备份目录
    ]
    
    # 复制核心文件
    print("\n📋 复制核心文件:")
    copied_files = 0
    for filename in essential_files:
        source_path = source_dir / filename
        if source_path.exists():
            target_path = target_dir / filename
            shutil.copy2(source_path, target_path)
            print(f"  ✅ {filename}")
            copied_files += 1
        else:
            print(f"  ⚠️  {filename} (不存在)")
    
    # 复制核心目录
    print("\n📁 复制核心目录:")
    copied_dirs = 0
    for dirname in essential_dirs:
        source_path = source_dir / dirname
        if source_path.exists() and source_path.is_dir():
            target_path = target_dir / dirname
            # 如果目标目录已存在，先删除
            if target_path.exists():
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
            print(f"  ✅ {dirname}/")
            copied_dirs += 1
        else:
            print(f"  ⚠️  {dirname}/ (不存在)")
    
    # 创建软链接到原目录（可选）
    print("\n🔗 创建执行环境:")
    
    # 创建说明文件
    readme_content = """# 方案B执行环境（迁移到技能目录）

## 📍 目录说明
- **源目录**: /Users/xingan/招聘数据/方案B_立即执行_20260515_010114
- **目标目录**: /Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output

## 📋 迁移内容
1. **核心数据文件**: all_security_ids_final.txt, fetched_security_ids.txt 等
2. **搜索结果**: search_page*.json 文件
3. **职位详情**: 职位详情/ 目录
4. **Excel文件**: 深圳_ai.xlsx 及备份

## 🚀 使用方法
1. 设置环境变量:
   ```bash
   export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"
   ```

2. 使用技能脚本:
   ```bash
   cd ~/.openclaw/workspace/skills/job-search/scheme_b
   python3 scripts/fetch_details_conservative_v2.py
   ```

## 📊 当前状态
- 总职位数: 150个
- 已获取详情: 68个 (45.3%)
- 未获取详情: 82个
- 目标: 达到75个 (50%)

## 🎯 下一步
继续获取详情直到达到50%完成率
"""
    
    readme_path = target_dir / "README_迁移说明.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"  ✅ README_迁移说明.md")
    
    # 创建环境配置脚本
    env_script = """#!/bin/bash
# 方案B执行环境配置脚本

echo "🚀 配置方案B执行环境"
echo "=========================================="

# 设置工作目录
export SCHEME_B_WORKSPACE="/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scheme_b/output"

echo "📁 工作目录: $SCHEME_B_WORKSPACE"
echo ""

# 检查目录存在
if [ ! -d "$SCHEME_B_WORKSPACE" ]; then
    echo "❌ 工作目录不存在: $SCHEME_B_WORKSPACE"
    echo "💡 请先运行迁移脚本"
    exit 1
fi

echo "✅ 环境配置完成"
echo ""
echo "💡 使用技能脚本:"
echo "  cd ~/.openclaw/workspace/skills/job-search/scheme_b"
echo "  python3 scripts/fetch_details_conservative_v2.py"
echo ""
echo "💡 或使用完整工作流:"
echo "  python3 scripts/complete_scheme_b_workflow.py"
"""
    
    env_path = target_dir / "setup_env.sh"
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_script)
    os.chmod(env_path, 0o755)
    print(f"  ✅ setup_env.sh")
    
    # 创建验证脚本
    verify_script = """#!/usr/bin/env python3
"""
    
    print(f"\n📊 迁移统计:")
    print(f"  • 复制文件: {copied_files} 个")
    print(f"  • 复制目录: {copied_dirs} 个")
    print(f"  • 总大小: {sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file()) / 1024:.1f} KB")
    
    print(f"\n✅ 迁移完成!")
    print(f"💡 新执行目录: {target_dir}")
    print(f"💡 使用命令: cd {target_dir.parent} && python3 scripts/fetch_details_conservative_v2.py")

if __name__ == "__main__":
    main()