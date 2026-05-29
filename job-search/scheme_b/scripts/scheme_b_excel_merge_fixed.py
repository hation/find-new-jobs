#!/usr/bin/env python3
"""
方案B Excel合并修复版
修复数据覆盖问题：详情数据不覆盖搜索数据的关键字段
"""

import pandas as pd
import json
import os
import glob
import shutil
from datetime import datetime

def main():
    print("🚀 方案B Excel合并修复版")
    print("=" * 60)
    print("💡 修复: 详情数据不覆盖搜索数据的关键字段")
    print("💡 规则: 详情数据优先更新，但保留搜索数据的技能要求、福利待遇等")
    print("=" * 60)
    
    # 工作目录
    workspace = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(workspace)
    
    # 固定文件名
    fixed_excel = "深圳_ai.xlsx"
    backup_dir = "backup_excel_files"
    
    print(f"📁 工作目录: {workspace}")
    print(f"📄 修复文件: {fixed_excel}")
    print(f"📁 备份目录: {backup_dir}")
    
    # 1. 检查主文件是否存在
    if not os.path.exists(fixed_excel):
        print(f"❌ 找不到主文件: {fixed_excel}")
        return
    
    # 2. 备份当前文件
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f"深圳_ai_before_fix_{timestamp}.xlsx")
    shutil.copy2(fixed_excel, backup_file)
    print(f"💾 备份文件: {backup_file}")
    
    # 3. 加载现有数据
    df_existing = pd.read_excel(fixed_excel)
    print(f"📥 加载现有数据: {len(df_existing)} 行, {len(df_existing.columns)} 列")
    
    # 4. 查找详情文件
    detail_dir = "职位详情"
    if not os.path.exists(detail_dir):
        print(f"❌ 找不到详情目录: {detail_dir}")
        return
    
    detail_files = glob.glob(os.path.join(detail_dir, "detail_*.json"))
    print(f"🔍 找到 {len(detail_files)} 个详情文件")
    
    if not detail_files:
        print("❌ 没有详情文件")
        return
    
    # 5. 提取详情数据
    detail_data = []
    for file in detail_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取关键信息 - 修复JSON结构
            if 'data' in data and data['data']:
                job_data = data['data']
                
                # 职位信息可能在jobInfo中
                job_info = job_data.get('jobInfo', {})
                boss_info = job_data.get('bossInfo', {})
                brand_info = job_data.get('brandComInfo', {})
                
                detail_row = {
                    '职位ID': job_info.get('encryptId', ''),
                    '职位名称': job_info.get('jobName', ''),
                    '薪资范围': job_info.get('salaryDesc', ''),
                    '公司名称': brand_info.get('brandName', ''),
                    '经验要求': job_info.get('experienceName', ''),
                    '学历要求': job_info.get('degreeName', ''),
                    '职位描述': job_info.get('jobDescription', ''),
                    '公司介绍': brand_info.get('brandIntroduction', ''),
                    '公司规模': brand_info.get('brandScaleName', ''),
                    '公司行业': brand_info.get('brandIndustryName', ''),
                    '地址': job_info.get('address', ''),
                    '联系人': boss_info.get('name', ''),
                    '联系电话': '',  # 通常不提供
                    '数据完整性': '完整'
                }
                
                # 只添加有职位ID的数据
                if detail_row['职位ID']:
                    detail_data.append(detail_row)
                    print(f'✅ 提取: {detail_row["职位名称"]} (ID: {detail_row["职位ID"][:20]}...)')
        except Exception as e:
            print(f"⚠️  读取详情文件失败 {file}: {e}")
    
    if not detail_data:
        print("❌ 没有提取到详情数据")
        return
    
    df_details = pd.DataFrame(detail_data)
    print(f"📊 从详情文件提取了 {len(df_details)} 个职位信息")
    
    # 6. 定义字段分类
    print(f"\n🔧 字段分类策略:")
    detail_only_fields = ['职位描述', '公司介绍', '地址', '联系人', '联系电话']
    search_only_fields = ['技能要求', '福利待遇', '职位亮点', '职位标签']
    both_fields = ['职位名称', '薪资范围', '公司名称', '经验要求', '学历要求', '公司规模', '公司行业']
    
    print(f"   详情数据字段: {', '.join(detail_only_fields)}")
    print(f"   搜索数据字段: {', '.join(search_only_fields)}")
    print(f"   两者都有的字段: {', '.join(both_fields)}")
    
    # 7. 智能合并数据
    updated_count = 0
    new_count = 0
    
    for idx, detail_row in df_details.iterrows():
        job_id = detail_row['职位ID']
        
        # 查找现有数据中是否有这个职位ID
        if job_id in df_existing['职位ID'].values:
            # 更新现有行 - 智能合并
            row_idx = df_existing[df_existing['职位ID'] == job_id].index[0]
            
            # 1. 更新详情数据特有的字段（即使为空也要更新）
            for col in detail_only_fields:
                if col in df_existing.columns and col in detail_row:
                    existing_value = df_existing.at[row_idx, col]
                    new_value = detail_row[col]
                    
                    # 如果详情数据有值，或者现有值为空，就更新
                    if (pd.notna(new_value) and str(new_value).strip()) or pd.isna(existing_value):
                        df_existing.at[row_idx, col] = new_value
            
            # 2. 更新两者都有的字段（详情数据优先）
            for col in both_fields:
                if col in df_existing.columns and col in detail_row:
                    new_value = detail_row[col]
                    if pd.notna(new_value) and str(new_value).strip():
                        df_existing.at[row_idx, col] = new_value
            
            # 3. 保留搜索数据特有的字段（不覆盖）
            # 技能要求、福利待遇、职位亮点、职位标签保持不变
            
            updated_count += 1
            print(f'🔄 智能更新: {detail_row["职位名称"]}')
            
        else:
            # 添加新行（这种情况不应该发生，因为所有职位ID应该都在搜索数据中）
            new_row = detail_row.to_dict()
            for col in df_existing.columns:
                if col not in new_row:
                    new_row[col] = ''
            
            new_df = pd.DataFrame([new_row])
            new_df = new_df[df_existing.columns]
            df_existing = pd.concat([df_existing, new_df], ignore_index=True)
            new_count += 1
            print(f'🆕 新增: {detail_row["职位名称"]}')
    
    # 8. 保存到固定文件名
    df_existing.to_excel(fixed_excel, index=False)
    
    # 9. 输出统计
    print(f"\n📈 合并结果:")
    print(f"   总记录数: {len(df_existing)} 行")
    print(f"   智能更新的职位: {updated_count} 个")
    print(f"   新增的职位: {new_count} 个")
    
    if '数据完整性' in df_existing.columns:
        complete_count = (df_existing['数据完整性'] == '完整').sum()
        print(f"   完整数据: {complete_count} 行 ({complete_count/len(df_existing)*100:.1f}%)")
    
    print(f"\n💾 保存到: {fixed_excel}")
    print(f"📊 文件大小: {os.path.getsize(fixed_excel):,} 字节")
    
    # 10. 验证关键字段
    print(f"\n🔍 关键字段验证:")
    for field in detail_only_fields + search_only_fields:
        if field in df_existing.columns:
            non_empty = df_existing[field].notna().sum()
            print(f"   {field}: {non_empty}/{len(df_existing)} 非空 ({non_empty/len(df_existing)*100:.1f}%)")
    
    # 11. 验证数据一致性
    print(f"\n🔍 数据一致性检查:")
    with open('all_security_ids_final.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        print(f"   Security_id数: {len(lines)}")
    
    if len(df_existing) == len(lines):
        print(f"✅ 数据一致性: Excel({len(df_existing)}) = Security_id({len(lines)})")
    else:
        print(f"❌ 数据不一致: Excel({len(df_existing)}) ≠ Security_id({len(lines)})")
    
    print(f"\n✅ 修复合并完成！")
    print(f"💡 修复内容: 详情数据不再覆盖搜索数据的技能要求、福利待遇等字段")
    print(f"💡 备份文件: {backup_file}")
    print(f"💡 验证方法: 检查最新获取的职位是否保留了技能要求等字段")

if __name__ == "__main__":
    main()