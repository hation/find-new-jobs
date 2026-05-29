#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
拼多多数据导出器 - 基于夸克项目数据导出框架
复用夸克项目的完整导出系统，避免重新发明轮子
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加夸克项目导出框架
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "quark-campus-recruitment-scraper/template/framework"))

try:
    from data_exporter import DataExporter
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False

import logging
logger = logging.getLogger(__name__)


class PddDataExporter:
    """拼多多数据导出器（基于夸克项目框架）"""
    
    def __init__(self, config_path: str = None):
        """
        初始化PDD数据导出器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "config/project_config.json"
        self.config = self._load_config()
        
        # 导出配置
        self.output_dir = self.config.get("output_dir", "output/pdd_export")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # PDD特定配置
        self.company_name = "拼多多"
        self.default_format = self.config.get("data_export", {}).get("default_format", "excel")
        
        # 检查夸克项目导出框架是否可用
        self.use_quark_framework = False
        self.quark_exporter = None
        
        if IMPORT_SUCCESS:
            try:
                self._initialize_quark_exporter()
                self.use_quark_framework = True
            except Exception as e:
                logger.warning(f"⚠️ 夸克项目导出框架初始化失败: {e}")
                self.use_quark_framework = False
        else:
            logger.warning("⚠️ 夸克项目导出框架导入失败，将使用简化版导出")
        
        logger.info(f"✅ PDD数据导出器初始化完成")
        logger.info(f"   使用夸克框架: {self.use_quark_framework}")
        logger.info(f"   输出目录: {self.output_dir}")
        logger.info(f"   默认格式: {self.default_format}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"配置文件加载失败: {e}")
        return {}
    
    def _initialize_quark_exporter(self):
        """初始化夸克项目导出器"""
        try:
            # 夸克项目导出器配置
            # 夸克项目使用"excel"作为格式，但我们需要.xlsx扩展名
            # 修改命名模式，将.excel替换为.xlsx
            quark_config = {
                "output_dir": self.output_dir,
                "company_name": self.company_name,
                "formats": ["excel", "csv", "json"],  # 夸克项目使用excel
                "default_format": "excel",  # 夸克项目使用excel
                "naming_pattern": "{company}_positions_{date}.{ext}",  # 夸克项目使用{ext}
                "excel_settings": {
                    "include_sheets": ["所有岗位", "地点分布", "类别分布", "数据摘要"],
                    "auto_adjust_columns": True,
                    "freeze_panes": True
                },
                "csv_settings": {
                    "encoding": "utf-8-sig",
                    "delimiter": ",",
                    "quotechar": "\""
                },
                "json_settings": {
                    "indent": 2,
                    "ensure_ascii": False
                }
            }
            
            self.quark_exporter = DataExporter(quark_config)
            logger.info("✅ 夸克项目导出框架初始化成功")
            
        except Exception as e:
            logger.error(f"夸克项目导出框架初始化失败: {e}")
            self.quark_exporter = None
            self.use_quark_framework = False
    
    def export_positions(self, positions: List[Dict[str, Any]], format: str = None) -> Dict[str, Any]:
        """
        导出岗位数据
        
        Args:
            positions: 岗位数据列表
            format: 导出格式（excel/csv/json/all）
            
        Returns:
            导出结果
        """
        logger.info(f"📤 开始导出 {len(positions)} 个岗位数据...")
        
        if not positions:
            logger.warning("⚠️ 没有岗位数据需要导出")
            return {"success": False, "error": "没有岗位数据"}
        
        # Excel导出使用简化版（夸克项目导出器有.excel扩展名问题）
        if format == "excel":
            logger.info("   ⚠️ Excel导出使用简化版（夸克项目导出器有扩展名问题）")
            return self._export_simple_excel(positions)
        
        # 其他格式使用夸克项目导出框架（如果可用）
        if self.use_quark_framework and self.quark_exporter:
            return self._export_with_quark_framework(positions, format)
        else:
            return self._export_simple(positions, format)
    
    def _export_with_quark_framework(self, positions: List[Dict[str, Any]], format: str = None) -> Dict[str, Any]:
        """使用夸克项目导出框架"""
        try:
            format = format or self.default_format
            
            # 准备附加信息
            additional_info = {
                "company": self.company_name,
                "total_positions": len(positions),
                "export_time": os.path.basename(__file__),
                "data_fields": list(positions[0].keys()) if positions else []
            }
            
            # 调用夸克项目导出器
            if self.quark_exporter:
                result = self.quark_exporter.export_data(
                    data=positions,
                    format=format,
                    company_name=self.company_name,
                    additional_info=additional_info
                )
                
                if result.get("success"):
                    logger.info(f"✅ 数据导出成功: {result.get('output_directory', 'N/A')}")
                    
                    # 提取文件路径
                    filepath = None
                    if "results" in result and format in result["results"]:
                        filepath = result["results"][format].get("filepath")
                        
                        # 处理Excel文件扩展名：.excel -> .xlsx
                        if format == "excel" and filepath and filepath.endswith(".excel"):
                            new_filepath = filepath.replace(".excel", ".xlsx")
                            try:
                                os.rename(filepath, new_filepath)
                                filepath = new_filepath
                                logger.info(f"   🔄 重命名Excel文件: {os.path.basename(filepath)} -> {os.path.basename(new_filepath)}")
                            except Exception as e:
                                logger.warning(f"   ⚠️ 重命名Excel文件失败: {e}")
                    
                    # 返回标准化结果
                    return {
                        "success": True,
                        "format": format,
                        "filepath": filepath,
                        "quark_result": result,
                        "total_positions": len(positions),
                        "file_size_mb": result.get("summary", {}).get("total_file_size_mb", 0)
                    }
                else:
                    logger.error(f"❌ 数据导出失败: {result.get('error', '未知错误')}")
                    return result
            else:
                logger.warning("⚠️ 夸克项目导出器未初始化")
                return {
                    "success": False,
                    "error": "夸克项目导出器未初始化",
                    "fallback": "将尝试简化版导出"
                }
            
        except Exception as e:
            logger.error(f"夸克框架导出异常: {e}")
            return {
                "success": False,
                "error": f"夸克框架导出异常: {str(e)}",
                "fallback": "将尝试简化版导出"
            }
    
    def _export_simple(self, positions: List[Dict[str, Any]], format: str = None) -> Dict[str, Any]:
        """简化版导出（夸克框架不可用时使用）"""
        try:
            from datetime import datetime
            import pandas as pd
            
            format = format or "json"  # 简化版默认使用JSON
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.{format}"
            filepath = os.path.join(self.output_dir, filename)
            
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(positions, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ JSON数据已保存: {filepath}")
                return {
                    "success": True,
                    "format": "json",
                    "filepath": filepath,
                    "filename": filename,
                    "total_positions": len(positions),
                    "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
                }
            
            elif format == "csv":
                df = pd.DataFrame(positions)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                
                logger.info(f"✅ CSV数据已保存: {filepath}")
                return {
                    "success": True,
                    "format": "csv",
                    "filepath": filepath,
                    "filename": filename,
                    "total_positions": len(positions),
                    "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
                }
            
            else:
                logger.error(f"❌ 不支持的格式: {format}")
                return {
                    "success": False,
                    "error": f"不支持的格式: {format}",
                    "supported_formats": ["json", "csv"]
                }
                
        except Exception as e:
            logger.error(f"简化版导出失败: {e}")
            return {
                "success": False,
                "error": f"简化版导出失败: {str(e)}"
            }
    
    def _export_simple_excel(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """简化版Excel导出"""
        try:
            from datetime import datetime
            import pandas as pd
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pdd_positions_{timestamp}.xlsx"
            filepath = os.path.join(self.output_dir, filename)
            
            # 创建Excel文件
            df = pd.DataFrame(positions)
            
            # 使用openpyxl引擎
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='所有岗位', index=False)
                
                # 可以添加更多工作表（如夸克项目导出器那样）
                # 这里先简化，只导出所有岗位
                
            logger.info(f"✅ Excel数据已保存: {filepath}")
            return {
                "success": True,
                "format": "excel",
                "filepath": filepath,
                "filename": filename,
                "total_positions": len(positions),
                "file_size_mb": os.path.getsize(filepath) / (1024 * 1024)
            }
                
        except Exception as e:
            logger.error(f"简化版Excel导出失败: {e}")
            return {
                "success": False,
                "error": f"简化版Excel导出失败: {str(e)}"
            }
    
    def generate_export_report(self, export_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成导出报告"""
        logger.info("📋 生成导出报告...")
        
        report = {
            "project": "拼多多招聘爬取器",
            "export_time": datetime.now().isoformat(),
            "company": self.company_name,
            "export_result": export_result,
            "environment": {
                "use_quark_framework": self.use_quark_framework,
                "output_directory": self.output_dir,
                "config_loaded": bool(self.config)
            }
        }
        
        if export_result.get("success"):
            report["status"] = "success"
            report["summary"] = {
                "total_positions": export_result.get("total_positions", 0),
                "export_format": export_result.get("format", "unknown"),
                "output_file": export_result.get("filepath", "N/A"),
                "file_size_mb": export_result.get("file_size_mb", 0)
            }
        else:
            report["status"] = "failed"
            report["error"] = export_result.get("error", "未知错误")
        
        # 保存报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.output_dir, f"export_report_{timestamp}.json")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 导出报告已保存: {report_file}")
        
        return report


# 测试函数
def test_export():
    """测试导出功能"""
    print("🧪 测试PDD数据导出器...")
    
    # 创建测试数据
    test_positions = [
        {
            "position_id": "T015294",
            "position_name": "web前端高级开发工程师（广告投放&媒体运营方向）",
            "work_location": "上海",
            "position_category": "技术类",
            "update_time_str": "2026-05-21",
            "update_timestamp": 1779352494000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/T015294"
        },
        {
            "position_id": "PL023658",
            "position_name": "商品合规审核",
            "work_location": "上海",
            "position_category": "平台管理类",
            "update_time_str": "2026-05-21",
            "update_timestamp": 1779339762000,
            "detail_url": "https://careers.pddglobalhr.com/jobs/PL023658"
        }
    ]
    
    # 创建导出器
    exporter = PddDataExporter()
    
    # 测试导出
    print(f"  导出 {len(test_positions)} 个测试岗位...")
    
    # 测试JSON导出
    result_json = exporter.export_positions(test_positions, format="json")
    print(f"  JSON导出: {'✅ 成功' if result_json.get('success') else '❌ 失败'}")
    
    # 测试Excel导出（如果夸克框架可用）
    if exporter.use_quark_framework:
        result_excel = exporter.export_positions(test_positions, format="excel")
        print(f"  Excel导出: {'✅ 成功' if result_excel.get('success') else '❌ 失败'}")
    
    # 生成报告
    report = exporter.generate_export_report(result_json)
    print(f"  报告状态: {report.get('status', 'unknown')}")
    
    return result_json


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    result = test_export()
    
    if result.get("success"):
        print("\n✅ PDD数据导出器测试通过")
        sys.exit(0)
    else:
        print(f"\n❌ PDD数据导出器测试失败: {result.get('error')}")
        sys.exit(1)