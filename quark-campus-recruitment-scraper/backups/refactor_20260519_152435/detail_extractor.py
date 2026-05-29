#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
岗位详情页数据提取工具
"""

import re
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json

def log_info(msg: str):
    """记录信息"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] {msg}")

def extract_position_id_from_url(url: str) -> Optional[str]:
    """
    从详情页URL精确提取positionId
    
    Args:
        url: 岗位详情页URL
        
    Returns:
        positionId字符串，如果未找到则返回None
    """
    pattern = r'positionId=([^&]+)'
    match = re.search(pattern, url)
    
    if match:
        position_id = match.group(1)
        log_info(f"从URL提取positionId: {position_id}")
        return position_id
    
    log_info(f"未找到positionId: {url}")
    return None

def analyze_detail_page_structure(snapshot_text: str) -> Dict[str, Any]:
    """
    分析详情页结构，识别各个字段的位置
    
    Args:
        snapshot_text: 详情页快照文本
        
    Returns:
        页面结构分析结果
    """
    lines = snapshot_text.split('\n')
    
    structure = {
        '岗位id': None,
        '岗位详情链接': None,
        '所属部门': None,
        '学历': None,
        '工作年限': None,
        '职位描述': None,
        '职位要求': None,
        '其他字段': []
    }
    
    # 查找关键字段的模式
    patterns = {
        '学历': [r'学历[:：]\s*([^\n]+)', r'教育背景[:：]\s*([^\n]+)', r'学历要求[:：]\s*([^\n]+)'],
        '工作年限': [r'工作年限[:：]\s*([^\n]+)', r'经验要求[:：]\s*([^\n]+)', r'经验[:：]\s*([^\n]+)'],
        '所属部门': [r'部门[:：]\s*([^\n]+)', r'事业部[:：]\s*([^\n]+)', r'所属部门[:：]\s*([^\n]+)']
    }
    
    for line in lines:
        line = line.strip()
        
        # 跳过空行
        if not line:
            continue
        
        # 检查各个字段
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, line)
                if match:
                    structure[field] = match.group(1).strip()
                    log_info(f"找到{field}: {structure[field]}")
                    break
        
        # 查找职位描述（通常有特定标识）
        if '职位描述' in line or '岗位职责' in line or '工作内容' in line:
            structure['职位描述'] = '待提取详细内容'
            log_info("找到职位描述区域")
        
        # 查找职位要求（通常有特定标识）
        if '职位要求' in line or '任职要求' in line or '技能要求' in line:
            structure['职位要求'] = '待提取详细内容'
            log_info("找到职位要求区域")
    
    return structure

def extract_detail_fields(snapshot_text: str, detail_url: str) -> Dict[str, Any]:
    """
    从详情页快照中精确提取字段
    
    Args:
        snapshot_text: 详情页快照文本
        detail_url: 详情页URL
        
    Returns:
        提取的字段数据
    """
    log_info("开始提取详情页字段...")
    
    # 1. 从URL提取positionId
    position_id = extract_position_id_from_url(detail_url)
    
    # 2. 分析页面结构
    structure = analyze_detail_page_structure(snapshot_text)
    
    # 3. 提取详细内容
    result = {
        '岗位id': position_id,
        '岗位详情链接': detail_url,
        '所属部门': structure['所属部门'] or '待提取',
        '学历': structure['学历'] or '待提取',
        '工作年限': structure['工作年限'] or '待提取',
        '职位描述': structure['职位描述'] or '待提取',
        '职位要求': structure['职位要求'] or '待提取',
        '提取时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '数据来源': '岗位详情页实际数据'
    }
    
    # 4. 如果找到字段但内容是"待提取详细内容"，则提取实际内容
    lines = snapshot_text.split('\n')
    
    if result['职位描述'] == '待提取详细内容':
        result['职位描述'] = extract_multiline_content(lines, ['职位描述', '岗位职责', '工作内容'])
    
    if result['职位要求'] == '待提取详细内容':
        result['职位要求'] = extract_multiline_content(lines, ['职位要求', '任职要求', '技能要求'])
    
    log_info(f"详情页字段提取完成: {len([v for v in result.values() if v != '待提取'])}/7 个字段")
    
    return result

def extract_multiline_content(lines: list, start_keywords: list) -> str:
    """
    提取多行内容（如职位描述、职位要求）
    
    Args:
        lines: 文本行列表
        start_keywords: 开始关键词列表
        
    Returns:
        提取的多行内容
    """
    content_lines = []
    in_content = False
    content_end_keywords = ['职位要求', '任职要求', '技能要求', '福利待遇', '联系方式', '工作地点']
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 检查是否开始提取
        if not in_content:
            for keyword in start_keywords:
                if keyword in line:
                    in_content = True
                    # 去掉关键词本身
                    line = line.split(keyword)[-1].strip(' :：')
                    if line:
                        content_lines.append(line)
                    break
        
        # 如果正在提取内容
        elif in_content:
            # 检查是否到达内容结束
            should_end = False
            for end_keyword in content_end_keywords:
                if end_keyword in line and end_keyword not in start_keywords:
                    should_end = True
                    break
            
            if should_end and line and not any(kw in line for kw in start_keywords):
                break
            
            # 添加内容行（跳过空行或过短的行）
            if line and len(line) > 2:
                content_lines.append(line)
    
    # 清理内容
    if content_lines:
        # 合并连续行
        content = ' '.join(content_lines)
        # 去除多余空格
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    
    return '待提取'

def test_detail_extraction():
    """
    测试详情页提取功能
    """
    print("=" * 60)
    print("详情页提取功能测试")
    print("=" * 60)
    
    # 测试URL解析
    test_url = "https://talent.quark.cn/off-campus/position-detail?lang=zh&positionId=100007500014&track_id=SSP1779088808364ptNkSlnjmv9241"
    position_id = extract_position_id_from_url(test_url)
    print(f"✅ URL解析测试: {position_id}")
    
    # 测试模拟的详情页内容
    mock_detail_page = """
职位详情
岗位名称: 千问事业部-C端用户产品-网盘相册方向
部门: 千问事业部-产品部
学历: 本科及以上
工作年限: 3-5年

职位描述:
1. 负责网盘相册产品的用户增长和产品优化
2. 分析用户需求，制定产品迭代计划
3. 协调设计、开发、测试资源，推动产品上线

职位要求:
1. 本科及以上学历，计算机相关专业优先
2. 3年以上互联网产品经验
3. 熟悉用户体验设计，有数据驱动思维

福利待遇:
- 五险一金
- 年度体检
- 带薪年假
"""
    
    result = extract_detail_fields(mock_detail_page, test_url)
    
    print("\n📋 提取结果:")
    for field, value in result.items():
        if field not in ['提取时间', '数据来源']:
            status = "✅" if value != '待提取' else "❌"
            print(f"  {status} {field}: {value[:50]}..." if len(str(value)) > 50 else f"  {status} {field}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    test_detail_extraction()