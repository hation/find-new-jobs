#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美团招聘岗位亮点分析工具
分析high_light字段内容，提取关键信息
"""

import json
import re
from collections import Counter
from typing import List, Dict, Any
import os

def load_latest_data() -> List[Dict[str, Any]]:
    """加载最新的数据文件"""
    import glob
    
    data_files = glob.glob('output/crawl_data/meituan_positions_*.json')
    if not data_files:
        print('❌ 没有找到数据文件')
        return []
    
    latest_file = max(data_files, key=os.path.getctime)
    print(f'📊 加载数据文件: {os.path.basename(latest_file)}')
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    positions = data.get('positions', [])
    print(f'📋 总岗位数: {len(positions)}')
    return positions

def analyze_high_light_content(positions: List[Dict[str, Any]]):
    """分析岗位亮点内容"""
    
    print("\n" + "=" * 60)
    print("🌟 岗位亮点分析报告")
    print("=" * 60)
    
    # 统计有亮点的岗位数量
    positions_with_high_light = [p for p in positions if p.get('high_light') and p['high_light'] != '无']
    print(f'📊 有岗位亮点的岗位: {len(positions_with_high_light)}/{len(positions)} ({len(positions_with_high_light)/len(positions)*100:.1f}%)')
    
    if not positions_with_high_light:
        print("⚠️ 没有找到岗位亮点数据")
        return
    
    # 分析亮点内容模式
    print("\n🔍 亮点内容模式分析:")
    
    # 常见关键词
    keywords = Counter()
    common_patterns = {
        '新业务': ['新业务', '新项目', '从0到1', '从0-1', '初创', '创业'],
        '国际化': ['国际化', '海外', '全球', '英文环境', '多国'],
        '成长空间': ['成长空间', '发展空间', '学习机会', '晋升通道', '职业发展'],
        '团队氛围': ['团队氛围', '氛围好', '扁平化', '简单', '务实'],
        '业务规模': ['万亿', '千亿', '大盘', '规模', '市场空间'],
        '技术挑战': ['技术挑战', '复杂业务', '高并发', '大数据', '算法'],
        '福利待遇': ['福利', '待遇', '薪资', '奖金', '股票']
    }
    
    for position in positions_with_high_light:
        high_light = position['high_light']
        
        # 按行分析
        lines = high_light.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查常见模式
            for pattern_name, pattern_keywords in common_patterns.items():
                for keyword in pattern_keywords:
                    if keyword in line:
                        keywords[pattern_name] += 1
                        break
    
    print("\n🏆 亮点关键词统计:")
    for keyword, count in keywords.most_common():
        print(f'  {keyword}: {count}次')
    
    # 分析亮点结构
    print("\n📋 亮点结构分析:")
    sample_high_lights = []
    for position in positions_with_high_light[:5]:  # 分析前5个
        high_light = position['high_light']
        lines = [line.strip() for line in high_light.split('\n') if line.strip()]
        
        print(f'\n  📝 岗位: {position.get("position_name", "未知")}')
        print(f'    部门: {position.get("department", "未知")}')
        print(f'    亮点行数: {len(lines)}行')
        
        # 分析每行内容
        for i, line in enumerate(lines[:3], 1):  # 只显示前3行
            print(f'    第{i}行: {line[:50]}...' if len(line) > 50 else f'    第{i}行: {line}')
        
        sample_high_lights.append({
            'position': position.get('position_name'),
            'department': position.get('department'),
            'high_light': high_light[:200] + '...' if len(high_light) > 200 else high_light
        })
    
    return {
        'total_positions': len(positions),
        'positions_with_high_light': len(positions_with_high_light),
        'keyword_stats': dict(keywords),
        'samples': sample_high_lights
    }

def extract_business_insights(positions: List[Dict[str, Any]]):
    """从亮点中提取业务洞察"""
    
    print("\n" + "=" * 60)
    print("💡 业务洞察提取")
    print("=" * 60)
    
    positions_with_high_light = [p for p in positions if p.get('high_light') and p['high_light'] != '无']
    
    if not positions_with_high_light:
        return
    
    # 按部门分析
    department_insights = {}
    for position in positions_with_high_light:
        dept = position.get('department', '未知部门')
        high_light = position['high_light']
        
        if dept not in department_insights:
            department_insights[dept] = {
                'count': 0,
                'high_lights': [],
                'keywords': Counter()
            }
        
        department_insights[dept]['count'] += 1
        department_insights[dept]['high_lights'].append(high_light[:100])
        
        # 提取关键词
        words = re.findall(r'【(.*?)】|（(.*?)）|「(.*?)」', high_light)
        for word_group in words:
            for word in word_group:
                if word:
                    department_insights[dept]['keywords'][word] += 1
    
    print("\n🏢 部门亮点分析:")
    for dept, insights in sorted(department_insights.items(), key=lambda x: x[1]['count'], reverse=True)[:10]:
        print(f'\n  📍 {dept}: {insights["count"]}个岗位')
        
        # 显示热门关键词
        top_keywords = insights['keywords'].most_common(3)
        if top_keywords:
            print(f'    热门关键词: {", ".join([k for k, _ in top_keywords])}')
        
        # 显示一个示例
        if insights['high_lights']:
            print(f'    示例亮点: {insights["high_lights"][0]}...')

def create_high_light_summary(positions: List[Dict[str, Any]]):
    """创建亮点总结报告"""
    
    print("\n" + "=" * 60)
    print("📋 岗位亮点总结报告")
    print("=" * 60)
    
    # 收集所有亮点
    all_high_lights = []
    for position in positions:
        if position.get('high_light') and position['high_light'] != '无':
            all_high_lights.append({
                'position': position.get('position_name'),
                'department': position.get('department'),
                'category': position.get('position_category'),
                'high_light': position['high_light']
            })
    
    if not all_high_lights:
        print("⚠️ 没有岗位亮点数据")
        return
    
    # 按类别统计
    category_stats = {}
    for item in all_high_lights:
        category = item['category']
        if category not in category_stats:
            category_stats[category] = 0
        category_stats[category] += 1
    
    print("\n📊 亮点分布:")
    for category, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(all_high_lights) * 100
        print(f'  {category}: {count}个 ({percentage:.1f}%)')
    
    # 亮点长度分析
    lengths = [len(item['high_light']) for item in all_high_lights]
    avg_length = sum(lengths) / len(lengths)
    
    print(f'\n📏 亮点长度分析:')
    print(f'  平均长度: {avg_length:.0f}字符')
    print(f'  最长: {max(lengths)}字符')
    print(f'  最短: {min(lengths)}字符')
    
    # 保存详细报告
    report_file = 'output/crawl_data/high_light_analysis.json'
    report_data = {
        'analysis_time': '2026-05-22 00:26',
        'total_positions': len(positions),
        'positions_with_high_light': len(all_high_lights),
        'category_stats': category_stats,
        'sample_high_lights': all_high_lights[:10]  # 保存前10个作为示例
    }
    
    os.makedirs('output/crawl_data', exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print(f'\n💾 详细报告已保存: {report_file}')

def main():
    """主函数"""
    print("🚀 美团招聘岗位亮点分析工具")
    print("按照夸克规范：深度分析数据价值")
    print("=" * 60)
    
    # 加载数据
    positions = load_latest_data()
    if not positions:
        return
    
    # 分析亮点内容
    analysis_result = analyze_high_light_content(positions)
    
    # 提取业务洞察
    extract_business_insights(positions)
    
    # 创建总结报告
    create_high_light_summary(positions)
    
    print("\n" + "=" * 60)
    print("🎯 按照夸克规范，下一步行动:")
    print("=" * 60)
    
    print("\n1. 🔄 重新爬取数据（包含high_light字段）")
    print("2. 📊 更新数据质量报告")
    print("3. 🔍 验证筛选条件问题")
    print("4. 📋 更新检查清单")
    
    print("\n💡 high_light字段的价值:")
    print("  • 了解业务发展方向")
    print("  • 分析团队文化和氛围")
    print("  • 发现职业发展机会")
    print("  • 洞察公司战略重点")

if __name__ == "__main__":
    main()