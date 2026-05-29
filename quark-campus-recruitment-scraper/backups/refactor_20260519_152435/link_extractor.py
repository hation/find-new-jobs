#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位链接提取工具 - 从列表页提取岗位详情页链接
"""

import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def find_position_elements(snapshot_text: str) -> List[Dict[str, Any]]:
    """
    在快照中查找岗位元素
    
    Args:
        snapshot_text: 列表页快照文本
        
    Returns:
        岗位元素信息列表
    """
    position_elements = []
    lines = snapshot_text.split('\n')
    
    current_position = {}
    position_index = 0
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
        
        # 查找岗位名称行（以"千问事业部-"或"阿里千问"开头）
        if line.startswith('千问事业部-') or line.startswith('阿里千问') or line.startswith('千问事业群'):
            # 保存上一个岗位
            if current_position and '岗位名称' in current_position:
                position_elements.append(current_position)
            
            position_index += 1
            current_position = {
                'index': position_index,
                '岗位名称': line,
                '原始行': line,
                'ref': None,
                'clickable_ref': None,
                'row_ref': None
            }
        
        # 查找对应的row元素（包含"更新于"）
        elif '更新于' in line and current_position:
            # 提取ref信息
            ref_pattern = r'\[ref=([^\]]+)\]'
            match = re.search(ref_pattern, line)
            
            if match:
                ref_id = match.group(1)
                if 'row' in line.lower():
                    current_position['row_ref'] = ref_id
                else:
                    current_position['ref'] = ref_id
        
        # 查找可能的点击元素
        elif 'cursor=pointer' in line and current_position:
            # 可能是可点击的元素
            ref_pattern = r'\[ref=([^\]]+)\]'
            match = re.search(ref_pattern, line)
            
            if match:
                current_position['clickable_ref'] = match.group(1)
    
    # 添加最后一个岗位
    if current_position and '岗位名称' in current_position:
        position_elements.append(current_position)
    
    return position_elements

def analyze_clickable_elements(snapshot_text: str) -> List[Dict[str, Any]]:
    """
    分析页面中的可点击元素
    
    Args:
        snapshot_text: 页面快照文本
        
    Returns:
        可点击元素信息
    """
    clickable_elements = []
    lines = snapshot_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # 查找可点击元素（包含cursor=pointer）
        if 'cursor=pointer' in line:
            # 提取元素信息
            element_info = {
                '原始行': line[:100] + '...' if len(line) > 100 else line,
                'ref': None,
                'text': None,
                'type': None
            }
            
            # 提取ref
            ref_match = re.search(r'\[ref=([^\]]+)\]', line)
            if ref_match:
                element_info['ref'] = ref_match.group(1)
            
            # 提取文本内容
            text_match = re.search(r'"(.*?)"', line)
            if text_match:
                element_info['text'] = text_match.group(1)
            
            # 判断元素类型
            if 'button' in line.lower():
                element_info['type'] = 'button'
            elif 'text' in line.lower():
                element_info['type'] = 'text'
            elif 'link' in line.lower() or 'a href' in line.lower():
                element_info['type'] = 'link'
            else:
                element_info['type'] = 'unknown'
            
            clickable_elements.append(element_info)
    
    return clickable_elements

def match_positions_with_clickables(position_elements: List[Dict[str, Any]], 
                                   clickable_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    将岗位元素与可点击元素匹配
    
    Args:
        position_elements: 岗位元素列表
        clickable_elements: 可点击元素列表
        
    Returns:
        匹配后的岗位链接信息
    """
    matched_positions = []
    
    for position in position_elements:
        position_name = position['岗位名称']
        matched = False
        
        # 尝试匹配可点击元素
        for clickable in clickable_elements:
            clickable_text = clickable.get('text', '')
            
            # 如果可点击元素的文本包含岗位名称
            if clickable_text and position_name in clickable_text:
                position['matched_clickable'] = clickable
                position['click_target'] = clickable['ref']
                matched = True
                break
        
        # 如果没有找到精确匹配，尝试其他匹配策略
        if not matched:
            # 策略1: 使用row_ref作为点击目标
            if position.get('row_ref'):
                position['click_target'] = position['row_ref']
                position['match_strategy'] = 'row_ref'
                matched = True
            
            # 策略2: 使用岗位名称作为selector
            elif position_name:
                position['click_target'] = f"text='{position_name}'"
                position['match_strategy'] = 'text_selector'
                matched = True
        
        if matched:
            matched_positions.append(position)
        else:
            log_info(f"未找到岗位点击目标: {position_name[:30]}...")
    
    return matched_positions

def extract_position_links_from_snapshot(snapshot_text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    从列表页快照中提取岗位链接信息
    
    Args:
        snapshot_text: 列表页快照文本
        
    Returns:
        (岗位链接信息列表, 可点击元素信息列表)
    """
    log_info("开始提取岗位链接...")
    
    # 1. 查找岗位元素
    position_elements = find_position_elements(snapshot_text)
    log_info(f"找到 {len(position_elements)} 个岗位元素")
    
    # 2. 分析可点击元素
    clickable_elements = analyze_clickable_elements(snapshot_text)
    log_info(f"找到 {len(clickable_elements)} 个可点击元素")
    
    # 3. 匹配岗位与可点击元素
    matched_positions = match_positions_with_clickables(position_elements, clickable_elements)
    log_info(f"成功匹配 {len(matched_positions)} 个岗位")
    
    # 4. 整理岗位链接信息
    position_links = []
    
    for i, position in enumerate(matched_positions, 1):
        link_info = {
            '序号': i,
            '岗位名称': position['岗位名称'],
            '点击目标': position.get('click_target', '未找到'),
            '匹配策略': position.get('match_strategy', '未知'),
            'row_ref': position.get('row_ref'),
            'ref': position.get('ref'),
            'clickable_ref': position.get('clickable_ref'),
            '状态': '可点击' if position.get('click_target') else '不可点击'
        }
        
        if 'matched_clickable' in position:
            link_info['可点击元素类型'] = position['matched_clickable'].get('type')
        
        position_links.append(link_info)
    
    return position_links, clickable_elements

def test_link_extraction():
    """
    测试链接提取功能
    """
    print("=" * 60)
    print("岗位链接提取功能测试")
    print("=" * 60)
    
    # 使用一个示例快照文本
    example_snapshot = """
千问事业部-AI Native 产品经理-北京
更新于 2026-05-18 产品类-商业型 北京
千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州
更新于 2026-05-18 产品类-用户型 北京 / 杭州
千问事业部-用户产品经理-书旗小说APP
更新于 2026-05-15 产品类-用户型 北京
row "更新于 2026-05-15 产品类-用户型 北京" [ref=e57] [cursor=pointer]
text "千问事业部-千问C端主对话产品经理-北京/杭州" [ref=e58] [cursor=pointer]
button "下一页，当前第1页" [ref=e65] [cursor=pointer]
"""
    
    position_links, clickable_elements = extract_position_links_from_snapshot(example_snapshot)
    
    print(f"\n📋 岗位链接提取结果 ({len(position_links)} 个):")
    for link in position_links[:3]:  # 显示前3个
        print(f"  #{link['序号']} {link['岗位名称'][:40]}...")
        print(f"    点击目标: {link['点击目标']}")
        print(f"    匹配策略: {link['匹配策略']}")
        print(f"    状态: {link['状态']}")
    
    print(f"\n🔍 可点击元素分析 ({len(clickable_elements)} 个):")
    for elem in clickable_elements[:5]:  # 显示前5个
        print(f"  - {elem['type']}: {elem.get('text', '无文本')[:30]}...")
        print(f"    ref: {elem.get('ref', '无ref')}")
    
    print("\n💡 提取策略说明:")
    print("  1. 首先尝试匹配岗位名称与可点击元素文本")
    print("  2. 其次使用row_ref作为点击目标")
    print("  3. 最后使用岗位名称作为文本选择器")
    print("  4. 点击时会在新标签页打开详情页")
    
    print("\n⚠️  注意事项:")
    print("  1. 点击后需要切换到新标签页获取详情")
    print("  2. 需要处理多个标签页的切换")
    print("  3. 需要控制点击频率避免反爬")
    print("  4. 需要关闭详情页标签返回列表页")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    return position_links, clickable_elements

if __name__ == "__main__":
    test_link_extraction()