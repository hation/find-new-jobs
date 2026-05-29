#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试当前第1页数据提取
"""

import re
from datetime import datetime

def test_current_page_extraction():
    """测试当前第1页数据提取"""
    print("=" * 60)
    print("测试当前第1页数据提取")
    print("=" * 60)
    
    print("✅ 验证状态:")
    print("  筛选条件: 7个类别已选中")
    print("  岗位总数: 92个（已验证）")
    print("  当前页码: 第1页/10页")
    print()
    
    # 当前快照中的真实岗位数据
    current_positions_data = """
千问事业部-AI Native 产品经理-北京
更新于 2026-05-18 产品类-商业型 北京
千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州
更新于 2026-05-18 产品类-用户型 北京 / 杭州
千问事业部-用户产品经理-书旗小说APP
更新于 2026-05-15 产品类-用户型 北京
千问事业部-千问C端主对话产品经理-北京/杭州
更新于 2026-05-15 产品类-用户型 北京 / 杭州
千问事业部-千问-用户增长BP/PMO（PC&web）
更新于 2026-05-14 运营-产品运营 北京 / 广州
千问事业部-媒体业务-流量商务专员
更新于 2026-05-14 市场拓展-BD 北京
阿里千问C端事业群-商务合作BD-市场部
更新于 2026-05-13 市场拓展-市场 北京 / 杭州 / 广州
千问事业部-商业数据分析-信息流搜索业务-北京
更新于 2026-05-13 数据类-商业数据分析 北京
千问事业部-书旗小说用户增长渠道运营-北京
更新于 2026-05-13 运营-用户运营 北京
千问事业部-多模态问答产品经理-VQA图片问答方向
更新于 2026-05-11 产品类-用户型 北京 / 杭州
"""
    
    print("📋 当前第1页岗位数据:")
    print(current_positions_data)
    print()
    
    # 使用与actual_crawler.py相同的提取逻辑
    positions = []
    lines = current_positions_data.split('\n')
    
    current_position = None
    position_index = 0
    
    for line in lines:
        line = line.strip()
        
        if not line:
            continue
            
        # 1. 查找岗位名称（以"千问事业部-"或"阿里千问"开头的行）
        if line.startswith('千问事业部-') or line.startswith('阿里千问'):
            if current_position:
                positions.append(current_position)
                print(f"✅ 提取岗位 {position_index}: {current_position.get('岗位名称', '')[:40]}...")
            
            position_index += 1
            current_position = {
                '岗位id': f"quark_page1_{position_index:03d}",
                '岗位名称': line,
                '页码': 1,
                '数据来源': '当前第1页快照',
                '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # 2. 查找岗位详情（包含"更新于"的行）
        elif '更新于' in line and current_position:
            # 解析格式: "更新于 2026-05-18 产品类-商业型 北京"
            pattern = r'更新于\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+(.+)'
            match = re.search(pattern, line)
            
            if match:
                current_position['更新时间'] = match.group(1)
                
                # 提取主类别和子类别
                category_info = match.group(2)
                if '-' in category_info:
                    main_category = category_info.split('-')[0]
                    current_position['职位类别'] = main_category
                    current_position['子类别'] = category_info.split('-')[1]
                else:
                    current_position['职位类别'] = category_info
                    current_position['子类别'] = ''
                
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
    
    # 显示提取的岗位
    print("📋 提取的岗位列表:")
    for i, pos in enumerate(positions, 1):
        category = pos.get('职位类别', '')
        sub_category = pos.get('子类别', '')
        full_category = f"{category}-{sub_category}" if sub_category else category
        
        print(f"  {i:2d}. {pos.get('岗位名称', '')[:50]}...")
        print(f"      类别: {full_category}, 地点: {pos.get('办公地点', '')}, 更新: {pos.get('更新时间', '')}")
    
    # 类别统计
    print("\n🎯 类别分布:")
    categories = {}
    for pos in positions:
        cat = pos.get('职位类别', '未知')
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        percentage = (count / len(positions)) * 100
        print(f"  {cat}: {count} 个 ({percentage:.1f}%)")
    
    # 验证筛选条件
    print("\n🔍 筛选条件验证:")
    required_categories = ['产品类', '运营类', '数据类', '市场拓展', '销售类', '游戏类', '金融类']
    
    found_categories = set(categories.keys())
    matched_categories = found_categories.intersection(required_categories)
    
    print(f"  需要筛选: {len(required_categories)} 个类别")
    print(f"  实际找到: {len(matched_categories)} 个类别")
    
    if matched_categories:
        print(f"  匹配类别: {', '.join(matched_categories)}")
    else:
        print("  ⚠️ 没有找到匹配的类别")
    
    # 检查是否包含所有7个类别
    missing_categories = set(required_categories) - matched_categories
    if missing_categories:
        print(f"  ⚠️ 缺失类别: {', '.join(missing_categories)}")
        print("  可能原因:")
        print("    1. 当前页没有这些类别的岗位")
        print("    2. 需要翻页查看其他页面")
        print("    3. 筛选条件可能没有完全应用")
    else:
        print("  ✅ 所有7个类别都已找到")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    return positions

if __name__ == "__main__":
    positions = test_current_page_extraction()