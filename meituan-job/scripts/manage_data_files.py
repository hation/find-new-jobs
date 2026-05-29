#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘数据文件管理工具
按照夸克规范：管理数据文件，清理测试数据，保留完整数据
"""

import os
import json
import glob
from datetime import datetime
import shutil

def list_data_files():
    """列出所有数据文件"""
    print("📁 美团招聘数据文件列表")
    print("=" * 60)
    
    json_files = sorted(glob.glob('output/crawl_data/meituan_*.json'))
    csv_files = sorted(glob.glob('output/crawl_data/meituan_*.csv'))
    
    print(f"📊 JSON文件: {len(json_files)}个")
    print(f"📊 CSV文件: {len(csv_files)}个")
    print("=" * 60)
    
    # 分析JSON文件
    file_info = []
    for filepath in json_files:
        filename = os.path.basename(filepath)
        size = os.path.getsize(filepath)
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                positions = len(data.get('positions', []))
                crawl_time = data.get('crawl_time', '未知')
                file_info.append({
                    'filename': filename,
                    'size_kb': size / 1024,
                    'positions': positions,
                    'crawl_time': crawl_time,
                    'mtime': mtime,
                    'filepath': filepath
                })
        except:
            file_info.append({
                'filename': filename,
                'size_kb': size / 1024,
                'positions': '解析失败',
                'crawl_time': '未知',
                'mtime': mtime,
                'filepath': filepath
            })
    
    # 按岗位数量排序
    file_info.sort(key=lambda x: x['positions'] if isinstance(x['positions'], int) else 0, reverse=True)
    
    print("\n📋 JSON文件详情:")
    for info in file_info:
        status = "✅ 完整数据" if info['positions'] == 117 else "⚠️ 测试数据"
        print(f"\n  {status}")
        print(f"  文件名: {info['filename']}")
        print(f"  大小: {info['size_kb']:.1f} KB")
        print(f"  岗位数: {info['positions']}")
        print(f"  爬取时间: {info['crawl_time']}")
        print(f"  修改时间: {info['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    return file_info

def identify_complete_data(file_info):
    """识别完整数据文件"""
    print("\n" + "=" * 60)
    print("🎯 识别完整数据文件")
    print("=" * 60)
    
    complete_files = []
    for info in file_info:
        if info['positions'] == 117:  # 完整117个岗位
            complete_files.append(info)
    
    if complete_files:
        print(f"✅ 找到 {len(complete_files)} 个完整数据文件:")
        for info in complete_files:
            print(f"\n  📁 {info['filename']}")
            print(f"    大小: {info['size_kb']:.1f} KB")
            print(f"    爬取时间: {info['crawl_time']}")
            print(f"    修改时间: {info['mtime'].strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("⚠️ 未找到完整数据文件（117个岗位）")
    
    return complete_files

def cleanup_test_files(file_info, keep_latest=True):
    """清理测试文件，保留完整数据"""
    print("\n" + "=" * 60)
    print("🧹 清理测试数据文件")
    print("=" * 60)
    
    # 识别完整文件
    complete_files = [info for info in file_info if info['positions'] == 117]
    test_files = [info for info in file_info if info['positions'] != 117]
    
    if not complete_files:
        print("❌ 没有完整数据文件，无法清理")
        return
    
    # 找到最新的完整文件
    if keep_latest:
        latest_complete = max(complete_files, key=lambda x: x['mtime'])
        print(f"📅 最新完整文件: {latest_complete['filename']}")
        print(f"⏰ 爬取时间: {latest_complete['crawl_time']}")
    
    print(f"\n📊 文件统计:")
    print(f"  完整文件: {len(complete_files)}个")
    print(f"  测试文件: {len(test_files)}个")
    
    if not test_files:
        print("✅ 没有需要清理的测试文件")
        return
    
    # 确认清理
    print("\n🔍 待清理的测试文件:")
    for info in test_files:
        print(f"  ❌ {info['filename']} ({info['positions']}个岗位, {info['size_kb']:.1f}KB)")
    
    # 创建备份目录
    backup_dir = 'output/crawl_data/backup'
    os.makedirs(backup_dir, exist_ok=True)
    
    # 移动测试文件到备份目录
    moved_files = []
    for info in test_files:
        src = info['filepath']
        dst = os.path.join(backup_dir, os.path.basename(src))
        
        try:
            shutil.move(src, dst)
            moved_files.append(info['filename'])
            print(f"  📦 已移动: {info['filename']} → backup/")
        except Exception as e:
            print(f"  ❌ 移动失败 {info['filename']}: {str(e)}")
    
    # 清理对应的CSV文件
    csv_files = glob.glob('output/crawl_data/meituan_*.csv')
    for csv_file in csv_files:
        csv_name = os.path.basename(csv_file)
        # 检查是否有对应的JSON测试文件被清理
        json_name = csv_name.replace('.csv', '.json')
        if json_name in moved_files:
            try:
                dst = os.path.join(backup_dir, csv_name)
                shutil.move(csv_file, dst)
                print(f"  📦 已移动CSV: {csv_name} → backup/")
            except Exception as e:
                print(f"  ❌ 移动CSV失败 {csv_name}: {str(e)}")
    
    print(f"\n✅ 清理完成: 移动了 {len(moved_files)} 个测试文件到 backup/ 目录")
    
    # 显示剩余文件
    remaining_json = glob.glob('output/crawl_data/meituan_*.json')
    remaining_csv = glob.glob('output/crawl_data/meituan_*.csv')
    
    print(f"\n📁 剩余文件:")
    print(f"  JSON文件: {len(remaining_json)}个")
    for f in remaining_json:
        print(f"    ✅ {os.path.basename(f)}")
    print(f"  CSV文件: {len(remaining_csv)}个")
    for f in remaining_csv:
        print(f"    ✅ {os.path.basename(f)}")

def create_data_summary(complete_files):
    """创建数据总结报告"""
    if not complete_files:
        return
    
    print("\n" + "=" * 60)
    print("📋 数据总结报告")
    print("=" * 60)
    
    # 使用最新的完整文件
    latest_file = max(complete_files, key=lambda x: x['mtime'])
    
    with open(latest_file['filepath'], 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    positions = data.get('positions', [])
    
    print(f"📊 数据来源: {latest_file['filename']}")
    print(f"📅 爬取时间: {data.get('crawl_time', '未知')}")
    print(f"🏙️ 城市: {data.get('city_name', '未知')}")
    print(f"📁 筛选类别: {', '.join(data.get('categories', []))}")
    print(f"📡 API地址: {data.get('api_url', '未知')}")
    
    print(f"\n📈 数据统计:")
    print(f"  总岗位数: {len(positions)}")
    
    # 类别分布
    categories = {}
    for pos in positions:
        category = pos.get('position_category', '未知')
        categories[category] = categories.get(category, 0) + 1
    
    print(f"\n🎯 岗位类别分布:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(positions) * 100
        print(f"  {category}: {count}个 ({percentage:.1f}%)")
    
    # 字段完整性
    required_fields = ['position_id', 'position_name', 'work_location', 'position_category',
                      'publish_time', 'detail_url', 'department', 'education_requirement',
                      'work_experience', 'job_responsibilities', 'job_requirements',
                      'salary_range', 'high_light']
    
    field_stats = {}
    for field in required_fields:
        count = sum(1 for pos in positions if pos.get(field))
        field_stats[field] = count
    
    print(f"\n📋 字段完整性:")
    for field, count in field_stats.items():
        percentage = count / len(positions) * 100
        status = "✅" if percentage > 90 else "⚠️" if percentage > 50 else "❌"
        print(f"  {status} {field}: {count}/{len(positions)} ({percentage:.1f}%)")
    
    # 保存总结报告
    summary_file = 'output/crawl_data/data_summary.md'
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# 美团招聘数据总结报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**数据文件**: {latest_file['filename']}\n")
        f.write(f"**爬取时间**: {data.get('crawl_time', '未知')}\n")
        f.write(f"**总岗位数**: {len(positions)}\n\n")
        
        f.write("## 数据概览\n\n")
        f.write(f"- **城市**: {data.get('city_name', '未知')}\n")
        f.write(f"- **筛选类别**: {', '.join(data.get('categories', []))}\n")
        f.write(f"- **API地址**: {data.get('api_url', '未知')}\n\n")
        
        f.write("## 岗位类别分布\n\n")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            percentage = count / len(positions) * 100
            f.write(f"- {category}: {count}个 ({percentage:.1f}%)\n")
        
        f.write("\n## 字段完整性\n\n")
        for field, count in field_stats.items():
            percentage = count / len(positions) * 100
            f.write(f"- {field}: {count}/{len(positions)} ({percentage:.1f}%)\n")
    
    print(f"\n💾 总结报告已保存: {summary_file}")

def main():
    """主函数"""
    print("🚀 美团招聘数据文件管理工具")
    print("按照夸克规范：管理数据文件，确保数据完整性")
    print("=" * 60)
    
    # 列出所有文件
    file_info = list_data_files()
    
    # 识别完整数据
    complete_files = identify_complete_data(file_info)
    
    # 清理测试文件
    cleanup_test_files(file_info, keep_latest=True)
    
    # 创建数据总结
    create_data_summary(complete_files)
    
    print("\n" + "=" * 60)
    print("🎯 按照夸克规范，数据管理完成")
    print("=" * 60)
    
    print("\n📁 最终文件结构:")
    print("output/crawl_data/")
    print("├── meituan_positions_20260522_001430.json  # ✅ 完整数据")
    print("├── meituan_positions_20260522_001430.csv   # ✅ CSV格式")
    print("├── high_light_analysis.json                # ✅ 亮点分析")
    print("├── data_summary.md                         # ✅ 数据总结")
    print("└── backup/                                 # 📦 测试文件备份")
    
    print("\n💡 建议:")
    print("1. 定期运行此工具管理数据文件")
    print("2. 备份重要数据文件")
    print("3. 验证数据完整性")
    print("4. 更新检查清单")

if __name__ == "__main__":
    main()