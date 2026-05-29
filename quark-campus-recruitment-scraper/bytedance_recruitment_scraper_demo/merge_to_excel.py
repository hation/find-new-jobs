#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将夸克爬取数据合并为Excel文件
提取所有93个岗位的完整信息
"""

import json
import os
import pandas as pd
from datetime import datetime
import glob

def merge_to_excel():
    """将所有数据合并为Excel文件"""
    
    print("📊 夸克数据合并为Excel文件")
    print("=" * 60)
    
    # 找到最新的输出目录
    output_dirs = glob.glob("output/quark_page1_*")
    if not output_dirs:
        print("❌ 未找到输出目录")
        return None
    
    latest_dir = sorted(output_dirs, key=os.path.getmtime, reverse=True)[0]
    print(f"📁 数据目录: {latest_dir}")
    
    # 1. 读取处理后的数据文件
    processed_file = os.path.join(latest_dir, "all_positions_processed.json")
    if not os.path.exists(processed_file):
        print(f"❌ 处理后的数据文件不存在: {processed_file}")
        return None
    
    with open(processed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    positions = data.get("positions", [])
    print(f"📈 找到 {len(positions)} 个岗位数据")
    
    if not positions:
        print("❌ 没有找到岗位数据")
        return None
    
    # 2. 转换为DataFrame
    print("🔄 转换为DataFrame...")
    
    # 创建DataFrame
    df = pd.DataFrame(positions)
    
    print(f"📊 DataFrame形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"📋 列名: {', '.join(df.columns.tolist())}")
    
    # 3. 数据清洗和格式化
    print("🧹 数据清洗和格式化...")
    
    # 重命名列名（中文更友好）
    column_mapping = {
        'position_id': '岗位ID',
        'position_name': '岗位名称',
        'position_category': '岗位类别',
        'work_location': '工作地点',
        'update_time': '更新时间',
        'department': '所属部门',
        'education_requirement': '学历要求',
        'work_experience': '工作经验',
        'position_description': '岗位描述',
        'position_requirements': '任职要求',
        'position_url': '详情页链接',
        'source': '数据来源',
        'extract_time': '提取时间',
        'page_number': '所在页码',
        'position_in_page': '页内位置'
    }
    
    # 只重命名存在的列
    existing_columns = {old: new for old, new in column_mapping.items() if old in df.columns}
    df = df.rename(columns=existing_columns)
    
    # 格式化时间戳
    if '更新时间' in df.columns:
        def format_timestamp(ts):
            if not ts:
                return "未知"
            try:
                # 时间戳是毫秒，转换为秒
                dt = datetime.fromtimestamp(int(ts) / 1000)
                return dt.strftime("%Y-%m-%d")
            except:
                return str(ts)
        
        df['更新时间'] = df['更新时间'].apply(format_timestamp)
    
    # 处理学历要求
    if '学历要求' in df.columns:
        degree_map = {
            'bachelor': '本科',
            'master': '硕士',
            'doctor': '博士',
            'college': '大专',
            'high_school': '高中'
        }
        df['学历要求'] = df['学历要求'].apply(lambda x: degree_map.get(x, x or '学历不限'))
    
    # 4. 创建Excel文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"quark_positions_all_{timestamp}.xlsx"
    excel_filepath = os.path.join(latest_dir, excel_filename)
    
    print(f"💾 创建Excel文件: {excel_filename}")
    
    # 使用Excel写入器
    with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
        # 主工作表：所有岗位
        df.to_excel(writer, sheet_name='所有岗位', index=False)
        
        # 创建工作地点统计表
        if '工作地点' in df.columns:
            location_stats = df['工作地点'].value_counts().reset_index()
            location_stats.columns = ['工作地点', '岗位数量']
            location_stats.to_excel(writer, sheet_name='地点分布', index=False)
        
        # 创建岗位类别统计表
        if '岗位类别' in df.columns:
            category_stats = df['岗位类别'].value_counts().reset_index()
            category_stats.columns = ['岗位类别', '岗位数量']
            category_stats.to_excel(writer, sheet_name='类别分布', index=False)
        
        # 创建学历要求统计表
        if '学历要求' in df.columns:
            education_stats = df['学历要求'].value_counts().reset_index()
            education_stats.columns = ['学历要求', '岗位数量']
            education_stats.to_excel(writer, sheet_name='学历分布', index=False)
        
        # 创建数据摘要表
        summary_data = {
            '统计项': ['总计岗位数', '数据提取时间', '数据来源', 'Excel生成时间', '文件路径'],
            '值': [
                len(df),
                data.get('metadata', {}).get('extract_time', '未知'),
                data.get('metadata', {}).get('source', '未知'),
                datetime.now().isoformat(),
                excel_filepath
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
    
    print(f"✅ Excel文件创建成功: {excel_filepath}")
    
    # 5. 创建简化版CSV文件（方便查看）
    csv_filename = f"quark_positions_simple_{timestamp}.csv"
    csv_filepath = os.path.join(latest_dir, csv_filename)
    
    # 选择关键列
    key_columns = ['岗位名称', '岗位类别', '工作地点', '学历要求', '所属部门', '更新时间']
    available_columns = [col for col in key_columns if col in df.columns]
    
    if available_columns:
        simple_df = df[available_columns]
        simple_df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
        print(f"✅ CSV文件创建成功: {csv_filepath}")
    
    # 6. 显示数据预览
    print("\n📋 Excel文件内容预览:")
    print(f"   工作表1: '所有岗位' - {len(df)} 行 × {len(df.columns)} 列")
    print(f"   工作表2: '地点分布' - 工作地点统计")
    print(f"   工作表3: '类别分布' - 岗位类别统计")
    print(f"   工作表4: '学历分布' - 学历要求统计")
    print(f"   工作表5: '数据摘要' - 数据基本信息")
    
    print("\n📊 前5个岗位预览:")
    preview_columns = ['岗位名称', '岗位类别', '工作地点', '学历要求']
    available_preview = [col for col in preview_columns if col in df.columns]
    
    if available_preview:
        preview_df = df[available_preview].head(5)
        print(preview_df.to_string(index=False))
    
    # 7. 创建文件清单
    files_list_file = os.path.join(latest_dir, "files_list.txt")
    with open(files_list_file, 'w', encoding='utf-8') as f:
        f.write("夸克校园招聘数据文件清单\n")
        f.write("=" * 50 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据目录: {latest_dir}\n")
        f.write(f"岗位总数: {len(df)} 个\n")
        f.write("\n文件列表:\n")
        
        for file in os.listdir(latest_dir):
            if file.endswith(('.json', '.xlsx', '.csv', '.txt')):
                filepath = os.path.join(latest_dir, file)
                size_kb = os.path.getsize(filepath) / 1024
                f.write(f"- {file} ({size_kb:.1f} KB)\n")
    
    print(f"\n📋 文件清单: {files_list_file}")
    
    return excel_filepath

def verify_excel_file(excel_filepath):
    """验证Excel文件内容"""
    print("\n🔍 验证Excel文件内容...")
    
    try:
        # 读取Excel文件
        excel_data = pd.read_excel(excel_filepath, sheet_name=None)
        
        print(f"✅ Excel文件验证成功")
        print(f"   包含 {len(excel_data)} 个工作表")
        
        for sheet_name, sheet_data in excel_data.items():
            print(f"   📄 {sheet_name}: {sheet_data.shape[0]} 行 × {sheet_data.shape[1]} 列")
        
        # 检查主工作表
        if '所有岗位' in excel_data:
            main_sheet = excel_data['所有岗位']
            print(f"\n📊 主工作表统计:")
            print(f"   岗位总数: {len(main_sheet)} 个")
            print(f"   字段数量: {len(main_sheet.columns)} 个")
            print(f"   列名: {', '.join(main_sheet.columns.tolist()[:8])}...")
            
            # 检查是否有空值
            missing_values = main_sheet.isnull().sum().sum()
            print(f"   缺失值总数: {missing_values} 个")
            
            if missing_values > 0:
                print(f"   ⚠️  发现缺失值，可能需要数据清洗")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel文件验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 夸克数据合并为Excel文件")
    print("=" * 60)
    print("🎯 目标: 将93个岗位数据合并为Excel文件")
    print("📊 包含: 所有岗位数据 + 统计分布 + 数据摘要")
    print()
    
    # 切换到脚本目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 合并数据为Excel
    excel_filepath = merge_to_excel()
    
    if excel_filepath:
        # 验证Excel文件
        verify_excel_file(excel_filepath)
        
        print("\n" + "=" * 60)
        print("🎉 Excel文件合并完成！")
        print(f"📁 文件位置: {excel_filepath}")
        print("💡 文件包含:")
        print("   1. 所有93个岗位的完整信息")
        print("   2. 工作地点分布统计")
        print("   3. 岗位类别分布统计")
        print("   4. 学历要求分布统计")
        print("   5. 数据基本信息摘要")
        print("   6. 简化版CSV文件（方便查看）")
        print("   7. 文件清单")
        print()
        print("✅ API方案修复 + 数据爬取 + Excel合并 全部完成！")
    else:
        print("\n❌ Excel文件创建失败")
    
    print("=" * 60)

if __name__ == "__main__":
    main()