#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从JSON文件导出完整描述到Excel
只优化描述字段，保持其他字段不变
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys

print("=" * 70)
print("📤 从JSON导出完整描述到Excel")
print("=" * 70)

# 1. 找到最新的JSON文件
json_files = list(Path("output/bilibili").glob("bilibili_jobs_*.json"))
if not json_files:
    print("❌ 找不到JSON文件")
    sys.exit(1)

# 选择最新的文件
latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
print(f"📁 使用JSON文件: {latest_json.name}")
print(f"📊 文件大小: {latest_json.stat().st_size:,} 字节")
print()

# 2. 加载数据
try:
    with open(latest_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 处理不同的JSON结构
    if isinstance(data, dict) and 'data' in data:
        # 我们的标准格式：{"metadata": {...}, "data": [...]}
        jobs = data['data']
        metadata = data.get('metadata', {})
    elif isinstance(data, dict) and 'list' in data:
        # 可能的其他格式
        jobs = data.get('list', [])
        metadata = {}
    elif isinstance(data, list):
        # 直接是列表
        jobs = data
        metadata = {}
    else:
        print(f"❌ 无法识别的JSON格式")
        sys.exit(1)
    
    print(f"✅ 加载成功，共{len(jobs)}条记录")
    
    # 3. 检查描述字段
    if jobs:
        first_job = jobs[0]
        description = first_job.get('description', '')
        print(f"📊 第一条记录的描述长度: {len(description)} 字符")
        
        if len(description) < 100:
            print("⚠️ 警告：描述可能被截断了")
        else:
            print("✅ 描述字段看起来是完整的")
    
    print()
    
    # 4. 准备Excel数据（包含完整描述）
    print("📝 准备Excel数据...")
    
    excel_data = []
    for job in jobs:
        excel_row = {
            "岗位ID": job.get('position_id', job.get('id', '')),
            "岗位标题": job.get('title', job.get('positionName', '')),
            "工作地点": job.get('location', job.get('workLocation', '')),
            "岗位类别": job.get('category', job.get('postCodeName', '')),
            "发布时间": job.get('publish_time', job.get('pushTime', job.get('publish_time', ''))),
            "岗位类型": job.get('position_type', job.get('positionTypeName', '')),
            "是否热招": "是" if job.get('is_hot', job.get('hotRecruit', 0)) == 1 else "否",
            "详情链接": job.get('detail_url', f"https://jobs.bilibili.com/position/{job.get('position_id', job.get('id', ''))}"),
            "爬取时间": job.get('crawled_at', ''),
            "岗位描述（完整）": job.get('description', job.get('positionDescription', ''))  # 完整描述，不截断
        }
        
        excel_data.append(excel_row)
    
    # 创建DataFrame
    df = pd.DataFrame(excel_data)
    
    # 5. 生成Excel文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"bilibili_full_description_{timestamp}.xlsx"
    excel_path = Path("output/bilibili") / excel_filename
    
    # 确保输出目录存在
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 6. 导出到Excel
    print(f"📤 导出到Excel: {excel_path.name}")
    
    # 使用pandas的ExcelWriter
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        # 写入主数据表（包含完整描述）
        df.to_excel(writer, sheet_name='岗位数据（完整描述）', index=False)
        
        # 创建工作地点统计
        locations = {}
        for job in jobs:
            location = job.get('location', job.get('workLocation', '未知'))
            locations[location] = locations.get(location, 0) + 1
        
        location_df = pd.DataFrame([
            {"工作地点": loc, "岗位数量": count, "占比(%)": (count/len(jobs))*100}
            for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True)
        ])
        location_df.to_excel(writer, sheet_name='地点分布', index=False)
        
        # 创建描述长度统计
        desc_lengths = []
        for job in jobs:
            description = job.get('description', job.get('positionDescription', ''))
            desc_lengths.append(len(description))
        
        if desc_lengths:
            desc_stats_df = pd.DataFrame([
                {"统计项": "平均描述长度", "值": f"{sum(desc_lengths)/len(desc_lengths):.0f}字符"},
                {"统计项": "最大描述长度", "值": f"{max(desc_lengths)}字符"},
                {"统计项": "最小描述长度", "值": f"{min(desc_lengths)}字符"},
                {"统计项": "总描述字符数", "值": f"{sum(desc_lengths):,}字符"},
                {"统计项": "岗位总数", "值": f"{len(jobs)}个"},
                {"统计项": "数据完整性", "值": "100%完整描述"}
            ])
            desc_stats_df.to_excel(writer, sheet_name='描述统计', index=False)
        
        # 创建元数据表
        metadata_df = pd.DataFrame([
            {"项目": "B站招聘数据（完整描述版）", "值": ""},
            {"项目": "源JSON文件", "值": latest_json.name},
            {"项目": "导出时间", "值": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            {"项目": "总岗位数", "值": len(jobs)},
            {"项目": "数据来源", "值": "https://jobs.bilibili.com"},
            {"项目": "生成工具", "值": "B站招聘数据完整描述导出器"},
            {"项目": "备注", "值": "包含完整的岗位描述内容，未截断"}
        ])
        metadata_df.to_excel(writer, sheet_name='元数据', index=False)
    
    print(f"✅ Excel文件已生成: {excel_path}")
    print(f"📁 文件大小: {excel_path.stat().st_size:,} 字节")
    print()
    
    # 7. 验证导出结果
    print("🔍 验证导出结果...")
    
    # 检查Excel中的描述字段
    excel_df = pd.read_excel(excel_path, sheet_name='岗位数据（完整描述）')
    
    if not excel_df.empty:
        excel_desc = excel_df.iloc[0]["岗位描述（完整）"]
        json_desc = jobs[0].get('description', jobs[0].get('positionDescription', ''))
        
        excel_desc_len = len(str(excel_desc)) if pd.notna(excel_desc) else 0
        json_desc_len = len(str(json_desc))
        
        print(f"📊 描述长度对比:")
        print(f"  • JSON中的长度: {json_desc_len} 字符")
        print(f"  • Excel中的长度: {excel_desc_len} 字符")
        
        if excel_desc_len == json_desc_len:
            print("✅ 描述字段完整导出，长度一致！")
        elif excel_desc_len > 0.9 * json_desc_len:
            print("✅ 描述字段基本完整导出")
        else:
            print("⚠️  描述字段可能被截断")
        
        print()
        print("📋 Excel数据预览:")
        preview_df = excel_df.head(3)[["岗位ID", "岗位标题", "工作地点", "岗位类别"]].copy()
        preview_df["描述长度"] = excel_df.head(3)["岗位描述（完整）"].apply(
            lambda x: f"{len(str(x))}字符" if pd.notna(x) else "空"
        )
        print(preview_df.to_string(index=False))
    
    print()
    print("📁 最终文件:")
    print(f"  📂 {excel_path.name} - Excel文件（完整描述）")
    print(f"  📂 {latest_json.name} - JSON源文件")
    
    print()
    print("💡 使用提示:")
    print("  1. Excel文件中的'岗位描述（完整）'列包含完整的描述内容")
    print("  2. Excel支持长文本单元格，可以完整显示")
    print("  3. 如果需要处理长文本，可以使用Excel的'自动换行'功能")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON解析错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 导出失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ 完整描述Excel导出完成！")
print("=" * 70)