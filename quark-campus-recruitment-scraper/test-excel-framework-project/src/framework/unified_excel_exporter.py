#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Excel导出框架（基于anti-job和jd-job经验沉淀）
- 多工作表标准结构（7个工作表）
- 中文列名标准化（16个标准列）
- 数据清洗和格式化
- 统计分析自动生成
- 质量验证和报告

【核心原则】
1. 统一性：所有项目使用相同的Excel格式
2. 标准化：16个标准列名，7个标准工作表
3. 自动化：自动数据清洗、统计分析、质量验证
4. 可维护：集中管理，一处修改，所有项目生效

【使用场景】
1. 新项目启动：直接使用统一格式
2. 历史数据转换：转换旧格式到统一格式
3. 数据质量检查：自动验证数据完整性
4. 统计分析：自动生成6个统计分析表
"""

import json
import os
import pandas as pd
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class UnifiedExcelExporter:
    """统一Excel导出框架"""
    
    # 标准列名定义（16列，完全匹配anti-job格式）
    STANDARD_COLUMNS = [
        "序号",          # 1. 自动生成的序号
        "岗位ID",        # 2. 岗位唯一标识
        "岗位名称",      # 3. 岗位名称
        "岗位类别",      # 4. 岗位类型/类别
        "工作地点",      # 5. 工作城市/地点
        "发布时间",      # 6. 岗位发布时间
        "所属部门",      # 7. 部门/事业部
        "学历要求",      # 8. 学历要求（自动提取）
        "工作经验",      # 9. 工作经验（自动提取）
        "岗位要求",      # 10. 任职要求/资格
        "岗位描述",      # 11. 工作内容/描述
        "岗位标签",      # 12. 标签（自动生成）
        "岗位代码",      # 13. 招聘代码/编号
        "是否收藏",      # 14. 是否收藏（默认"否"）
        "数据来源",      # 15. 数据来源（公司名称+官网）
        "类别名称"       # 16. 类别名称（同岗位类别）
    ]
    
    # 标准工作表定义（7个工作表）
    STANDARD_SHEETS = [
        "所有岗位",      # 主工作表：完整数据
        "地点分布",      # 统计分析：工作地点分布
        "类别分布",      # 统计分析：岗位类别分布
        "学历分布",      # 统计分析：学历要求分布
        "部门分布",      # 统计分析：所属部门分布
        "经验要求",      # 统计分析：工作经验分布
        "数据摘要"       # 质量报告：数据基本信息
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化统一Excel导出器
        
        Args:
            config: 配置字典，包含公司名称、输出目录等
        """
        self.config = config or {}
        
        # 公司信息
        self.company_name = self.config.get("company_name", "未知公司")
        self.company_website = self.config.get("company_website", "")
        
        # 输出目录
        self.output_dir = Path(self.config.get("output_dir", "output/unified_excel"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 文件命名模式
        self.naming_pattern = self.config.get(
            "naming_pattern",
            "{company}_international_positions_{timestamp}.xlsx"
        )
        
        # 数据质量要求
        self.quality_config = self.config.get("quality_config", {
            "min_completeness": 0.8,      # 最小数据完整率
            "required_columns": 16,       # 必须的列数
            "auto_validation": True,      # 自动验证
            "generate_csv": True          # 同时生成CSV
        })
        
        logger.info(f"✅ 统一Excel导出器初始化完成")
        logger.info(f"   公司: {self.company_name}")
        logger.info(f"   输出目录: {self.output_dir}")
        logger.info(f"   标准列: {len(self.STANDARD_COLUMNS)} 列")
        logger.info(f"   标准工作表: {len(self.STANDARD_SHEETS)} 个")
    
    def export_to_unified_excel(
        self,
        positions: List[Dict[str, Any]],
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出岗位数据到统一格式的Excel
        
        Args:
            positions: 岗位数据列表
            additional_info: 附加信息（如统计信息、备注等）
            
        Returns:
            导出结果字典，包含文件路径、大小、质量报告等
        """
        logger.info(f"📤 开始导出到统一Excel格式，共 {len(positions)} 个岗位")
        
        if not positions:
            logger.warning("⚠️ 没有岗位数据需要导出")
            return {
                "success": False,
                "error": "没有岗位数据",
                "file_path": None
            }
        
        try:
            # 1. 数据清洗和格式化
            logger.info("🔄 数据清洗和格式化中...")
            processed_positions = self._process_positions(positions)
            
            # 2. 创建DataFrame
            df = pd.DataFrame(processed_positions)
            
            # 3. 验证数据质量
            quality_report = self._validate_data_quality(df)
            
            # 4. 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.naming_pattern.format(
                company=self.company_name.lower().replace(" ", "_"),
                timestamp=timestamp
            )
            file_path = self.output_dir / filename
            
            # 5. 创建多工作表Excel
            logger.info("💾 创建多工作表Excel文件中...")
            self._create_multisheet_excel(df, file_path, additional_info)
            
            # 6. 同时生成简化版CSV（可选）
            csv_file_path = None
            if self.quality_config.get("generate_csv", True):
                csv_file_path = self._generate_simplified_csv(df, timestamp)
            
            # 7. 生成最终报告
            result = {
                "success": True,
                "file_path": str(file_path),
                "file_size_mb": os.path.getsize(file_path) / (1024 * 1024),
                "total_positions": len(df),
                "total_columns": len(df.columns),
                "quality_report": quality_report,
                "sheets_created": self.STANDARD_SHEETS,
                "csv_file_path": str(csv_file_path) if csv_file_path else None,
                "export_time": datetime.now().isoformat(),
                "company_name": self.company_name,
                "format_version": "1.0.0"
            }
            
            logger.info(f"✅ 统一Excel导出完成: {filename}")
            logger.info(f"   文件大小: {result['file_size_mb']:.2f} MB")
            logger.info(f"   岗位数量: {result['total_positions']} 个")
            logger.info(f"   工作表: {len(result['sheets_created'])} 个")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 统一Excel导出失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None,
                "export_time": datetime.now().isoformat()
            }
    
    def _process_positions(self, positions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理岗位数据，转换为统一格式
        
        Args:
            positions: 原始岗位数据
            
        Returns:
            处理后的岗位数据（统一格式）
        """
        processed = []
        
        for i, position in enumerate(positions):
            try:
                # 构建统一格式的岗位数据
                processed_position = {
                    "序号": i + 1,
                    "岗位ID": self._extract_field(position, ["position_id", "id", "job_id"]),
                    "岗位名称": self._extract_field(position, ["position_name", "name", "title"]),
                    "岗位类别": self._extract_field(position, ["job_type", "category", "type"]),
                    "工作地点": self._extract_field(position, ["work_location", "location", "city"]),
                    "发布时间": self._format_publish_time(
                        self._extract_field(position, ["publish_date", "created_at", "post_time"])
                    ),
                    "所属部门": self._extract_field(position, ["department", "dept", "company_department"]),
                    "学历要求": self._extract_education(
                        self._extract_field(position, ["education_requirement", "education", "degree"])
                    ),
                    "工作经验": self._extract_experience(
                        self._extract_field(position, ["work_experience", "experience", "years_experience"])
                    ),
                    "岗位要求": self._extract_field(position, ["position_requirements", "requirements", "qualifications"]),
                    "岗位描述": self._extract_field(position, ["position_description", "description", "job_description"]),
                    "岗位标签": self._generate_tags(position),
                    "岗位代码": self._extract_field(position, ["recruitment_number", "job_code", "code"]),
                    "是否收藏": "否",  # 默认值，大多数招聘网站没有收藏功能
                    "数据来源": f"{self.company_name}招聘官网",
                    "类别名称": self._extract_field(position, ["job_type", "category"])  # 同岗位类别
                }
                
                # 确保所有标准列都存在
                for col in self.STANDARD_COLUMNS:
                    if col not in processed_position:
                        processed_position[col] = ""
                
                processed.append(processed_position)
                
            except Exception as e:
                logger.warning(f"⚠️ 处理第 {i+1} 个岗位失败: {e}")
                # 跳过这个岗位，继续处理下一个
        
        return processed
    
    def _extract_field(self, position: Dict[str, Any], field_names: List[str]) -> str:
        """
        从岗位数据中提取字段（支持多个可能的字段名）
        
        Args:
            position: 岗位数据
            field_names: 可能的字段名列表
            
        Returns:
            字段值（字符串）
        """
        for field_name in field_names:
            if field_name in position:
                value = position[field_name]
                if pd.isna(value):
                    return ""
                return str(value).strip()
        return ""
    
    def _format_publish_time(self, time_str: str) -> str:
        """
        格式化发布时间
        
        Args:
            time_str: 原始时间字符串
            
        Returns:
            格式化后的时间字符串
        """
        if not time_str or pd.isna(time_str) or time_str == "nan":
            return "未知"
        
        try:
            # 尝试解析各种时间格式
            if isinstance(time_str, str):
                # 移除时间部分（如果有）
                time_str = time_str.split()[0]
            
            # 如果是时间戳（毫秒）
            if time_str.isdigit() and len(time_str) == 13:
                timestamp = int(time_str) / 1000
                dt = datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d")
            
            # 如果是日期字符串
            return str(time_str)
            
        except Exception:
            return str(time_str)
    
    def _extract_education(self, education_text: str) -> str:
        """
        从文本中提取学历要求
        
        Args:
            education_text: 原始学历要求文本
            
        Returns:
            标准化的学历要求
        """
        if not education_text or pd.isna(education_text):
            return "学历不限"
        
        education_text = str(education_text)
        
        # 学历关键词映射
        education_keywords = {
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
        
        # 检查是否包含关键词
        for keyword, level in education_keywords.items():
            if keyword in education_text:
                return level
        
        # 检查常见模式
        if "不限" in education_text or "无要求" in education_text or "学历不限" in education_text:
            return "学历不限"
        
        return "学历不限"
    
    def _extract_experience(self, experience_text: str) -> str:
        """
        从文本中提取工作经验
        
        Args:
            experience_text: 原始工作经验文本
            
        Returns:
            标准化的工作经验
        """
        if not experience_text or pd.isna(experience_text):
            return "经验不限"
        
        experience_text = str(experience_text)
        
        # 匹配数字+年
        year_pattern = r'(\d+)[\+-]?\s*年'
        matches = re.findall(year_pattern, experience_text)
        
        if matches:
            years = [int(m) for m in matches]
            if len(years) >= 2:
                return f"{min(years)}-{max(years)}年"
            else:
                return f"{years[0]}+年"
        
        # 检查常见关键词
        if "不限" in experience_text or "无要求" in experience_text or "经验不限" in experience_text:
            return "经验不限"
        elif "应届" in experience_text:
            return "应届生"
        elif "实习" in experience_text:
            return "实习生"
        elif "在校" in experience_text:
            return "在校生"
        
        return "经验不限"
    
    def _generate_tags(self, position: Dict[str, Any]) -> str:
        """
        生成岗位标签
        
        Args:
            position: 岗位数据
            
        Returns:
            标签字符串（逗号分隔）
        """
        tags = []
        
        # 从工作地点提取
        location = self._extract_field(position, ["work_location", "location", "city"])
        if location and location != "未知":
            tags.append(location)
        
        # 从部门提取
        department = self._extract_field(position, ["department", "dept"])
        if department:
            tags.append(department)
        
        # 从岗位类型提取
        job_type = self._extract_field(position, ["job_type", "category"])
        if job_type:
            tags.append(job_type)
        
        # 检查是否热门
        is_hot = position.get("is_hot", 0)
        if is_hot == 1 or is_hot == "1" or is_hot == True:
            tags.append("热门岗位")
        
        # 检查是否紧急
        is_urgent = position.get("is_urgent", 0)
        if is_urgent == 1 or is_urgent == "1" or is_urgent == True:
            tags.append("紧急招聘")
        
        return ", ".join(tags) if tags else ""
    
    def _validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据质量
        
        Args:
            df: 数据框
            
        Returns:
            质量报告
        """
        if df.empty:
            return {
                "completeness": 0.0,
                "missing_columns": self.STANDARD_COLUMNS,
                "total_missing": len(df) * len(self.STANDARD_COLUMNS),
                "status": "失败",
                "message": "数据框为空"
            }
        
        # 检查列名匹配度
        missing_columns = [col for col in self.STANDARD_COLUMNS if col not in df.columns]
        extra_columns = [col for col in df.columns if col not in self.STANDARD_COLUMNS]
        
        # 计算数据完整率
        total_cells = df.shape[0] * df.shape[1]
        missing_values = df.isnull().sum().sum()
        completeness = 1.0 - (missing_values / total_cells) if total_cells > 0 else 0.0
        
        # 生成质量报告
        quality_report = {
            "completeness": completeness,
            "completeness_percentage": f"{completeness * 100:.1f}%",
            "missing_columns": missing_columns,
            "extra_columns": extra_columns,
            "column_match_rate": f"{len(df.columns)}/{len(self.STANDARD_COLUMNS)}",
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": int(missing_values),
            "total_cells": total_cells,
            "status": "通过" if completeness >= self.quality_config["min_completeness"] else "失败",
            "message": f"数据完整率: {completeness * 100:.1f}%"
        }
        
        logger.info(f"📊 数据质量报告:")
        logger.info(f"   完整率: {quality_report['completeness_percentage']}")
        logger.info(f"   列匹配: {quality_report['column_match_rate']}")
        logger.info(f"   缺失值: {quality_report['missing_values']}/{quality_report['total_cells']}")
        
        return quality_report
    
    def _create_multisheet_excel(self, df: pd.DataFrame, file_path: Path, additional_info: Dict[str, Any] = None):
        """
        创建多工作表Excel文件
        
        Args:
            df: 数据框
            file_path: 文件路径
            additional_info: 附加信息
        """
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 1. 所有岗位（主工作表）
            df.to_excel(writer, sheet_name='所有岗位', index=False)
            
            # 2. 地点分布
            if '工作地点' in df.columns and not df['工作地点'].isnull().all():
                location_stats = df['工作地点'].value_counts().reset_index()
                location_stats.columns = ['工作地点', '岗位数量']
                location_stats.to_excel(writer, sheet_name='地点分布', index=False)
            
            # 3. 类别分布
            if '岗位类别' in df.columns and not df['岗位类别'].isnull().all():
                category_stats = df['岗位类别'].value_counts().reset_index()
                category_stats.columns = ['岗位类别', '岗位数量']
                category_stats.to_excel(writer, sheet_name='类别分布', index=False)
            
            # 4. 学历分布
            if '学历要求' in df.columns and not df['学历要求'].isnull().all():
                education_stats = df['学历要求'].value_counts().reset_index()
                education_stats.columns = ['学历要求', '岗位数量']
                education_stats.to_excel(writer, sheet_name='学历分布', index=False)
            
            # 5. 部门分布
            if '所属部门' in df.columns and not df['所属部门'].isnull().all():
                department_stats = df['所属部门'].value_counts().reset_index()
                department_stats.columns = ['所属部门', '岗位数量']
                department_stats.to_excel(writer, sheet_name='部门分布', index=False)
            
            # 6. 经验要求
            if '工作经验' in df.columns and not df['工作经验'].isnull().all():
                experience_stats = df['工作经验'].value_counts().reset_index()
                experience_stats.columns = ['工作经验', '岗位数量']
                experience_stats.to_excel(writer, sheet_name='经验要求', index=False)
            
            # 7. 数据摘要
            summary_data = self._generate_summary_data(df, additional_info)
            summary_df = pd.DataFrame([summary_data])
            summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
    
    def _generate_summary_data(self, df: pd.DataFrame, additional_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成数据摘要
        
        Args:
            df: 数据框
            additional_info: 附加信息
            
        Returns:
            摘要数据字典
        """
        summary = {
            "统计项": "值",
            "总岗位数": len(df),
            "数据来源": f"{self.company_name}招聘官网",
            "公司名称": self.company_name,
            "Excel生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据文件": self.output_dir.name,
            "数据质量": f"完整率: {df.notnull().sum().sum()/(df.shape[0]*df.shape[1])*100:.1f}%",
            "标准列数": len(self.STANDARD_COLUMNS),
            "实际列数": len(df.columns),
            "工作表数量": len(self.STANDARD_SHEETS),
            "导出框架版本": "1.0.0"
        }
        
        if additional_info:
            summary.update(additional_info)
        
        return summary
    
    def _generate_simplified_csv(self, df: pd.DataFrame, timestamp: str) -> Path:
        """
        生成简化版CSV文件
        
        Args:
            df: 数据框
            timestamp: 时间戳
            
        Returns:
            CSV文件路径
        """
        # 选择关键列
        key_columns = ['序号', '岗位名称', '岗位类别', '工作地点', '学历要求', '工作经验', '所属部门']
        available_columns = [col for col in key_columns if col in df.columns]
        
        if not available_columns:
            return None
        
        # 生成文件名
        csv_filename = f"{self.company_name.lower().replace(' ', '_')}_positions_simple_{timestamp}.csv"
        csv_file_path = self.output_dir / csv_filename
        
        # 创建简化版数据
        simple_df = df[available_columns]
        simple_df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"✅ 简化版CSV文件已创建: {csv_filename}")
        
        return csv_file_path
    
    def convert_legacy_excel(self, legacy_file_path: Path, output_dir: Path = None) -> Dict[str, Any]:
        """
        转换旧格式Excel到统一格式
        
        Args:
            legacy_file_path: 旧格式Excel文件路径
            output_dir: 输出目录（可选）
            
        Returns:
            转换结果
        """
        logger.info(f"🔄 开始转换旧格式Excel: {legacy_file_path.name}")
        
        try:
            # 读取旧格式Excel
            df = pd.read_excel(legacy_file_path)
            
            # 转换为字典列表
            positions = df.to_dict('records')
            
            # 使用统一导出器
            if output_dir:
                self.output_dir = Path(output_dir)
                self.output_dir.mkdir(parents=True, exist_ok=True)
            
            result = self.export_to_unified_excel(positions)
            
            if result["success"]:
                logger.info(f"✅ 旧格式转换成功: {legacy_file_path.name} → {Path(result['file_path']).name}")
            else:
                logger.error(f"❌ 旧格式转换失败: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 转换旧格式Excel失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }


# ==================== 使用示例 ====================

def demo_unified_excel_exporter():
    """演示统一Excel导出器的使用"""
    print("🚀 统一Excel导出框架演示")
    print("=" * 60)
    
    # 创建示例数据
    sample_data = [
        {
            "position_id": "JD001",
            "position_name": "软件工程师",
            "job_type": "技术类",
            "work_location": "北京",
            "publish_date": "2026-05-20",
            "department": "技术研发部",
            "education_requirement": "本科及以上学历",
            "work_experience": "3-5年工作经验",
            "position_requirements": "熟悉Python、Java等编程语言",
            "position_description": "负责后端系统开发和维护",
            "recruitment_number": "ZP260520001",
            "is_hot": 1
        },
        {
            "position_id": "JD002",
            "position_name": "产品经理",
            "job_type": "产品类",
            "work_location": "上海",
            "publish_date": "2026-05-19",
            "department": "产品部",
            "education_requirement": "硕士学历优先",
            "work_experience": "5年以上产品经验",
            "position_requirements": "有B端产品经验者优先",
            "position_description": "负责产品规划和管理",
            "recruitment_number": "ZP260519001",
            "is_hot": 0
        }
    ]
    
    # 配置统一导出器
    config = {
        "company_name": "示例公司",
        "company_website": "https://example.com",
        "output_dir": "output/demo_unified_excel",
        "quality_config": {
            "min_completeness": 0.7,
            "auto_validation": True,
            "generate_csv": True
        }
    }
    
    # 创建导出器实例
    exporter = UnifiedExcelExporter(config)
    
    # 导出数据
    print("📤 导出到统一Excel格式...")
    result = exporter.export_to_unified_excel(sample_data)
    
    if result["success"]:
        print(f"    ✅ 导出成功!")
        print(f"       文件: {Path(result['file_path']).name}")
        print(f"       大小: {result['file_size_mb']:.2f} MB")
        print(f"       岗位: {result['total_positions']} 个")
        print(f"       工作表: {len(result['sheets_created'])} 个")
        print(f"       质量: {result['quality_report']['completeness_percentage']}")
        
        # 显示质量报告
        print(f"\n📊 数据质量报告:")
        for key, value in result['quality_report'].items():
            if isinstance(value, (str, int, float)):
                print(f"       {key}: {value}")
    else:
        print(f"    ❌ 导出失败: {result.get('error')}")
    
    print(f"\n📂 导出文件位置: {exporter.output_dir}")
    print(f"🎉 演示完成!")
    
    return result


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行演示
    demo_result = demo_unified_excel_exporter()
    
    if demo_result.get("success"):
        print(f"\n✅ 统一Excel导出框架演示成功")
    else:
        print(f"\n❌ 统一Excel导出框架演示失败: {demo_result.get('error')}")