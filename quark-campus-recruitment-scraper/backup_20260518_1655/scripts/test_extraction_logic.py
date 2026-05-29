#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据提取逻辑
"""

import re
from datetime import datetime

def test_extract_logic(snapshot_text: str):
    """测试提取逻辑"""
    print("=" * 60)
    print("测试数据提取逻辑")
    print("=" * 60)
    
    # 模拟快照内容（基于实际快照）
    test_snapshot = """
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
    
    print("📋 测试快照内容:")
    print(test_snapshot)
    print()
    
    # 使用actual_crawler.py中的提取逻辑
    positions = []
    lines = test_snapshot.split('\n')
    
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
                '岗位id': f"quark_test_{position_index:04d}",
                '岗位名称': line,
                '数据来源': '测试数据',
                '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
    
    print("\n📊 提取结果统计:")
    print(f"  总提取岗位数: {len(positions)}")
    print()
    
    # 显示提取的岗位
    print("📋 提取的岗位列表:")
    for i, pos in enumerate(positions, 1):
        print(f"  {i:2d}. {pos.get('岗位名称', '')[:50]}...")
        print(f"      类别: {pos.get('职位类别', '')}, 地点: {pos.get('办公地点', '')}, 更新: {pos.get('更新时间', '')}")
    
    # 类别统计
    print("\n🎯 类别分布:")
    categories = {}
    for pos in positions:
        cat = pos.get('职位类别', '未知')
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        percentage = (count / len(positions)) * 100
        print(f"  {cat}: {count} 个 ({percentage:.1f}%)")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    return positions

if __name__ == "__main__":
    test_positions = test_extract_logic("")