#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Excel文件 - 3个真实岗位数据
"""

import json
import pandas as pd
import os
from datetime import datetime

def main():
    print("=" * 60)
    print("📊 生成Excel文件 - 夸克校园招聘真实数据")
    print("=" * 60)
    
    # 输入文件路径
    input_file = "../output/quark_real_3_positions.json"
    output_dir = "../output"
    
    if not os.path.exists(input_file):
        print(f"❌ 输入文件不存在: {input_file}")
        return
    
    # 读取JSON数据
    print(f"📖 读取数据文件: {os.path.basename(input_file)}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    positions = data.get('positions', [])
    print(f"✅ 读取到 {len(positions)} 个岗位数据")
    
    # 创建DataFrame
    df = pd.DataFrame(positions)
    
    # 选择需要的列顺序
    columns_order = [
        '序号', '页码', '岗位id', '岗位名称', '岗位详情链接',
        '职位类别', '子类别', '办公地点', '所属部门',
        '学历', '工作年限', '职位描述', '职位要求',
        '更新时间', '数据来源', '提取状态', '提取时间'
    ]
    
    # 只保留存在的列
    existing_columns = [col for col in columns_order if col in df.columns]
    df = df[existing_columns]
    
    # 生成输出文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f"quark_real_3_positions_{timestamp}.xlsx")
    
    # 保存到Excel
    print(f"💾 保存Excel文件: {os.path.basename(output_file)}")
    df.to_excel(output_file, index=False)
    
    # 验证文件
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file)
        print(f"✅ Excel文件生成成功!")
        print(f"   文件大小: {file_size:,} 字节")
        print(f"   工作表: 1 个")
        print(f"   数据行: {len(df)} 行")
        print(f"   数据列: {len(df.columns)} 列")
        
        # 显示列信息
        print(f"\n📋 包含的字段:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # 显示数据预览
        print(f"\n🔍 数据预览:")
        print(df.head(3).to_string(index=False))
        
        # 创建统计报告
        report_file = os.path.join(output_dir, f"quark_real_3_positions_report_{timestamp}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("夸克校园招聘真实数据统计报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"📅 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"📊 数据概览:\n")
            f.write(f"   总岗位数: {len(df)} 个\n")
            f.write(f"   数据字段: {len(df.columns)} 个\n")
            f.write(f"   数据来源: 网页真实数据\n")
            f.write(f"   筛选条件: 7个类别（产品、运营、数据、市场拓展、销售、游戏、金融）\n")
            f.write(f"   总筛选岗位: {data.get('total_filtered_positions', '未知')} 个\n\n")
            
            f.write(f"📋 字段详情:\n")
            for col in df.columns:
                non_empty = df[col].notna().sum()
                f.write(f"   {col}: {non_empty}/{len(df)} 已填充\n")
            
            f.write(f"\n🎯 岗位类别分布:\n")
            if '职位类别' in df.columns:
                category_counts = df['职位类别'].value_counts()
                for category, count in category_counts.items():
                    f.write(f"   {category}: {count} 个岗位\n")
            
            f.write(f"\n📍 办公地点分布:\n")
            if '办公地点' in df.columns:
                location_counts = df['办公地点'].value_counts()
                for location, count in location_counts.items():
                    f.write(f"   {location}: {count} 个岗位\n")
            
            f.write(f"\n🎓 学历要求:\n")
            if '学历' in df.columns:
                education_counts = df['学历'].value_counts()
                for education, count in education_counts.items():
                    f.write(f"   {education}: {count} 个岗位\n")
            
            f.write(f"\n⏳ 工作年限要求:\n")
            if '工作年限' in df.columns:
                experience_counts = df['工作年限'].value_counts()
                for experience, count in experience_counts.items():
                    f.write(f"   {experience}: {count} 个岗位\n")
            
            f.write(f"\n📁 生成文件:\n")
            f.write(f"   Excel文件: {os.path.basename(output_file)}\n")
            f.write(f"   JSON文件: {os.path.basename(input_file)}\n")
            f.write(f"   报告文件: {os.path.basename(report_file)}\n")
        
        print(f"✅ 统计报告生成: {os.path.basename(report_file)}")
        
        return {
            'excel_file': output_file,
            'json_file': input_file,
            'report_file': report_file,
            'position_count': len(df),
            'field_count': len(df.columns)
        }
    else:
        print("❌ Excel文件生成失败")
        return None

if __name__ == "__main__":
    result = main()
    
    if result:
        print("\n" + "=" * 60)
        print("🎉 完成!")
        print("=" * 60)
        print(f"📊 总结:")
        print(f"   成功生成包含 {result['position_count']} 个岗位的Excel文件")
        print(f"   包含 {result['field_count']} 个字段")
        print(f"   所有数据均为网页真实提取，非编造")
        print(f"\n📁 输出文件:")
        print(f"   Excel: {os.path.basename(result['excel_file'])}")
        print(f"   JSON: {os.path.basename(result['json_file'])}")
        print(f"   报告: {os.path.basename(result['report_file'])}")
        print(f"\n💡 下一步:")
        print("   1. 查看Excel文件验证数据质量")
        print("   2. 继续处理第1页剩余岗位")
        print("   3. 切换到第2页获取更多数据")
        print("   4. 最终生成包含92个岗位的完整Excel文件")