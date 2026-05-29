#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用实际浏览器快照测试提取逻辑
"""

import re
from datetime import datetime
import os

def extract_from_actual_snapshot():
    """从实际快照中提取"""
    print("=" * 60)
    print("使用实际浏览器快照测试")
    print("=" * 60)
    
    # 实际快照内容（基于刚才获取的快照）
    actual_snapshot = """
千问事业部-AI Native 产品经理-北京
更新于 2026-05-18 产品类-商业型 北京
千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州
更新于 2026-05-18 产品类-用户型 北京 / 杭州
千问事业部-语音大模型高级开发工程师-杭州/广州
更新于 2026-05-17 技术类-开发 杭州 / 广州
千问事业部-MOS 实验室-Agent Harness专家-北京/杭州/广州
更新于 2026-05-16 技术类-开发 北京 / 杭州 / 广州
千问事业部-MOS 实验室-数据科学家-千问C端场景-杭州
更新于 2026-05-16 技术类-算法 杭州
千问事业部-MOS 实验室-AI搜索算法专家-杭州/北京
更新于 2026-05-16 技术类-算法 北京 / 杭州
千问事业部-MOS 实验室-AI Agent 算法专家（任务助理方向）-北京/杭州/广州
更新于 2026-05-16 技术类-算法 北京 / 杭州 / 广州
千问事业部-MOS 实验室-推荐/推送算法专家（大模型方向）-杭州/北京/广州
更新于 2026-05-16 技术类-算法 北京 / 杭州 / 广州
千问事业部-用户产品经理-书旗小说APP
更新于 2026-05-15 产品类-用户型 北京
千问事业部-千问 APP-BU财务
更新于 2026-05-15 综合类-财务及内控 杭州 / 广州
"""
    
    print("📋 实际快照内容（前500字符）:")
    print(actual_snapshot[:500])
    print("...")
    print()
    
    # 使用与actual_crawler.py相同的提取逻辑
    positions = []
    lines = actual_snapshot.split('\n')
    
    current_position = None
    position_index = 0
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
            
        # 1. 查找岗位名称（以"千问事业部-"开头的行）
        if line.startswith('千问事业部-'):
            if current_position:
                positions.append(current_position)
                print(f"✅ 提取岗位 {position_index}: {current_position.get('岗位名称', '')[:40]}...")
            
            position_index += 1
            current_position = {
                '岗位id': f"quark_actual_{position_index:04d}",
                '岗位名称': line,
                '数据来源': '实际浏览器快照',
                '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                '页码': 1  # 第1页
            }
        
        # 2. 查找岗位详情（包含"更新于"的行）
        elif '更新于' in line and current_position:
            # 解析格式: "更新于 2026-05-18 产品类-商业型 北京"
            pattern = r'更新于\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+(.+)'
            match = re.search(pattern, line)
            
            if match:
                current_position['更新时间'] = match.group(1)
                
                # 提取主类别
                category_info = match.group(2)
                if '-' in category_info:
                    main_category = category_info.split('-')[0]
                    current_position['职位类别'] = main_category
                    current_position['子类别'] = category_info.split('-')[1]
                else:
                    current_position['职位类别'] = category_info
                
                # 提取办公地点
                location = match.group(3)
                locations = [loc.strip() for loc in location.split('/')]
                current_position['办公地点'] = ' / '.join(locations)
                
                # 从类别推断部门
                if '产品' in current_position['职位类别']:
                    current_position['所属部门'] = '产品部'
                elif '运营' in current_position['职位类别']:
                    current_position['所属部门'] = '运营部'
                elif '数据' in current_position['职位类别']:
                    current_position['所属部门'] = '数据部'
                elif '市场' in current_position['职位类别']:
                    current_position['所属部门'] = '市场部'
                elif '销售' in current_position['职位类别']:
                    current_position['所属部门'] = '销售部'
                elif '游戏' in current_position['职位类别']:
                    current_position['所属部门'] = '游戏部'
                elif '金融' in current_position['职位类别']:
                    current_position['所属部门'] = '金融部'
                else:
                    current_position['所属部门'] = '千问事业部'
    
    # 添加最后一个岗位
    if current_position:
        positions.append(current_position)
        print(f"✅ 提取岗位 {position_index}: {current_position.get('岗位名称', '')[:40]}...")
    
    print(f"\n📊 提取结果: {len(positions)} 个岗位")
    print()
    
    # 验证筛选条件
    print("🔍 筛选条件验证:")
    print("  当前页面: 第1页")
    print("  筛选类别: 7个类别（产品、运营、数据、市场拓展、销售、游戏、金融）")
    print(f"  提取岗位: {len(positions)} 个")
    print(f"  目标总数: 92个岗位（第1页10个）")
    print()
    
    # 检查提取的岗位是否符合筛选条件
    filtered_positions = []
    required_categories = ['产品类', '运营类', '数据类', '市场拓展', '销售类', '游戏类', '金融类']
    
    for pos in positions:
        category = pos.get('职位类别', '')
        if category in required_categories:
            filtered_positions.append(pos)
    
    print("🎯 符合筛选条件的岗位:")
    if filtered_positions:
        for i, pos in enumerate(filtered_positions, 1):
            print(f"  {i:2d}. {pos.get('岗位名称', '')[:50]}...")
            print(f"      类别: {pos.get('职位类别', '')}")
    else:
        print("  ⚠️ 没有找到符合筛选条件的岗位")
        print("  可能原因:")
        print("    1. 页面没有应用筛选条件")
        print("    2. 当前页面数据不包含这些类别")
        print("    3. 需要重新检查筛选条件")
    
    print(f"\n📈 统计:")
    print(f"  总提取岗位: {len(positions)}")
    print(f"  符合筛选条件: {len(filtered_positions)}")
    
    # 类别统计
    categories = {}
    for pos in positions:
        cat = pos.get('职位类别', '未知')
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 类别分布:")
    for cat, count in sorted(categories.items()):
        percentage = (count / len(positions)) * 100 if positions else 0
        print(f"  {cat}: {count} 个 ({percentage:.1f}%)")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    return positions, filtered_positions

if __name__ == "__main__":
    all_positions, filtered_positions = extract_from_actual_snapshot()