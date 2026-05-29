#!/usr/bin/env python3
"""
重命名Excel文件工具
将长文件名改为固定格式：地点_搜索关键词.xlsx
例如：深圳_ai.xlsx
"""

import os
import glob
import shutil
import pandas as pd
from datetime import datetime

def main():
    print("📁 重命名Excel文件工具")
    print("=" * 60)
    
    # 设置工作目录
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 固定文件名格式
    fixed_name = "深圳_ai.xlsx"
    backup_dir = "backup_excel_files"
    
    print(f"📋 配置:")
    print(f"  工作目录: {workspace}")
    print(f"  固定文件名: {fixed_name}")
    print(f"  备份目录: {backup_dir}")
    
    # 1. 创建备份目录
    os.makedirs(backup_dir, exist_ok=True)
    
    # 2. 找到所有Excel文件
    excel_files = glob.glob('深圳AI岗位_*.xlsx')
    print(f"\n🔍 找到 {len(excel_files)} 个Excel文件:")
    
    for i, file in enumerate(excel_files, 1):
        size = os.path.getsize(file)
        mtime = datetime.fromtimestamp(os.path.getmtime(file))
        print(f"  {i:2d}. {os.path.basename(file)}")
        print(f"      大小: {size:,} 字节")
        print(f"      修改时间: {mtime}")
    
    if not excel_files:
        print("❌ 没有找到Excel文件")
        return
    
    # 3. 找到最新的文件
    latest_file = max(excel_files, key=os.path.getmtime)
    print(f"\n📊 最新文件: {os.path.basename(latest_file)}")
    
    # 4. 备份所有文件
    print(f"\n💾 备份原始文件...")
    backup_count = 0
    for file in excel_files:
        filename = os.path.basename(file)
        backup_path = os.path.join(backup_dir, filename)
        
        # 如果备份文件已存在，添加时间戳
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f"{os.path.splitext(filename)[0]}_{timestamp}.xlsx")
        
        shutil.copy2(file, backup_path)
        backup_count += 1
    
    print(f"✅ 备份完成: {backup_count} 个文件备份到 {backup_dir}/")
    
    # 5. 重命名最新文件为固定名称
    print(f"\n🔄 重命名最新文件...")
    
    # 先删除旧的固定文件名（如果存在）
    if os.path.exists(fixed_name):
        old_backup = os.path.join(backup_dir, f"old_{fixed_name}")
        shutil.move(fixed_name, old_backup)
        print(f"📁 移动旧文件: {fixed_name} -> {old_backup}")
    
    # 复制最新文件为固定名称
    shutil.copy2(latest_file, fixed_name)
    
    print(f"✅ 重命名完成:")
    print(f"  源文件: {os.path.basename(latest_file)}")
    print(f"  目标文件: {fixed_name}")
    
    # 6. 验证新文件
    print(f"\n🔍 验证新文件...")
    try:
        df = pd.read_excel(fixed_name)
        print(f"✅ 文件验证通过:")
        print(f"   行数: {len(df)}")
        print(f"   列数: {len(df.columns)}")
        
        if '数据完整性' in df.columns:
            complete = (df['数据完整性'] == '完整').sum()
            print(f"   完整数据: {complete} ({complete/len(df)*100:.1f}%)")
        
        # 检查数据一致性
        with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if len(df) == len(lines):
            print(f"✅ 数据一致性: Excel({len(df)}) = Security_id({len(lines)})")
        else:
            print(f"⚠️  数据不一致: Excel({len(df)}) ≠ Security_id({len(lines)})")
    
    except Exception as e:
        print(f"❌ 文件验证失败: {e}")
    
    # 7. 创建符号链接（可选）
    print(f"\n🔗 创建符号链接...")
    
    # 创建简单名称的符号链接
    simple_names = ["latest.xlsx", "深圳AI岗位最新.xlsx"]
    for link_name in simple_names:
        if os.path.exists(link_name):
            os.remove(link_name)
        
        # 创建相对路径的符号链接
        os.symlink(fixed_name, link_name)
        print(f"  创建链接: {link_name} -> {fixed_name}")
    
    # 8. 显示文件信息
    print(f"\n📊 最终文件结构:")
    print(f"  📁 {backup_dir}/ - 原始文件备份")
    print(f"  📄 {fixed_name} - 主文件（固定名称）")
    print(f"  🔗 latest.xlsx - 最新文件链接")
    print(f"  🔗 深圳AI岗位最新.xlsx - 中文名称链接")
    
    # 9. 清理建议
    print(f"\n🧹 清理建议（可选）:")
    print(f"  # 删除除备份外的所有旧文件")
    print(f"  rm 深圳AI岗位_*.xlsx")
    print(f"  # 保留符号链接和固定文件")
    print(f"  # 如果出错，可以从备份恢复:")
    print(f"  cp {backup_dir}/最新文件.xlsx 深圳_ai.xlsx")
    
    print(f"\n✅ 重命名工具执行完成!")
    print(f"💡 现在可以使用固定文件名: {fixed_name}")

if __name__ == "__main__":
    main()