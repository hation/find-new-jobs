#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Excel生成脚本
基于anti-job和jd-job经验沉淀

【功能】
1. 将任意格式的招聘数据转换为统一Excel格式
2. 自动数据清洗和格式化
3. 生成7个工作表（所有岗位+6个统计分析表+数据摘要）
4. 质量验证和报告生成

【使用场景】
1. 新项目：直接生成统一格式Excel
2. 历史项目：转换旧格式到统一格式
3. 数据验证：验证数据质量和格式
4. 批量处理：批量转换多个数据文件

【核心特点】
- 完全匹配anti-job格式（16列，7个工作表）
- 自动化数据清洗和提取
- 完整的质量验证体系
- 错误处理和恢复机制
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import logging

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from framework.unified_excel_exporter import UnifiedExcelExporter
from utils.data_extractors import DataExtractor

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/unified_excel_generator.log')
    ]
)

logger = logging.getLogger(__name__)


class UnifiedExcelGenerator:
    """统一Excel生成器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化统一Excel生成器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.extractor = DataExtractor()
        self.exporter = None
        
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logger.info("🚀 统一Excel生成器初始化完成")
    
    def _load_config(self, config_path: str) -> dict:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        default_config = {
            "company_name": "未知公司",
            "company_website": "",
            "output_dir": "output/unified_excel",
            "quality_config": {
                "min_completeness": 0.8,
                "auto_validation": True,
                "generate_csv": True
            },
            "excel_settings": {
                "include_sheets": [
                    "所有岗位",
                    "地点分布",
                    "类别分布",
                    "学历分布",
                    "部门分布",
                    "经验要求",
                    "数据摘要"
                ],
                "auto_adjust_columns": True,
                "freeze_panes": True
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                default_config.update(user_config)
                logger.info(f"✅ 已加载配置文件: {config_path}")
            except Exception as e:
                logger.warning(f"⚠️ 加载配置文件失败，使用默认配置: {e}")
        
        return default_config
    
    def load_data_from_json(self, json_path: str) -> list:
        """
        从JSON文件加载数据
        
        Args:
            json_path: JSON文件路径
            
        Returns:
            数据列表
        """
        logger.info(f"📂 从JSON文件加载数据: {json_path}")
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 处理不同格式的JSON
            if isinstance(data, dict):
                if "positions" in data:
                    positions = data["positions"]
                elif "data" in data:
                    positions = data["data"]
                else:
                    positions = [data]
            elif isinstance(data, list):
                positions = data
            else:
                positions = []
            
            logger.info(f"✅ 成功加载 {len(positions)} 条数据")
            return positions
            
        except Exception as e:
            logger.error(f"❌ 加载JSON文件失败: {e}")
            return []
    
    def load_data_from_excel(self, excel_path: str) -> list:
        """
        从Excel文件加载数据
        
        Args:
            excel_path: Excel文件路径
            
        Returns:
            数据列表
        """
        logger.info(f"📂 从Excel文件加载数据: {excel_path}")
        
        try:
            df = pd.read_excel(excel_path)
            positions = df.to_dict('records')
            
            logger.info(f"✅ 成功加载 {len(positions)} 条数据")
            return positions
            
        except Exception as e:
            logger.error(f"❌ 加载Excel文件失败: {e}")
            return []
    
    def load_data_from_directory(self, data_dir: str, pattern: str = "*.json") -> list:
        """
        从目录加载多个数据文件
        
        Args:
            data_dir: 数据目录
            pattern: 文件匹配模式
            
        Returns:
            合并后的数据列表
        """
        logger.info(f"📂 从目录加载数据: {data_dir}")
        
        data_dir = Path(data_dir)
        if not data_dir.exists():
            logger.error(f"❌ 数据目录不存在: {data_dir}")
            return []
        
        all_positions = []
        
        # 查找所有匹配的文件
        for file_path in data_dir.glob(pattern):
            if file_path.suffix == '.json':
                positions = self.load_data_from_json(str(file_path))
            elif file_path.suffix in ['.xlsx', '.xls']:
                positions = self.load_data_from_excel(str(file_path))
            else:
                logger.warning(f"⚠️ 跳过不支持的文件格式: {file_path}")
                continue
            
            all_positions.extend(positions)
            logger.info(f"   已添加 {len(positions)} 条数据从 {file_path.name}")
        
        logger.info(f"✅ 从目录加载完成，共 {len(all_positions)} 条数据")
        return all_positions
    
    def clean_and_validate_data(self, positions: list) -> tuple:
        """
        清洗和验证数据
        
        Args:
            positions: 原始数据列表
            
        Returns:
            (清洗后的数据, 质量报告)
        """
        logger.info("🔄 数据清洗和验证中...")
        
        if not positions:
            logger.warning("⚠️ 没有数据需要清洗")
            return [], {
                "status": "失败",
                "message": "没有数据",
                "total_records": 0,
                "completeness": 0.0
            }
        
        cleaned_positions = []
        validation_errors = []
        
        for i, position in enumerate(positions):
            try:
                # 清洗文本字段
                cleaned_position = {}
                for key, value in position.items():
                    if isinstance(value, str):
                        cleaned_position[key] = self.extractor.clean_text(value)
                    else:
                        cleaned_position[key] = value
                
                # 验证必填字段
                required_fields = ["position_id", "position_name", "work_location"]
                missing_fields = []
                
                for field in required_fields:
                    value = cleaned_position.get(field)
                    if not value or pd.isna(value) or str(value).strip() == "":
                        missing_fields.append(field)
                
                if missing_fields:
                    validation_errors.append({
                        "index": i,
                        "position_id": cleaned_position.get("position_id", "未知"),
                        "missing_fields": missing_fields
                    })
                    logger.warning(f"⚠️ 第 {i+1} 条数据缺失必填字段: {missing_fields}")
                
                cleaned_positions.append(cleaned_position)
                
            except Exception as e:
                logger.error(f"❌ 清洗第 {i+1} 条数据失败: {e}")
                validation_errors.append({
                    "index": i,
                    "error": str(e)
                })
        
        # 生成质量报告
        total_records = len(positions)
        valid_records = len(cleaned_positions)
        completeness = valid_records / total_records if total_records > 0 else 0.0
        
        quality_report = {
            "status": "通过" if completeness >= 0.8 else "警告" if completeness >= 0.5 else "失败",
            "message": f"数据清洗完成，有效记录: {valid_records}/{total_records}",
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": total_records - valid_records,
            "completeness": completeness,
            "completeness_percentage": f"{completeness * 100:.1f}%",
            "validation_errors": validation_errors,
            "error_count": len(validation_errors)
        }
        
        logger.info(f"📊 数据清洗完成:")
        logger.info(f"   总记录: {quality_report['total_records']}")
        logger.info(f"   有效记录: {quality_report['valid_records']}")
        logger.info(f"   完整率: {quality_report['completeness_percentage']}")
        logger.info(f"   错误数: {quality_report['error_count']}")
        
        return cleaned_positions, quality_report
    
    def generate_unified_excel(self, positions: list, output_path: str = None) -> dict:
        """
        生成统一格式的Excel文件
        
        Args:
            positions: 岗位数据列表
            output_path: 输出文件路径（可选）
            
        Returns:
            生成结果
        """
        logger.info(f"📤 开始生成统一Excel文件，共 {len(positions)} 个岗位")
        
        # 初始化导出器
        self.exporter = UnifiedExcelExporter(self.config)
        
        # 如果指定了输出路径，更新导出器配置
        if output_path:
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            self.exporter.output_dir = output_dir
        
        # 导出数据
        result = self.exporter.export_to_unified_excel(positions)
        
        return result
    
    def convert_legacy_excel(self, legacy_file_path: str, output_dir: str = None) -> dict:
        """
        转换旧格式Excel到统一格式
        
        Args:
            legacy_file_path: 旧格式Excel文件路径
            output_dir: 输出目录（可选）
            
        Returns:
            转换结果
        """
        logger.info(f"🔄 开始转换旧格式Excel: {legacy_file_path}")
        
        # 加载旧格式数据
        positions = self.load_data_from_excel(legacy_file_path)
        
        if not positions:
            return {
                "success": False,
                "error": "无法加载旧格式Excel数据",
                "file_path": None
            }
        
        # 清洗和验证数据
        cleaned_positions, quality_report = self.clean_and_validate_data(positions)
        
        if quality_report["status"] == "失败":
            logger.warning(f"⚠️ 数据质量检查失败，完整率: {quality_report['completeness_percentage']}")
        
        # 生成统一格式Excel
        result = self.generate_unified_excel(cleaned_positions, output_dir)
        
        # 添加转换信息
        if result["success"]:
            result["conversion_info"] = {
                "source_file": legacy_file_path,
                "original_records": len(positions),
                "cleaned_records": len(cleaned_positions),
                "quality_report": quality_report
            }
        
        return result
    
    def batch_convert_directory(self, source_dir: str, output_dir: str = None) -> list:
        """
        批量转换目录中的所有Excel文件
        
        Args:
            source_dir: 源目录
            output_dir: 输出目录（可选）
            
        Returns:
            转换结果列表
        """
        logger.info(f"🔄 开始批量转换目录: {source_dir}")
        
        source_dir = Path(source_dir)
        if not source_dir.exists():
            logger.error(f"❌ 源目录不存在: {source_dir}")
            return []
        
        # 查找所有Excel文件
        excel_files = list(source_dir.glob("*.xlsx")) + list(source_dir.glob("*.xls"))
        
        if not excel_files:
            logger.warning(f"⚠️ 目录中没有Excel文件: {source_dir}")
            return []
        
        results = []
        
        for excel_file in excel_files:
            logger.info(f"📄 处理文件: {excel_file.name}")
            
            # 转换单个文件
            result = self.convert_legacy_excel(str(excel_file), output_dir)
            result["source_file"] = str(excel_file)
            results.append(result)
            
            if result["success"]:
                logger.info(f"    ✅ 转换成功: {Path(result['file_path']).name}")
            else:
                logger.error(f"    ❌ 转换失败: {result.get('error')}")
        
        # 生成批量转换报告
        successful = sum(1 for r in results if r["success"])
        total = len(results)
        success_rate = successful / total if total > 0 else 0
        
        batch_report = {
            "total_files": total,
            "successful_files": successful,
            "failed_files": total - successful,
            "success_rate": success_rate,
            "success_rate_percentage": f"{success_rate * 100:.1f}%",
            "results": results
        }
        
        logger.info(f"📊 批量转换完成:")
        logger.info(f"   总文件: {batch_report['total_files']}")
        logger.info(f"   成功: {batch_report['successful_files']}")
        logger.info(f"   失败: {batch_report['failed_files']}")
        logger.info(f"   成功率: {batch_report['success_rate_percentage']}")
        
        return batch_report


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="统一Excel生成器")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--company", help="公司名称")
    parser.add_argument("--input", help="输入文件或目录路径")
    parser.add_argument("--output", help="输出目录路径")
    parser.add_argument("--mode", choices=["single", "batch", "convert"], 
                       default="single", help="运行模式")
    parser.add_argument("--format", choices=["json", "excel", "auto"], 
                       default="auto", help="输入文件格式")
    
    args = parser.parse_args()
    
    print("="*70)
    print("🚀 统一Excel生成器")
    print("="*70)
    print("基于anti-job和jd-job项目经验沉淀")
    print("生成完全一致的Excel格式（16列，7个工作表）")
    print()
    
    # 创建生成器实例
    generator = UnifiedExcelGenerator(args.config)
    
    # 如果指定了公司名称，更新配置
    if args.company:
        generator.config["company_name"] = args.company
        print(f"🎯 公司名称: {args.company}")
    
    # 根据模式执行
    if args.mode == "single":
        # 单个文件模式
        if not args.input:
            print("❌ 请指定输入文件路径 (--input)")
            return
        
        print(f"📂 输入文件: {args.input}")
        
        # 加载数据
        if args.format == "json" or (args.format == "auto" and args.input.endswith(".json")):
            positions = generator.load_data_from_json(args.input)
        else:
            positions = generator.load_data_from_excel(args.input)
        
        if not positions:
            print("❌ 无法加载数据，请检查输入文件")
            return
        
        # 生成统一Excel
        result = generator.generate_unified_excel(positions, args.output)
        
    elif args.mode == "batch":
        # 批量模式
        if not args.input:
            print("❌ 请指定输入目录路径 (--input)")
            return
        
        print(f"📂 输入目录: {args.input}")
        
        # 批量处理
        batch_report = generator.batch_convert_directory(args.input, args.output)
        
        if batch_report:
            result = {
                "success": batch_report["success_rate"] > 0.5,
                "batch_report": batch_report
            }
        else:
            result = {"success": False, "error": "批量处理失败"}
            
    elif args.mode == "convert":
        # 转换模式（旧格式转统一格式）
        if not args.input:
            print("❌ 请指定输入文件路径 (--input)")
            return
        
        print(f"🔄 转换文件: {args.input}")
        
        # 转换旧格式
        result = generator.convert_legacy_excel(args.input, args.output)
    
    else:
        print("❌ 未知模式，请使用 --help 查看帮助")
        return
    
    # 显示结果
    print()
    print("="*70)
    
    if result.get("success"):
        print("🎉 统一Excel生成成功!")
        print()
        
        if "file_path" in result:
            print(f"📁 文件位置: {result['file_path']}")
            print(f"📏 文件大小: {result.get('file_size_mb', 0):.2f} MB")
            print(f"📊 岗位数量: {result.get('total_positions', 0)} 个")
            print(f"📋 工作表: {len(result.get('sheets_created', []))} 个")
            print(f"📈 数据质量: {result.get('quality_report', {}).get('completeness_percentage', 'N/A')}")
        
        if "csv_file_path" in result and result["csv_file_path"]:
            print(f"📄 CSV文件: {result['csv_file_path']}")
        
        if "conversion_info" in result:
            print(f"\n🔄 转换信息:")
            info = result["conversion_info"]
            print(f"   源文件: {Path(info['source_file']).name}")
            print(f"   原始记录: {info['original_records']}")
            print(f"   清洗后记录: {info['cleaned_records']}")
            print(f"   质量状态: {info['quality_report']['status']}")
        
        if "batch_report" in result:
            print(f"\n📊 批量处理报告:")
            report = result["batch_report"]
            print(f"   总文件: {report['total_files']}")
            print(f"   成功: {report['successful_files']}")
            print(f"   失败: {report['failed_files']}")
            print(f"   成功率: {report['success_rate_percentage']}")
        
    else:
        print("❌ 统一Excel生成失败!")
        print()
        print(f"错误信息: {result.get('error', '未知错误')}")
    
    print()
    print("📝 详细日志请查看: logs/unified_excel_generator.log")
    print("="*70)


if __name__ == "__main__":
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 运行主函数
    main()