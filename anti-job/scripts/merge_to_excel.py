#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蚂蚁国际招聘数据合并为Excel文件
基于夸克项目框架的Excel合并逻辑
"""

import json
import os
import pandas as pd
import glob
from datetime import datetime
from pathlib import Path
import sys

def find_latest_crawl_dir():
    """查找最新的爬取目录"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output"
    
    # 查找所有爬取目录
    crawl_dirs = list(output_dir.glob("*crawl_*"))
    if not crawl_dirs:
        print("❌ 未找到爬取目录")
        return None
    
    # 按目录名中的时间戳排序，取最新的
    crawl_dirs = sorted(crawl_dirs, key=lambda x: x.name, reverse=True)
    
    for dir_path in crawl_dirs:
        # 检查是否有positions目录
        positions_dir = dir_path / "positions"
        if positions_dir.exists() and any(positions_dir.glob("*.json")):
            print(f"📁 找到数据目录: {dir_path.name}")
            return dir_path
    
    print("❌ 未找到包含岗位数据的目录")
    return None

def load_all_positions(crawl_dir):
    """加载所有岗位数据"""
    positions_dir = crawl_dir / "positions"
    
    if not positions_dir.exists():
        print(f"❌ positions目录不存在: {positions_dir}")
        return []
    
    position_files = list(positions_dir.glob("*.json"))
    if not position_files:
        print(f"❌ 没有找到岗位数据文件")
        return []
    
    print(f"📊 找到 {len(position_files)} 个岗位数据文件")
    
    all_positions = []
    for file_path in position_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                position = json.load(f)
            all_positions.append(position)
        except Exception as e:
            print(f"⚠️  读取文件 {file_path.name} 失败: {e}")
    
    print(f"✅ 成功加载 {len(all_positions)} 个岗位数据")
    return all_positions

def process_positions(positions):
    """处理岗位数据，转换为适合Excel的格式"""
    if not positions:
        return []
    
    processed = []
    
    for i, position in enumerate(positions):
        try:
            # 提取基本信息
            processed_position = {
                "序号": i + 1,
                "岗位ID": position.get("id", ""),
                "岗位名称": position.get("name", ""),
                "岗位类别": ", ".join(position.get("categories", [])),
                "工作地点": ", ".join(position.get("workLocations", [])),
                "发布时间": position.get("publishTime", ""),
                "所属部门": position.get("department", ""),
                "学历要求": position.get("degree", ""),
                "工作经验": format_experience(position.get("experience", {})),
                "岗位要求": position.get("requirement", ""),
                "岗位描述": position.get("description", ""),
                "岗位标签": format_tags(position.get("featureTagList", [])),
                "岗位代码": position.get("code", ""),
                "是否收藏": position.get("isCollected", ""),
                "数据来源": "蚂蚁国际招聘"
            }
            
            # 添加额外的字段
            if "category_names" in position:
                processed_position["类别名称"] = ", ".join(position["category_names"])
            
            processed.append(processed_position)
            
        except Exception as e:
            print(f"⚠️  处理岗位 {i+1} 失败: {e}")
    
    return processed

def format_experience(experience):
    """格式化工作经验"""
    if not isinstance(experience, dict):
        return "经验不限"
    
    from_years = experience.get("from")
    to_years = experience.get("to")
    
    if from_years is not None and to_years is not None:
        return f"{from_years}-{to_years}年"
    elif from_years is not None:
        return f"{from_years}+年"
    elif to_years is not None:
        return f"≤{to_years}年"
    else:
        return "经验不限"

def format_tags(tags):
    """格式化标签"""
    if not tags:
        return ""
    return ", ".join([str(tag) for tag in tags])

def create_excel_file(processed_positions, crawl_dir):
    """创建Excel文件"""
    if not processed_positions:
        print("❌ 没有可用的处理后的数据")
        return None
    
    # 转换为DataFrame
    df = pd.DataFrame(processed_positions)
    
    print(f"📊 DataFrame形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"📋 列名: {', '.join(df.columns.tolist())}")
    
    # 格式化学历要求
    if '学历要求' in df.columns:
        degree_map = {
            'bachelor': '本科',
            'master': '硕士',
            'doctor': '博士',
            'college': '大专',
            'high_school': '高中'
        }
        df['学历要求'] = df['学历要求'].apply(lambda x: degree_map.get(x, x or '学历不限'))
    
    # 格式化发布时间
    if '发布时间' in df.columns:
        def format_publish_time(time_str):
            if not time_str:
                return "未知"
            try:
                # 解析ISO时间格式
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return time_str
        
        df['发布时间'] = df['发布时间'].apply(format_publish_time)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"ant_international_positions_{timestamp}.xlsx"
    excel_filepath = crawl_dir / excel_filename
    
    print(f"💾 创建Excel文件: {excel_filename}")
    
    # 使用Excel写入器
    with pd.ExcelWriter(excel_filepath, engine='openpyxl') as writer:
        # 1. 主工作表：所有岗位
        df.to_excel(writer, sheet_name='所有岗位', index=False)
        
        print(f"✅ 工作表1: '所有岗位' - {len(df)} 行 × {len(df.columns)} 列")
        
        # 2. 工作地点统计
        if '工作地点' in df.columns:
            # 拆分工作地点（可能多个地点）
            location_counts = {}
            for locations in df['工作地点']:
                for location in str(locations).split(', '):
                    if location and location != 'nan':
                        location_counts[location] = location_counts.get(location, 0) + 1
            
            location_stats = pd.DataFrame({
                '工作地点': list(location_counts.keys()),
                '岗位数量': list(location_counts.values())
            }).sort_values('岗位数量', ascending=False)
            
            location_stats.to_excel(writer, sheet_name='地点分布', index=False)
            print(f"✅ 工作表2: '地点分布' - {len(location_stats)} 个地点")
        
        # 3. 岗位类别统计
        if '岗位类别' in df.columns:
            # 拆分岗位类别（可能多个类别）
            category_counts = {}
            for categories in df['岗位类别']:
                for category in str(categories).split(', '):
                    if category and category != 'nan':
                        category_counts[category] = category_counts.get(category, 0) + 1
            
            category_stats = pd.DataFrame({
                '岗位类别': list(category_counts.keys()),
                '岗位数量': list(category_counts.values())
            }).sort_values('岗位数量', ascending=False)
            
            category_stats.to_excel(writer, sheet_name='类别分布', index=False)
            print(f"✅ 工作表3: '类别分布' - {len(category_stats)} 个类别")
        
        # 4. 学历要求统计
        if '学历要求' in df.columns:
            education_stats = df['学历要求'].value_counts().reset_index()
            education_stats.columns = ['学历要求', '岗位数量']
            education_stats.to_excel(writer, sheet_name='学历分布', index=False)
            print(f"✅ 工作表4: '学历分布' - {len(education_stats)} 种学历要求")
        
        # 5. 部门统计
        if '所属部门' in df.columns:
            department_stats = df['所属部门'].value_counts().reset_index()
            department_stats.columns = ['所属部门', '岗位数量']
            department_stats.to_excel(writer, sheet_name='部门分布', index=False)
            print(f"✅ 工作表5: '部门分布' - {len(department_stats)} 个部门")
        
        # 6. 工作经验统计
        if '工作经验' in df.columns:
            experience_stats = df['工作经验'].value_counts().reset_index()
            experience_stats.columns = ['工作经验', '岗位数量']
            experience_stats.to_excel(writer, sheet_name='经验要求', index=False)
            print(f"✅ 工作表6: '经验要求' - {len(experience_stats)} 种经验要求")
        
        # 7. 数据摘要
        summary_data = {
            '统计项': [
                '总岗位数',
                '数据来源',
                '爬取时间',
                'Excel生成时间',
                '数据目录',
                '文件路径'
            ],
            '值': [
                len(df),
                '蚂蚁国际招聘官网',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(crawl_dir),
                str(excel_filepath)
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
        print(f"✅ 工作表7: '数据摘要' - 数据基本信息")
    
    print(f"🎉 Excel文件创建成功: {excel_filepath}")
    
    # 创建简化版CSV文件
    csv_filename = f"ant_positions_simple_{timestamp}.csv"
    csv_filepath = crawl_dir / csv_filename
    
    # 选择关键列
    key_columns = ['序号', '岗位名称', '岗位类别', '工作地点', '学历要求', '工作经验', '所属部门']
    available_columns = [col for col in key_columns if col in df.columns]
    
    if available_columns:
        simple_df = df[available_columns]
        simple_df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
        print(f"✅ CSV文件创建成功: {csv_filepath}")
    
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
            
            # 显示前几列
            columns = main_sheet.columns.tolist()
            if len(columns) > 8:
                print(f"   列名 (前8个): {', '.join(columns[:8])}...")
            else:
                print(f"   列名: {', '.join(columns)}")
            
            # 检查数据质量
            missing_values = main_sheet.isnull().sum().sum()
            total_cells = main_sheet.shape[0] * main_sheet.shape[1]
            missing_percentage = (missing_values / total_cells) * 100
            
            print(f"   缺失值: {missing_values}/{total_cells} ({missing_percentage:.1f}%)")
            
            if missing_percentage > 20:
                print(f"   ⚠️  缺失值较多，可能需要数据清洗")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel文件验证失败: {e}")
        return False

def main():
    """主函数"""
    print("="*70)
    print("🚀 蚂蚁国际招聘数据合并为Excel文件")
    print("="*70)
    print("🎯 目标: 将381个岗位数据合并为Excel文件")
    print("📊 包含: 所有岗位数据 + 6个统计分析表 + 数据摘要")
    print()
    
    # 1. 查找最新的爬取目录
    crawl_dir = find_latest_crawl_dir()
    if not crawl_dir:
        return
    
    # 2. 加载所有岗位数据
    positions = load_all_positions(crawl_dir)
    if not positions:
        return
    
    # 3. 处理数据
    print("\n🔄 处理数据中...")
    processed_positions = process_positions(positions)
    
    if not processed_positions:
        print("❌ 数据处理失败")
        return
    
    # 4. 创建Excel文件
    print("\n💾 创建Excel文件中...")
    excel_filepath = create_excel_file(processed_positions, crawl_dir)
    
    if not excel_filepath:
        print("❌ Excel文件创建失败")
        return
    
    # 5. 验证Excel文件
    verify_excel_file(excel_filepath)
    
    # 6. 显示结果
    print("\n" + "="*70)
    print("🎉 Excel文件合并完成！")
    print("="*70)
    print(f"📁 文件位置: {excel_filepath}")
    print()
    print("📋 Excel文件包含以下工作表:")
    print("   1. 📄 '所有岗位' - 381个岗位的完整信息")
    print("   2. 📊 '地点分布' - 工作地点统计分析")
    print("   3. 📊 '类别分布' - 岗位类别统计分析")
    print("   4. 📊 '学历分布' - 学历要求统计分析")
    print("   5. 📊 '部门分布' - 所属部门统计分析")
    print("   6. 📊 '经验要求' - 工作经验统计分析")
    print("   7. 📋 '数据摘要' - 数据基本信息汇总")
    print()
    print("💡 同时生成:")
    print("   📄 简化版CSV文件 (方便快速查看)")
    print()
    print("✅ 基于夸克项目框架的Excel合并逻辑已成功应用！")
    print("="*70)

if __name__ == "__main__":
    main()