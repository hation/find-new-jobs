#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证模块
验证爬取数据的完整性和质量
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DataValidator:
    """数据验证器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据验证器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.validation_config = config.get('validation', {})
        self.rules = self.validation_config.get('rules', {})
        self.strict_mode = self.validation_config.get('strict_mode', False)
        
    def validate_position(self, position_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证单个岗位数据
        
        Args:
            position_data: 岗位数据字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必填字段
        required_fields = self.config.get('scraper', {}).get('fields', {}).get('required', [])
        for field in required_fields:
            if field not in position_data or not position_data[field]:
                errors.append(f"缺少必填字段: {field}")
            elif not self._validate_field(field, position_data[field]):
                errors.append(f"字段验证失败: {field}")
        
        # 检查数据质量
        if '岗位名称' in position_data:
            if len(position_data['岗位名称']) < 2:
                errors.append("岗位名称太短")
            if len(position_data['岗位名称']) > 100:
                errors.append("岗位名称太长")
        
        if '办公地点' in position_data:
            if len(position_data['办公地点']) < 2:
                errors.append("办公地点太短")
        
        if '职位描述' in position_data:
            if len(position_data['职位描述']) < 10:
                errors.append("职位描述太短")
        
        # 检查更新时间格式
        if '更新时间' in position_data and position_data['更新时间']:
            if not self._validate_date_format(position_data['更新时间']):
                errors.append("更新时间格式不正确")
        
        # 检查工作年限格式
        if '工作年限' in position_data and position_data['工作年限']:
            if not self._validate_experience_format(position_data['工作年限']):
                errors.append("工作年限格式不正确")
        
        # 在严格模式下，任何错误都导致验证失败
        if self.strict_mode and errors:
            return False, errors
        
        # 在非严格模式下，只有关键错误才导致失败
        critical_errors = [e for e in errors if "必填字段" in e]
        if critical_errors:
            return False, critical_errors
        
        return len(errors) == 0, errors
    
    def _validate_field(self, field_name: str, value: Any) -> bool:
        """
        验证单个字段
        
        Args:
            field_name: 字段名
            value: 字段值
            
        Returns:
            是否有效
        """
        if field_name not in self.rules:
            return True  # 没有验证规则，默认通过
        
        rule = self.rules[field_name]
        
        # 检查必填
        if rule.get('required', False) and (value is None or value == ''):
            return False
        
        # 检查最小长度
        if 'min_length' in rule and isinstance(value, str):
            if len(value) < rule['min_length']:
                return False
        
        # 检查最大长度
        if 'max_length' in rule and isinstance(value, str):
            if len(value) > rule['max_length']:
                return False
        
        # 检查正则表达式
        if 'pattern' in rule and isinstance(value, str):
            if not re.match(rule['pattern'], value):
                return False
        
        return True
    
    def _validate_date_format(self, date_str: str) -> bool:
        """
        验证日期格式
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否有效日期格式
        """
        # 常见的日期格式
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
            r'\d{4}年\d{2}月\d{2}日',  # 中文日期
            r'\d{2}-\d{2}',  # MM-DD (可能缺少年份)
            r'\d{1,2}月\d{1,2}日',  # 中文月日
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, date_str):
                return True
        
        # 尝试解析相对时间（如"3天前"、"刚刚"等）
        relative_patterns = [
            r'刚刚',
            r'\d+分钟前',
            r'\d+小时前',
            r'\d+天前',
            r'\d+周前',
            r'\d+月前',
            r'\d+年前',
        ]
        
        for pattern in relative_patterns:
            if re.search(pattern, date_str):
                return True
        
        return False
    
    def _validate_experience_format(self, experience_str: str) -> bool:
        """
        验证工作年限格式
        
        Args:
            experience_str: 工作年限字符串
            
        Returns:
            是否有效工作年限格式
        """
        # 常见的工作年限格式
        experience_patterns = [
            r'不限',
            r'应届生',
            r'在校生',
            r'\d+年以内',
            r'\d+-\d+年',
            r'\d+年及以上',
            r'\d+年以上',
            r'\d+年',
            r'经验不限',
        ]
        
        for pattern in experience_patterns:
            if re.search(pattern, experience_str):
                return True
        
        return False
    
    def clean_position_data(self, position_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗岗位数据
        
        Args:
            position_data: 原始岗位数据
            
        Returns:
            清洗后的岗位数据
        """
        cleaned = {}
        
        for key, value in position_data.items():
            if value is None:
                cleaned[key] = ''
            elif isinstance(value, str):
                # 去除首尾空白
                cleaned_value = value.strip()
                
                # 替换多个空白为单个空格
                cleaned_value = re.sub(r'\s+', ' ', cleaned_value)
                
                # 去除特殊字符（保留中文、英文、数字、常用标点）
                cleaned_value = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\-\.\,\，\。\！\？\；\：\「\」\《\》\（\）]', '', cleaned_value)
                
                cleaned[key] = cleaned_value
            else:
                cleaned[key] = value
        
        return cleaned
    
    def deduplicate_positions(self, positions: List[Dict[str, Any]], 
                             key_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        去重岗位数据
        
        Args:
            positions: 岗位数据列表
            key_fields: 用于去重的关键字段列表
            
        Returns:
            去重后的岗位数据列表
        """
        if key_fields is None:
            # 优先使用岗位ID进行去重，如果岗位ID不存在，则使用其他字段
            if any('岗位id' in position and position['岗位id'] for position in positions):
                key_fields = ['岗位id']
            else:
                key_fields = ['岗位名称', '办公地点', '所属部门', '岗位详情链接']
        
        seen = set()
        deduplicated = []
        duplicates_count = 0
        
        for position in positions:
            # 创建唯一标识键
            key_parts = []
            for field in key_fields:
                value = position.get(field, '')
                if isinstance(value, str):
                    key_parts.append(value.strip())
                else:
                    key_parts.append(str(value))
            
            key = '|'.join(key_parts)
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(position)
            else:
                duplicates_count += 1
                logger.warning(f"发现重复岗位: {key} - {position.get('岗位名称', '未知岗位')}")
        
        logger.info(f"去重前: {len(positions)} 个岗位, 去重后: {len(deduplicated)} 个岗位, 重复: {duplicates_count} 个")
        return deduplicated
    
    def validate_batch(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量验证岗位数据
        
        Args:
            positions: 岗位数据列表
            
        Returns:
            验证结果统计
        """
        total = len(positions)
        valid_count = 0
        invalid_count = 0
        all_errors = []
        
        for i, position in enumerate(positions):
            is_valid, errors = self.validate_position(position)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                position_errors = {
                    'index': i,
                    'position': position.get('岗位名称', f'未知岗位_{i}'),
                    'errors': errors
                }
                all_errors.append(position_errors)
                logger.warning(f"岗位验证失败 [{i}]: {position.get('岗位名称')} - {', '.join(errors)}")
        
        # 统计数据质量
        quality_score = valid_count / total if total > 0 else 0
        
        result = {
            'total_positions': total,
            'valid_positions': valid_count,
            'invalid_positions': invalid_count,
            'quality_score': quality_score,
            'errors': all_errors,
            'summary': f"验证完成: {valid_count}/{total} 个岗位有效 ({quality_score:.1%})"
        }
        
        logger.info(result['summary'])
        
        return result
    
    def format_for_excel(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        格式化数据用于Excel输出
        
        Args:
            positions: 岗位数据列表
            
        Returns:
            格式化后的数据列表
        """
        formatted = []
        
        # 定义Excel列顺序（更新后包含新字段）
        excel_columns = [
            '岗位id',          # 新增字段
            '岗位名称',
            '职位类别',
            '办公地点',
            '所属部门',
            '学历要求',
            '工作年限',
            '更新时间',
            '页码',           # 新增字段
            '职位描述',
            '职位要求',
            '岗位详情链接'    # 新增字段
        ]
        
        for position in positions:
            formatted_position = {}
            
            for column in excel_columns:
                value = position.get(column, '')
                
                # 确保值是字符串类型
                if value is None:
                    formatted_position[column] = ''
                else:
                    formatted_position[column] = str(value).strip()
            
            formatted.append(formatted_position)
        
        return formatted