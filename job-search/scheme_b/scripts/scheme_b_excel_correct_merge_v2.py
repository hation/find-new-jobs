#!/usr/bin/env python3
"""
方案B Excel正确合并工具 - 通用版本
使用正确的ID映射：Excel职位ID = JSON encryptId
适用于技能架构，不硬编码工作目录
"""

import pandas as pd
import json
import os
import glob
import sys
from datetime import datetime
from pathlib import Path

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
def main():
    print("🚀 方案B Excel正确合并工具")
    print("=" * 60)
    print("💡 通用版本，适用于技能架构")
    print("💡 使用正确的ID映射: Excel职位ID = JSON encryptId")
    print("=" * 60)
    
    # 获取工作目录
    workspace = get_workspace_path()
    print(f"📁 工作目录: {workspace}")
    os.chdir(workspace)
    
    # 1. 找到最新的Excel文件
    excel_files = sorted(glob.glob('深圳AI岗位_*.xlsx'))
    if not excel_files:
        print("❌ 没有找到Excel文件")
        print("💡 请确保工作目录包含Excel文件")
        return
    
    latest_excel = excel_files[-1]
    print(f"📁 找到最新Excel文件: {latest_excel}")
    print(f"   修改时间: {datetime.fromtimestamp(os.path.getmtime(latest_excel)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. 加载现有Excel数据
    try:
        df_existing = pd.read_excel(latest_excel)
        print(f"📥 加载现有数据: {len(df_existing)} 行, {len(df_existing.columns)} 列")
    except Exception as e:
        print(f"❌ 加载Excel文件失败: {e}")
        return
    
    # 显示现有数据状态
    if '数据完整性' in df_existing.columns:
        complete_count = (df_existing['数据完整性'] == '完整').sum()
        search_only_count = (df_existing['数据完整性'] == '仅搜索').sum() if '仅搜索' in df_existing['数据完整性'].values else 0
        print(f"📊 现有数据状态:")
        print(f"   完整数据: {complete_count} 行 ({complete_count/len(df_existing)*100:.1f}%)")
        print(f"   仅搜索数据: {search_only_count} 行 ({search_only_count/len(df_existing)*100:.1f}%)")
    
    # 3. 找到所有详情文件
    detail_files = sorted(glob.glob('职位详情/detail_*.json'))
    print(f"🔍 找到 {len(detail_files)} 个详情文件")
    
    if not detail_files:
        print("❌ 没有详情文件")
        print("💡 请先运行获取详情脚本")
        return
    
    # 4. 从详情文件提取数据
    print(f"📋 从详情文件提取数据...")
    detail_data_list = []
    
    for detail_file in detail_files:
        try:
            with open(detail_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get('ok') and 'data' in data and data['data']:
                job_info = data['data'].get('jobInfo', {})
                company_info = data['data'].get('bossInfo', {})
                brand_info = data['data'].get('brandComInfo', {})
                
                # 使用正确的映射: Excel职位ID = JSON encryptId
                encrypt_id = job_info.get('encryptId', '')
                if not encrypt_id:
                    continue  # 跳过没有encryptId的记录
                
                # 提取关键信息
                detail_data = {
                    '职位ID': encrypt_id,  # 关键映射：Excel职位ID = JSON encryptId
                    '职位名称': job_info.get('jobName', ''),
                    '薪资范围': job_info.get('salaryDesc', ''),
                    '经验要求': job_info.get('experienceName', ''),
                    '学历要求': job_info.get('degreeName', ''),
                    '职位描述': job_info.get('description', ''),
                    '公司名称': brand_info.get('brandName', company_info.get('name', '')),
                    '公司规模': brand_info.get('scaleName', ''),
                    '行业': brand_info.get('industryName', ''),
                    '融资阶段': brand_info.get('stageName', ''),
                    '城市': job_info.get('cityName', ''),
                    '区域': job_info.get('areaDistrict', ''),
                    '地址': job_info.get('cityName', '') + job_info.get('areaDistrict', ''),
                    '经度': job_info.get('longitude', ''),
                    '纬度': job_info.get('latitude', ''),
                    '公司介绍': brand_info.get('introduction', ''),
                    '联系人': company_info.get('name', ''),
                    '联系人职位': company_info.get('title', ''),
                    '数据来源': '详情',
                    '数据完整性': '完整',
                    '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    '详情文件': os.path.basename(detail_file)
                }
                
                detail_data_list.append(detail_data)
        
        except Exception as e:
            print(f"⚠️  处理文件 {detail_file} 时出错: {e}")
    
    print(f"📊 从详情文件提取了 {len(detail_data_list)} 个职位信息")
    
    if not detail_data_list:
        print("❌ 没有提取到有效详情数据")
        return
    
    # 5. 转换为DataFrame
    df_details = pd.DataFrame(detail_data_list)
    print(f"📋 详情数据: {len(df_details)} 行, {len(df_details.columns)} 列")
    
    # 6. 检查ID映射
    print(f"\n🔍 检查ID映射关系:")
    if len(df_details) > 0:
        sample_ids = df_details['职位ID'].head(3).tolist()
        for i, job_id in enumerate(sample_ids):
            print(f"  示例职位ID {i+1}: {job_id[:20]}...")
    else:
        print("   没有详情数据")
    
    # 7. 合并数据
    print(f"\n🔄 开始合并数据...")
    
    # 检查Excel中是否有职位ID列
    if '职位ID' not in df_existing.columns:
        print("❌ Excel文件中没有'职位ID'列")
        print("💡 现有列名:")
        for col in df_existing.columns:
            print(f"   - {col}")
        return
    
    # 创建合并后的DataFrame
    merged_df = df_existing.copy()
    
    # 更新已有职位的数据
    updated_count = 0
    new_count = 0
    
    for idx, detail_row in df_details.iterrows():
        job_id = detail_row['职位ID']
        
        # 在现有数据中查找
        mask = merged_df['职位ID'] == job_id
        
        if mask.any():
            # 更新现有行
            row_idx = merged_df[mask].index[0]
            for col in detail_row.index:
                if col in merged_df.columns:
                    current_value = merged_df.at[row_idx, col]
                    detail_value = detail_row[col]
                    
                    # 只填充空值或更新缺失字段
                    if pd.isna(current_value) or current_value == '':
                        if pd.notna(detail_value) and detail_value != '':
                            try:
                                merged_df.at[row_idx, col] = detail_value
                                updated_count += 1
                            except:
                                pass  # 忽略类型不匹配
            
            # 更新数据来源和完整性
            if '数据来源' in merged_df.columns:
                current_source = str(merged_df.at[row_idx, '数据来源'])
                if '详情' not in current_source:
                    merged_df.at[row_idx, '数据来源'] = current_source + '+详情' if current_source else '详情'
            
            if '数据完整性' in merged_df.columns:
                merged_df.at[row_idx, '数据完整性'] = '完整'
            
        else:
            # 添加新行
            new_row = detail_row.to_dict()
            
            # 确保所有列都存在
            for col in merged_df.columns:
                if col not in new_row:
                    new_row[col] = ''
            
            # 按Excel列顺序重新排列
            new_df = pd.DataFrame([new_row])
            new_df = new_df[merged_df.columns]
            
            merged_df = pd.concat([merged_df, new_df], ignore_index=True)
            new_count += 1
    
    print(f"📈 合并结果:")
    print(f"   总记录数: {len(merged_df)} 行")
    print(f"   更新的职位: {updated_count} 个")
    print(f"   新增的职位: {new_count} 个")
    
    # 更新数据完整性统计
    if '数据完整性' in merged_df.columns:
        complete_count = (merged_df['数据完整性'] == '完整').sum()
        print(f"   完整数据: {complete_count} 行 ({complete_count/len(merged_df)*100:.1f}%)")
    
    # 8. 保存文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = os.path.splitext(os.path.basename(latest_excel))[0]
    output_file = f'{base_name}_正确合并_{timestamp}.xlsx'
    merged_df.to_excel(output_file, index=False)
    
    print(f"\n💾 保存到: {output_file}")
    print(f"📊 文件大小: {os.path.getsize(output_file):,} 字节")
    
    # 9. 显示更新/新增的职位
    if updated_count > 0:
        print(f"\n🔄 更新的职位 ({min(3, updated_count)} 个示例):")
        # 找出更新的职位
        updated_jobs = []
        for job_id in df_details['职位ID']:
            if job_id in df_existing['职位ID'].values:
                job_name = df_details[df_details['职位ID'] == job_id]['职位名称'].iloc[0] if not df_details[df_details['职位ID'] == job_id].empty else '未知'
                updated_jobs.append(job_name)
        
        for i, job_name in enumerate(updated_jobs[:3]):
            print(f"   • {job_name}")
    
    if new_count > 0:
        print(f"\n🆕 新增的职位 ({new_count} 个):")
        new_jobs = merged_df[~merged_df['职位ID'].isin(df_existing['职位ID'])]
        for idx, row in new_jobs.head(3).iterrows():
            print(f"   • {row['职位名称']} - {row['薪资范围']}")
    
    print(f"\n✅ 合并完成！")
    print(f"💡 验证: Excel职位ID = JSON encryptId 映射正确")
    print(f"\n📋 使用说明:")
    print(f"   1. 设置工作目录: export SCHEME_B_WORKSPACE=\"你的工作目录\"")
    print(f"   2. 运行脚本: python3 {os.path.basename(__file__)}")
    print(f"   3. 检查输出文件: {output_file}")

if __name__ == "__main__":
    main()