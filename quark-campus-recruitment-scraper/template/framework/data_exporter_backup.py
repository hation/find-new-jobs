#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出框架模板
- 支持Excel、CSV、JSON格式
- 数据验证和清洗
- 模板化输出

通用组件，可用于任何公司招聘数据导出
"""

import json
import csv
import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    """数据导出框架（通用模板）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化数据导出器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 输出目录
        self.output_dir = self.config.get("output_dir", "output/data_export")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 默认配置
        self.default_config = {
            "formats": ["excel", "csv", "json"],
            "default_format": "excel",
            "excel_settings": {
                "include_sheets": ["所有岗位", "地点分布", "类别分布", "学历分布", "数据摘要"],
                "auto_adjust_columns": True,
                "freeze_panes": True,
                "include_charts": False
            },
            "csv_settings": {
                "encoding": "utf-8-sig",  # 支持Excel中文
                "delimiter": ",",
                "quotechar": "\""
            },
            "json_settings": {
                "indent": 2,
                "ensure_ascii": False
            },
            "naming_pattern": "{company}_positions_{date}.{ext}",
            "date_format": "%Y%m%d_%H%M%S",
            "company_name": "未知公司"
        }
        
        # 合并配置
        self.default_config.update(self.config)
        
        logger.info(f"✅ 数据导出器初始化完成，输出目录: {self.output_dir}")
    
    def export_data(
        self, 
        data: Union[List[Dict], Dict[str, Any]], 
        format: str = None,
        company_name: str = None,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出数据到指定格式
        
        Args:
            data: 要导出的数据
            format: 导出格式（excel/csv/json/all）
            company_name: 公司名称（用于文件名）
            additional_info: 附加信息（如统计信息）
            
        Returns:
            导出结果
        """
        format = format or self.default_config["default_format"]
        company_name = company_name or self.default_config["company_name"]
        
        if not data:
            logger.warning("⚠️ 没有数据需要导出")
            return {"success": False, "error": "没有数据"}
        
        logger.info(f"📤 开始导出数据，格式: {format}，公司: {company_name}")
        
        results = {}
        
        try:
            if format == "all":
                # 导出所有格式
                for fmt in self.default_config["formats"]:
                    result = self._export_single_format(data, fmt, company_name, additional_info)
                    results[fmt] = result
            else:
                # 导出单个格式
                result = self._export_single_format(data, format, company_name, additional_info)
                results[format] = result
            
            # 生成汇总报告
            summary = self._generate_export_summary(results, company_name)
            
            logger.info(f"✅ 数据导出完成，文件位置: {self.output_dir}")
            return {
                "success": True,
                "results": results,
                "summary": summary,
                "output_directory": self.output_dir
            }
            
        except Exception as e:
            logger.error(f"❌ 数据导出失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": format,
                "company_name": company_name
            }
    
    def _export_single_format(
        self,
        data: Union[List[Dict], Dict[str, Any]],
        format: str,
        company_name: str,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出到单个格式
        
        Args:
            data: 要导出的数据
            format: 导出格式
            company_name: 公司名称
            additional_info: 附加信息
            
        Returns:
            导出结果
        """
        logger.info(f"  📝 导出到{format.upper()}格式...")
        
        # 生成文件名
        timestamp = datetime.now().strftime(self.default_config["date_format"])
        filename = self.default_config["naming_pattern"].format(
            company=company_name.lower().replace(" ", "_"),
            date=timestamp,
            ext=format
        )
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            if format == "excel":
                result = self._export_to_excel(data, filepath, company_name, additional_info)
            elif format == "csv":
                result = self._export_to_csv(data, filepath, additional_info)
            elif format == "json":
                result = self._export_to_json(data, filepath, additional_info)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            result["filepath"] = filepath
            result["filename"] = filename
            result["format"] = format
            
            logger.info(f"    ✅ 已保存: {filename}")
            return result
            
        except Exception as e:
            logger.error(f"    ❌ 导出{format.upper()}格式失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "format": format,
                "filepath": filepath
            }
    
    def _export_to_excel(
        self,
        data: Union[List[Dict], Dict[str, Any]],
        filepath: str,
        company_name: str,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出到Excel
        
        Args:
            data: 要导出的数据
            filepath: 文件路径
            company_name: 公司名称
            additional_info: 附加信息
            
        Returns:
            导出结果
        """
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # 1. 所有岗位数据
                if isinstance(data, list):
                    df_all = pd.DataFrame(data)
                else:
                    df_all = pd.DataFrame(data.get("positions", []))
                
                if not df_all.empty:
                    df_all.to_excel(writer, sheet_name='所有岗位', index=False)
                    
                    # 自动调整列宽
                    if self.default_config["excel_settings"]["auto_adjust_columns"]:
                        self._auto_adjust_excel_columns(writer, '所有岗位', df_all)
                
                # 2. 地点分布
                if not df_all.empty and 'work_location' in df_all.columns:
                    location_stats = df_all['work_location'].value_counts().reset_index()
                    location_stats.columns = ['工作地点', '岗位数量']
                    location_stats.to_excel(writer, sheet_name='地点分布', index=False)
                
                # 3. 类别分布（如果存在类别字段）
                if not df_all.empty:
                    category_field = self._find_category_field(df_all)
                    if category_field:
                        category_stats = df_all[category_field].value_counts().reset_index()
                        category_stats.columns = ['岗位类别', '岗位数量']
                        category_stats.to_excel(writer, sheet_name='类别分布', index=False)
                
                # 4. 学历分布
                if not df_all.empty and 'education_requirement' in df_all.columns:
                    education_stats = df_all['education_requirement'].value_counts().reset_index()
                    education_stats.columns = ['学历要求', '岗位数量']
                    education_stats.to_excel(writer, sheet_name='学历分布', index=False)
                
                # 5. 数据摘要
                summary_data = self._generate_summary_data(df_all, company_name, additional_info)
                df_summary = pd.DataFrame([summary_data])
                df_summary.to_excel(writer, sheet_name='数据摘要', index=False)
                
                # 6. 原始数据（如果需要）
                if isinstance(data, dict) and "raw_data" in data:
                    raw_df = pd.DataFrame(data["raw_data"])
                    raw_df.to_excel(writer, sheet_name='原始数据', index=False)
            
            return {
                "success": True,
                "sheets": writer.sheets.keys() if hasattr(writer, 'sheets') else [],
                "total_positions": len(df_all) if not df_all.empty else 0,
                "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
            }
            
        except Exception as e:
            raise Exception(f"Excel导出失败: {e}")
    
    def _export_to_csv(
        self,
        data: Union[List[Dict], Dict[str, Any]],
        filepath: str,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出到CSV
        
        Args:
            data: 要导出的数据
            filepath: 文件路径
            additional_info: 附加信息
            
        Returns:
            导出结果
        """
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data.get("positions", []))
            
            if df.empty:
                raise ValueError("没有数据可以导出")
            
            csv_settings = self.default_config["csv_settings"]
            
            df.to_csv(
                filepath,
                index=False,
                encoding=csv_settings["encoding"],
                sep=csv_settings["delimiter"],
                quotechar=csv_settings["quotechar"]
            )
            
            return {
                "success": True,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
            }
            
        except Exception as e:
            raise Exception(f"CSV导出失败: {e}")
    
    def _export_to_json(
        self,
        data: Union[List[Dict], Dict[str, Any]],
        filepath: str,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出到JSON
        
        Args:
            data: 要导出的数据
            filepath: 文件路径
            additional_info: 附加信息
            
        Returns:
            导出结果
        """
        try:
            export_data = {
                "export_info": {
                    "export_time": datetime.now().isoformat(),
                    "format": "json",
                    "version": "1.0"
                },
                "data": data if isinstance(data, dict) else {"positions": data}
            }
            
            if additional_info:
                export_data["additional_info"] = additional_info
            
            json_settings = self.default_config["json_settings"]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(
                    export_data, 
                    f, 
                    ensure_ascii=json_settings["ensure_ascii"],
                    indent=json_settings["indent"]
                )
            
            return {
                "success": True,
                "total_items": len(data) if isinstance(data, list) else 1,
                "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
            }
            
        except Exception as e:
            raise Exception(f"JSON导出失败: {e}")
    
    def _auto_adjust_excel_columns(self, writer, sheet_name: str, df: pd.DataFrame):
        """
        自动调整Excel列宽
        
        Args:
            writer: Excel写入器
            sheet_name: 工作表名称
            df: 数据框
        """
        try:
            worksheet = writer.sheets[sheet_name]
            
            for idx, col in enumerate(df.columns):
                # 获取列宽（基于列名和最大数据长度）
                column_width = max(
                    len(str(col)),
                    df[col].astype(str).str.len().max() if not df[col].empty else 0
                ) + 2  # 添加一些边距
                
                # 设置列宽（限制最大宽度）
                column_width = min(column_width, 50)
                worksheet.column_dimensions[chr(65 + idx)].width = column_width
                
        except Exception as e:
            logger.warning(f"自动调整列宽失败: {e}")
    
    def _find_category_field(self, df: pd.DataFrame) -> Optional[str]:
        """
        查找类别字段
        
        Args:
            df: 数据框
            
        Returns:
            类别字段名或None
        """
        category_fields = ['category', 'department', 'position_type', 'job_type']
        
        for field in category_fields:
            if field in df.columns:
                return field
        
        return None
    
    def _generate_summary_data(
        self, 
        df: pd.DataFrame, 
        company_name: str,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        生成数据摘要
        
        Args:
            df: 数据框
            company_name: 公司名称
            additional_info: 附加信息
            
        Returns:
            摘要数据
        """
        summary = {
            "公司名称": company_name,
            "导出时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "总岗位数量": len(df) if not df.empty else 0,
            "数据字段数量": len(df.columns) if not df.empty else 0
        }
        
        if not df.empty:
            # 统计信息
            if 'work_location' in df.columns:
                summary["地点数量"] = df['work_location'].nunique()
                summary["最多岗位地点"] = df['work_location'].mode().iloc[0] if not df['work_location'].mode().empty else "N/A"
            
            if 'education_requirement' in df.columns:
                summary["学历要求种类"] = df['education_requirement'].nunique()
            
            # 完整性统计
            completeness = {}
            for col in df.columns:
                non_null_count = df[col].notna().sum()
                completeness[col] = f"{non_null_count/len(df)*100:.1f}%"
            
            summary["数据完整性"] = completeness
        
        # 添加附加信息
        if additional_info:
            summary.update(additional_info)
        
        return summary
    
    def _generate_export_summary(self, results: Dict[str, Dict], company_name: str) -> Dict[str, Any]:
        """
        生成导出汇总报告
        
        Args:
            results: 各格式的导出结果
            company_name: 公司名称
            
        Returns:
            汇总报告
        """
        successful_formats = []
        failed_formats = []
        total_file_size_mb = 0
        
        for format, result in results.items():
            if result.get("success"):
                successful_formats.append(format)
                total_file_size_mb += result.get("file_size_mb", 0)
            else:
                failed_formats.append(format)
        
        return {
            "company_name": company_name,
            "export_time": datetime.now().isoformat(),
            "total_formats_attempted": len(results),
            "successful_formats": successful_formats,
            "failed_formats": failed_formats,
            "success_rate": f"{len(successful_formats)/len(results)*100:.1f}%" if results else "0%",
            "total_file_size_mb": total_file_size_mb,
            "output_directory": self.output_dir,
            "note": f"使用 {len(successful_formats)}/{len(results)} 种格式成功导出数据"
        }


# ==================== 模板使用示例 ====================

def demo_data_exporter():
    """演示如何使用数据导出器模板"""
    print("🚀 数据导出器模板演示")
    print("=" * 50)
    
    # 1. 创建示例数据
    sample_data = [
        {
            "position_id": "001",
            "position_name": "软件工程师",
            "work_location": "北京",
            "department": "技术部",
            "education_requirement": "本科",
            "work_experience": "3-5年",
            "salary_range": "20-30k",
            "publish_date": "2026-05-20"
        },
        {
            "position_id": "002",
            "position_name": "产品经理",
            "work_location": "上海",
            "department": "产品部",
            "education_requirement": "硕士",
            "work_experience": "5年以上",
            "salary_range": "30-40k",
            "publish_date": "2026-05-19"
        },
        {
            "position_id": "003",
            "position_name": "数据分析师",
            "work_location": "深圳",
            "department": "数据部",
            "education_requirement": "本科",
            "work_experience": "2-3年",
            "salary_range": "15-25k",
            "publish_date": "2026-05-18"
        }
    ]
    
    # 2. 创建导出器配置
    config = {
        "output_dir": "output/demo_export",
        "company_name": "示例公司",
        "excel_settings": {
            "include_sheets": ["所有岗位", "地点分布", "数据摘要"],
            "auto_adjust_columns": True
        }
    }
    
    # 3. 创建导出器实例
    exporter = DataExporter(config)
    
    # 4. 导出数据（Excel格式）
    print("📤 导出到Excel格式...")
    result_excel = exporter.export_data(
        sample_data, 
        format="excel", 
        company_name="示例公司"
    )
    
    if result_excel["success"]:
        print(f"    ✅ Excel导出成功: {result_excel['results']['excel']['filepath']}")
    else:
        print(f"    ❌ Excel导出失败: {result_excel.get('error')}")
    
    # 5. 导出数据（所有格式）
    print("\n📤 导出到所有格式...")
    result_all = exporter.export_data(
        sample_data, 
        format="all", 
        company_name="示例公司"
    )
    
    if result_all["success"]:
        print(f"    ✅ 所有格式导出成功")
        summary = result_all["summary"]
        print(f"    成功格式: {', '.join(summary['successful_formats'])}")
        print(f"    文件大小: {summary['total_file_size_mb']:.2f} MB")
    else:
        print(f"    ❌ 导出失败: {result_all.get('error')}")
    
    print(f"\n📂 导出文件位置: {exporter.output_dir}")
    print(f"🎉 演示完成！")
    
    return result_all


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行演示
    demo_result = demo_data_exporter()
    
    if demo_result.get("success"):
        print(f"\n✅ 数据导出器模板演示成功")
    else:
        print(f"\n❌ 数据导出器模板演示失败: {demo_result.get('error')}")