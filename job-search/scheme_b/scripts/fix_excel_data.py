#!/usr/bin/env python3
"""
修复Excel数据工具
1. 删除空行
2. 确保数据一致性
3. 验证职位ID数量
"""

import pandas as pd
import os
import shutil
from datetime import datetime

def main():
    print("🔧 修复Excel数据工具")
    print("=" * 60)
    
    # 工作目录
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 固定文件名
    fixed_excel = "深圳_ai.xlsx"
    backup_dir = "backup_excel_files"
    
    print(f"📁 工作目录: {workspace}")
    print(f"📄 修复文件: {fixed_excel}")
    
    # 1. 备份当前文件
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"深圳_ai_before_fix_{timestamp}.xlsx")
    shutil.copy2(fixed_excel, backup_file)
    print(f"💾 备份文件: {backup_file}")
    
    # 2. 加载数据
    df = pd.read_excel(fixed_excel)
    print(f"📥 原始数据: {len(df)} 行, {len(df.columns)} 列")
    
    # 3. 修复步骤
    original_count = len(df)
    
    # 步骤1: 删除空职位ID的行
    print(f"\n🔍 步骤1: 删除空职位ID的行...")
    before = len(df)
    df = df[df['职位ID'].notna() & (df['职位ID'] != '')]
    after = len(df)
    print(f"   删除: {before - after} 行空职位ID")
    
    # 步骤2: 删除重复职位ID的行
    print(f"\n🔍 步骤2: 删除重复职位ID的行...")
    before = len(df)
    df = df.drop_duplicates(subset=['职位ID'], keep='first')
    after = len(df)
    print(f"   删除: {before - after} 行重复职位ID")
    
    # 步骤3: 验证数据完整性列
    print(f"\n🔍 步骤3: 验证数据完整性...")
    if '数据完整性' not in df.columns:
        print("❌ 没有数据完整性列")
        return
    
    # 统计
    complete_count = (df['数据完整性'] == '完整').sum()
    search_only_count = (df['数据完整性'] == '仅搜索').sum()
    other_count = len(df) - complete_count - search_only_count
    
    print(f"   完整数据: {complete_count} 行 ({complete_count/len(df)*100:.1f}%)")
    print(f"   仅搜索数据: {search_only_count} 行 ({search_only_count/len(df)*100:.1f}%)")
    if other_count > 0:
        print(f"   其他数据: {other_count} 行")
    
    # 4. 保存修复后的文件
    df.to_excel(fixed_excel, index=False)
    
    # 5. 验证数据一致性
    print(f"\n🔍 步骤4: 验证数据一致性...")
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        security_id_count = len(lines)
    
    print(f"   Excel职位数: {len(df)}")
    print(f"   Security_id数: {security_id_count}")
    
    if len(df) == security_id_count:
        print(f"✅ 数据一致性验证通过!")
    else:
        print(f"❌ 数据不一致!")
        print(f"💡 差异: {abs(len(df) - security_id_count)} 行")
        
        # 检查哪些职位ID不匹配
        excel_ids = set(df['职位ID'].dropna().astype(str))
        with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
            security_ids = set([line.strip().split('|')[0] for line in f if line.strip() and not line.startswith('#')])
        
        missing_in_excel = security_ids - excel_ids
        extra_in_excel = excel_ids - security_ids
        
        if missing_in_excel:
            print(f"💡 在Excel中缺失的security_id: {len(missing_in_excel)} 个")
            for sid in list(missing_in_excel)[:3]:
                print(f"   - {sid[:30]}...")
        
        if extra_in_excel:
            print(f"💡 在Excel中多余的职位ID: {len(extra_in_excel)} 个")
            for eid in list(extra_in_excel)[:3]:
                print(f"   - {eid[:30]}...")
    
    # 6. 输出修复结果
    print(f"\n📊 修复结果:")
    print(f"   原始行数: {original_count}")
    print(f"   修复后行数: {len(df)}")
    print(f"   删除行数: {original_count - len(df)}")
    print(f"   完整率: {complete_count/len(df)*100:.1f}%")
    print(f"   文件大小: {os.path.getsize(fixed_excel):,} 字节")
    
    print(f"\n✅ 修复完成!")
    print(f"💡 修复后文件: {fixed_excel}")
    print(f"💡 备份文件: {backup_file}")

if __name__ == "__main__":
    main()