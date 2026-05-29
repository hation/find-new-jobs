#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据提取工具（基于anti-job和jd-job经验沉淀）
- 学历要求提取器
- 工作经验提取器
- 岗位标签生成器
- 时间格式化器
- 数据验证器

【核心功能】
1. 标准化数据提取：从不同格式的原始数据中提取标准字段
2. 智能清洗：自动清洗和格式化数据
3. 质量验证：确保数据质量符合要求
4. 错误恢复：优雅处理异常数据

【使用场景】
1. 数据清洗：清洗爬取的原始数据
2. 格式转换：转换不同数据源格式
3. 质量检查：验证数据完整性
4. 错误修复：修复常见数据问题
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    """数据提取器（通用工具）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化数据提取器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 学历关键词映射
        self.education_keywords = {
            "博士": "博士",
            "硕士": "硕士", 
            "研究生": "硕士",
            "本科": "本科",
            "学士": "本科",
            "大专": "大专",
            "专科": "大专",
            "高职": "大专",
            "高中": "高中",
            "中专": "中专",
            "中职": "中专",
            "初中": "初中",
            "小学": "小学"
        }
        
        # 工作经验关键词
        self.experience_keywords = {
            "不限": "经验不限",
            "无要求": "经验不限",
            "经验不限": "经验不限",
            "应届": "应届生",
            "实习": "实习生",
            "在校": "在校生"
        }
        
        logger.info("✅ 数据提取器初始化完成")
    
    def extract_education_level(self, text: str) -> str:
        """
        从文本中提取学历要求
        
        Args:
            text: 原始学历要求文本
            
        Returns:
            标准化的学历要求
        """
        if not text or pd.isna(text):
            return "学历不限"
        
        text = str(text).strip()
        
        # 检查是否包含关键词
        for keyword, level in self.education_keywords.items():
            if keyword in text:
                return level
        
        # 检查常见模式
        if any(word in text for word in ["不限", "无要求", "学历不限"]):
            return "学历不限"
        
        # 检查英文关键词
        english_keywords = {
            "phd": "博士",
            "doctor": "博士",
            "master": "硕士",
            "bachelor": "本科",
            "undergraduate": "本科",
            "college": "大专",
            "high school": "高中"
        }
        
        text_lower = text.lower()
        for keyword, level in english_keywords.items():
            if keyword in text_lower:
                return level
        
        return "学历不限"
    
    def extract_experience_range(self, text: str) -> str:
        """
        从文本中提取工作经验范围
        
        Args:
            text: 原始工作经验文本
            
        Returns:
            标准化的工作经验范围
        """
        if not text or pd.isna(text):
            return "经验不限"
        
        text = str(text).strip()
        
        # 检查关键词
        for keyword, value in self.experience_keywords.items():
            if keyword in text:
                return value
        
        # 匹配数字+年模式
        year_patterns = [
            r'(\d+)[\+-]?\s*年',           # 3年, 3+年, 3-5年
            r'(\d+)[\+-]?\s*years?',       # 3 years, 3+ years
            r'(\d+)[\+-]?\s*yr',           # 3 yr
            r'(\d+)\s*年以上',             # 3年以上
            r'(\d+)\s*年以下',             # 3年以下
            r'(\d+)\s*年以内',             # 3年以内
            r'(\d+)\s*年及以上',           # 3年及以上
            r'(\d+)\s*年及以下'            # 3年及以下
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # 如果是元组，取第一个元素
                    match = match[0]
                try:
                    years.append(int(match))
                except ValueError:
                    pass
        
        if years:
            if len(years) >= 2:
                # 如果有多个年份，取范围
                return f"{min(years)}-{max(years)}年"
            else:
                # 如果只有一个年份
                return f"{years[0]}+年"
        
        # 匹配"X年经验"模式
        experience_pattern = r'(\d+)\s*年\s*经验'
        match = re.search(experience_pattern, text)
        if match:
            try:
                years = int(match.group(1))
                return f"{years}+年"
            except ValueError:
                pass
        
        # 匹配"X年工作经历"模式
        work_pattern = r'(\d+)\s*年\s*工作'
        match = re.search(work_pattern, text)
        if match:
            try:
                years = int(match.group(1))
                return f"{years}+年"
            except ValueError:
                pass
        
        return "经验不限"
    
    def generate_position_tags(self, position: Dict[str, Any]) -> str:
        """
        生成岗位标签
        
        Args:
            position: 岗位数据
            
        Returns:
            标签字符串（逗号分隔）
        """
        tags = []
        
        # 从工作地点提取
        location = position.get("work_location") or position.get("location") or position.get("city")
        if location and str(location).strip() and str(location).strip().lower() != "nan":
            tags.append(str(location).strip())
        
        # 从部门提取
        department = position.get("department") or position.get("dept")
        if department and str(department).strip() and str(department).strip().lower() != "nan":
            tags.append(str(department).strip())
        
        # 从岗位类型提取
        job_type = position.get("job_type") or position.get("category") or position.get("type")
        if job_type and str(job_type).strip() and str(job_type).strip().lower() != "nan":
            tags.append(str(job_type).strip())
        
        # 检查是否热门
        is_hot = position.get("is_hot", 0)
        if is_hot in [1, "1", True, "true", "True"]:
            tags.append("热门岗位")
        
        # 检查是否紧急
        is_urgent = position.get("is_urgent", 0)
        if is_urgent in [1, "1", True, "true", "True"]:
            tags.append("紧急招聘")
        
        # 检查是否有薪资信息
        salary = position.get("salary") or position.get("salary_range")
        if salary and str(salary).strip() and str(salary).strip().lower() != "nan":
            tags.append("有薪资信息")
        
        # 去重并返回
        unique_tags = []
        for tag in tags:
            if tag and tag not in unique_tags:
                unique_tags.append(tag)
        
        return ", ".join(unique_tags) if unique_tags else ""
    
    def format_publish_time(self, time_str: str) -> str:
        """
        格式化发布时间
        
        Args:
            time_str: 原始时间字符串
            
        Returns:
            格式化后的时间字符串
        """
        if not time_str or pd.isna(time_str) or str(time_str).strip().lower() in ["nan", "none", "null", ""]:
            return "未知"
        
        time_str = str(time_str).strip()
        
        try:
            # 如果是时间戳（毫秒）
            if time_str.isdigit() and len(time_str) == 13:
                timestamp = int(time_str) / 1000
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # 如果是时间戳（秒）
            if time_str.isdigit() and len(time_str) == 10:
                timestamp = int(time_str)
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            
            # 尝试解析ISO格式
            try:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
            
            # 尝试解析常见格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y/%m/%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%Y年%m月%d日",
                "%Y.%m.%d"
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(time_str, fmt)
                    return dt.strftime("%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue
            
            # 如果都无法解析，返回原始字符串
            return time_str
            
        except Exception as e:
            logger.warning(f"格式化时间失败: {time_str}, 错误: {e}")
            return time_str
    
    def extract_field(self, data: Dict[str, Any], field_names: List[str], default: str = "") -> str:
        """
        从数据中提取字段（支持多个可能的字段名）
        
        Args:
            data: 数据字典
            field_names: 可能的字段名列表
            default: 默认值
            
        Returns:
            字段值（字符串）
        """
        for field_name in field_names:
            if field_name in data:
                value = data[field_name]
                if value is None or pd.isna(value):
                    continue
                
                str_value = str(value).strip()
                if str_value and str_value.lower() not in ["nan", "none", "null"]:
                    return str_value
        
        return default
    
    def validate_data_quality(self, data: List[Dict[str, Any]], required_fields: List[str] = None) -> Dict[str, Any]:
        """
        验证数据质量
        
        Args:
            data: 数据列表
            required_fields: 必填字段列表
            
        Returns:
            质量报告
        """
        if not data:
            return {
                "status": "失败",
                "message": "数据为空",
                "total_records": 0,
                "completeness": 0.0
            }
        
        required_fields = required_fields or ["position_id", "position_name", "work_location", "department"]
        
        total_records = len(data)
        valid_records = 0
        missing_fields_stats = {}
        
        for record in data:
            record_valid = True
            
            for field in required_fields:
                value = record.get(field)
                if value is None or pd.isna(value) or str(value).strip() == "":
                    record_valid = False
                    missing_fields_stats[field] = missing_fields_stats.get(field, 0) + 1
            
            if record_valid:
                valid_records += 1
        
        completeness = valid_records / total_records if total_records > 0 else 0.0
        
        return {
            "status": "通过" if completeness >= 0.8 else "警告" if completeness >= 0.5 else "失败",
            "message": f"数据完整率: {completeness * 100:.1f}%",
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": total_records - valid_records,
            "completeness": completeness,
            "completeness_percentage": f"{completeness * 100:.1f}%",
            "missing_fields": missing_fields_stats
        }
    
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        if not text or pd.isna(text):
            return ""
        
        text = str(text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊字符（保留中文、英文、数字、标点）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.,，。!！?？:：;；""\'\'()（）\[\]【】\-——]', '', text)
        
        # 标准化标点
        text = text.replace("，", ",")
        text = text.replace("。", ".")
        text = text.replace("！", "!")
        text = text.replace("？", "?")
        text = text.replace("：", ":")
        text = text.replace("；", ";")
        text = text.replace("（", "(")
        text = text.replace("）", ")")
        text = text.replace("【", "[")
        text = text.replace("】", "]")
        
        return text.strip()


# ==================== 使用示例 ====================

def demo_data_extractors():
    """演示数据提取工具的使用"""
    print("🚀 数据提取工具演示")
    print("=" * 50)
    
    # 创建数据提取器实例
    extractor = DataExtractor()
    
    # 示例数据
    sample_data = [
        {
            "position_id": "001",
            "position_name": "软件工程师",
            "work_location": "北京",
            "department": "技术部",
            "education_requirement": "本科及以上学历",
            "work_experience": "3-5年工作经验",
            "publish_date": "2026-05-20",
            "is_hot": 1
        },
        {
            "position_id": "002",
            "position_name": "产品经理",
            "work_location": "上海",
            "department": "产品部",
            "education_requirement": "硕士优先",
            "work_experience": "5年以上",
            "publish_date": "1779379200000",  # 时间戳
            "is_hot": 0
        },
        {
            "position_id": "003",
            "position_name": "数据分析师",
            "work_location": "深圳",
            "department": "数据部",
            "education_requirement": "学历不限",
            "work_experience": "经验不限",
            "publish_date": "2026/05/18"
        }
    ]
    
    print("📊 原始数据:")
    for i, data in enumerate(sample_data, 1):
        print(f"   {i}. {data['position_name']} - {data['work_location']}")
    
    print("\n🔄 数据提取和清洗:")
    
    for i, data in enumerate(sample_data, 1):
        print(f"\n   📝 岗位 {i}: {data['position_name']}")
        
        # 提取学历
        education = extractor.extract_education_level(data["education_requirement"])
        print(f"      学历要求: {data['education_requirement']} → {education}")
        
        # 提取经验
        experience = extractor.extract_experience_range(data["work_experience"])
        print(f"      工作经验: {data['work_experience']} → {experience}")
        
        # 格式化时间
        publish_time = extractor.format_publish_time(data["publish_date"])
        print(f"      发布时间: {data['publish_date']} → {publish_time}")
        
        # 生成标签
        tags = extractor.generate_position_tags(data)
        print(f"      岗位标签: {tags}")
    
    print("\n📈 数据质量验证:")
    quality_report = extractor.validate_data_quality(sample_data)
    print(f"   状态: {quality_report['status']}")
    print(f"   消息: {quality_report['message']}")
    print(f"   总记录: {quality_report['total_records']}")
    print(f"   有效记录: {quality_report['valid_records']}")
    print(f"   完整率: {quality_report['completeness_percentage']}")
    
    print("\n✅ 数据提取工具演示完成!")
    
    return quality_report


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行演示
    demo_result = demo_data_extractors()
    
    if demo_result["status"] == "通过":
        print(f"\n🎉 数据提取工具演示成功")
    else:
        print(f"\n⚠️  数据提取工具演示完成，但有警告")
