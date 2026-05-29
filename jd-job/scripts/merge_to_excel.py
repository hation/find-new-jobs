#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
京东招聘数据合并为Excel文件
基于anti-job项目的Excel合并逻辑
统一数据导出格式
"""

import json
import os
import pandas as pd
import glob
from datetime import datetime
from pathlib import Path
import sys
import re

def find_jd_jobs_data():
    """查找最新的京东招聘数据"""
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "output" / "jd_jobs"
    
    if not output_dir.exists():
        print("❌ 未找到京东招聘数据目录")
        return None, None
    
    # 查找所有Excel文件
    excel_files = list(output_dir.glob("*.xlsx"))
    if not excel_files:
        print("❌ 未找到Excel数据文件")
        return None, None
    
    # 按修改时间排序，取最新的
    excel_files = sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = excel_files[0]
    
    print(f"📁 找到最新数据文件: {latest_file.name}")
    return output_dir, latest_file

def load_jd_positions(file_path):
    """加载京东岗位数据"""
    try:
        df = pd.read_excel(file_path)
        print(f"📊 加载数据: {len(df)} 行 × {len(df.columns)} 列")
        
        # 转换为字典列表（兼容anti-job格式）
        positions = []
        for _, row in df.iterrows():
            position = row.to_dict()
            
            # 如果包含raw_data，尝试解析
            if 'raw_data' in position and isinstance(position['raw_data'], str):
                try:
                    raw_data = json.loads(position['raw_data'])
                    # 合并原始数据
                    position.update(raw_data)
                except:
                    pass
            
            positions.append(position)
        
        print(f"✅ 成功转换 {len(positions)} 个岗位数据")
        return positions
        
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return []

def process_jd_positions(positions):
    """处理京东岗位数据，转换为适合Excel的格式"""
    if not positions:
        return []
    
    processed = []
    
    for i, position in enumerate(positions):
        try:
            # 提取基本信息
            processed_position = {
                "序号": i + 1,
                "岗位ID": position.get("position_id") or position.get("id", ""),
                "岗位名称": position.get("position_name", ""),
                "岗位类别": position.get("job_type", ""),
                "工作地点": position.get("work_location", ""),
                "发布时间": position.get("publish_date", ""),
                "所属部门": position.get("department", ""),
                "学历要求": extract_education(position.get("education_requirement", "")),
                "工作经验": extract_experience(position.get("work_experience", "")),
                "岗位要求": position.get("position_requirements", ""),
                "岗位描述": position.get("position_description", ""),
                "岗位标签": extract_tags(position),
                "岗位代码": position.get("recruitment_number", ""),
                "是否收藏": "否",  # 京东没有收藏功能
                "数据来源": "京东招聘官网"
            }
            
            # 添加类别名称（如果有）
            if "job_type" in position:
                processed_position["类别名称"] = position["job_type"]
            
            processed.append(processed_position)
            
        except Exception as e:
            print(f"⚠️  处理岗位 {i+1} 失败: {e}")
    
    return processed

def extract_education(education_text):
    """从文本中提取学历要求"""
    if not education_text:
        return "学历不限"
    
    # 常见学历关键词
    education_keywords = {
        "博士": "博士",
        "硕士": "硕士", 
        "研究生": "硕士",
        "本科": "本科",
        "大专": "大专",
        "专科": "大专",
        "高中": "高中",
        "中专": "中专"
    }
    
    for keyword, level in education_keywords.items():
        if keyword in education_text:
            return level
    
    return "学历不限"

def extract_experience(experience_text):
    """从文本中提取工作经验"""
    if not experience_text:
        return "经验不限"
    
    # 匹配数字+年
    import re
    year_pattern = r'(\d+)[\+-]?\s*年'
    matches = re.findall(year_pattern, experience_text)
    
    if matches:
        years = [int(m) for m in matches]
        if len(years) >= 2:
            return f"{min(years)}-{max(years)}年"
        else:
            return f"{years[0]}+年"
    
    # 检查常见关键词
    if "不限" in experience_text or "无要求" in experience_text:
        return "经验不限"
    elif "应届" in experience_text:
        return "应届生"
    elif "实习" in experience_text:
        return "实习生"
    
    return "经验不限"

def extract_tags(position):
    """提取岗位标签"""
    tags = []
    
    # 从工作地点提取
    location = position.get("work_location", "")
    if location:
        tags.append(location)
    
    # 从部门提取
    department = position.get("department", "")
    if department:
        tags.append(department)
    
    # 从岗位类型提取
    job_type = position.get("job_type", "")
    if job_type:
        tags.append(job_type)
    
    # 检查是否热门
    is_hot = position.get("is_hot", 0)
    if is_hot == 1:
        tags.append("热门岗位")
    
    return ", ".join(tags) if tags else ""

def create_jd_excel_file(processed_positions, output_dir):
    """创建京东Excel文件"""
    if not processed_positions:
        print("❌ 没有可用的处理后的数据")
        return None
    
    # 转换为DataFrame
    df = pd.DataFrame(processed_positions)
    
    print(f"📊 DataFrame形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    print(f"📋 列名: {', '.join(df.columns.tolist())}")
    
    # 格式化发布时间
    if '发布时间' in df.columns:
        def format_publish_date(date_str):
            if not date_str or pd.isna(date_str):
                return "未知"
            try:
                # 尝试解析日期
                if isinstance(date_str, str):
                    # 移除时间部分（如果有）
                    date_str = date_str.split()[0]
                return str(date_str)
            except:
                return str(date_str)
        
        df['发布时间'] = df['发布时间'].apply(format_publish_date)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"jd_international_positions_{timestamp}.xlsx"
    excel_filepath = output_dir / excel_filename
    
    print(f"💾 创建Excel文件: {excel_filename}")
    
    try:
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
                    if pd.isna(locations):
                        continue
                    for location in str(locations).split(','):
                        location = location.strip()
                        if location:
                            location_counts[location] = location_counts.get(location, 0) + 1
                
                if location_counts:
                    location_stats = pd.DataFrame({
                        '工作地点': list(location_counts.keys()),
                        '岗位数量': list(location_counts.values())
                    }).sort_values('岗位数量', ascending=False)
                    
                    location_stats.to_excel(writer, sheet_name='地点分布', index=False)
                    print(f"✅ 工作表2: '地点分布' - {len(location_stats)} 个地点")
            
            # 3. 岗位类别统计
            if '岗位类别' in df.columns:
                category_counts = df['岗位类别'].value_counts().reset_index()
                category_counts.columns = ['岗位类别', '岗位数量']
                category_counts.to_excel(writer, sheet_name='类别分布', index=False)
                print(f"✅ 工作表3: '类别分布' - {len(category_counts)} 个类别")
            
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
                    '公司名称',
                    'Excel生成时间',
                    '数据文件',
                    '数据质量'
                ],
                '值': [
                    len(df),
                    '京东招聘官网',
                    '京东集团',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    excel_filename,
                    f"完整率: {df.notnull().sum().sum()/(df.shape[0]*df.shape[1])*100:.1f}%"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
            print(f"✅ 工作表7: '数据摘要' - 数据基本信息")
        
        print(f"🎉 Excel文件创建成功: {excel_filepath}")
        
        # 创建简化版CSV文件
        csv_filename = f"jd_positions_simple_{timestamp}.csv"
        csv_filepath = output_dir / csv_filename
        
        # 选择关键列
        key_columns = ['序号', '岗位名称', '岗位类别', '工作地点', '学历要求', '工作经验', '所属部门']
        available_columns = [col for col in key_columns if col in df.columns]
        
        if available_columns:
            simple_df = df[available_columns]
            simple_df.to_csv(csv_filepath, index=False, encoding='utf-8-sig')
            print(f"✅ CSV文件创建成功: {csv_filepath}")
        
        return excel_filepath
        
    except Exception as e:
        print(f"❌ 创建Excel文件失败: {e}")
        return None

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
            
            # 显示列名
            columns = main_sheet.columns.tolist()
            print(f"   列名: {', '.join(columns[:8])}...")
            
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
    print("🚀 京东招聘数据合并为Excel文件")
    print("="*70)
    print("🎯 目标: 将京东招聘数据合并为统一格式的Excel文件")
    print("📊 包含: 所有岗位数据 + 6个统计分析表 + 数据摘要")
    print("🔄 基于anti-job项目的统一导出格式")
    print()
    
    # 1. 查找最新的京东数据
    output_dir, data_file = find_jd_jobs_data()
    if not output_dir or not data_file:
        return
    
    # 2. 加载数据
    positions = load_jd_positions(data_file)
    if not positions:
        return
    
    # 3. 处理数据
    print("\n🔄 处理数据中...")
    processed_positions = process_jd_positions(positions)
    
    if not processed_positions:
        print("❌ 数据处理失败")
        return
    
    # 4. 创建Excel文件
    print("\n💾 创建Excel文件中...")
    excel_filepath = create_jd_excel_file(processed_positions, output_dir)
    
    if not excel_filepath:
        print("❌ Excel文件创建失败")
        return
    
    # 5. 验证Excel文件
    verify_excel_file(excel_filepath)
    
    # 6. 显示结果
    print("\n" + "="*70)
    print("🎉 京东招聘Excel文件合并完成！")
    print("="*70)
    print(f"📁 文件位置: {excel_filepath}")
    print()
    print("📋 Excel文件包含以下工作表:")
    print("   1. 📄 '所有岗位' - 所有岗位的完整信息（中文列名）")
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
    print("✅ 基于anti-job项目的统一Excel导出格式已成功应用！")
    print("="*70)

if __name__ == "__main__":
    main()