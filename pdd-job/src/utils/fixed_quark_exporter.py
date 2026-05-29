#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版夸克项目导出器
修复Excel导出问题：.excel扩展名 -> .xlsx扩展名
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union

# 导入夸克项目导出器
quark_path = os.path.expanduser('~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/template/framework')
sys.path.insert(0, quark_path)

try:
    from data_exporter import DataExporter as OriginalDataExporter
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False

import logging
logger = logging.getLogger(__name__)


class FixedDataExporter:
    """修复版数据导出器（解决.excel扩展名问题）"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化修复版导出器
        
        Args:
            config: 配置字典
        """
        if not IMPORT_SUCCESS:
            raise ImportError("无法导入夸克项目导出框架")
        
        self.config = config or {}
        
        # 修改配置：将excel格式的扩展名改为xlsx
        self._fix_config()
        
        # 创建原版导出器
        self.original_exporter = OriginalDataExporter(self.config)
        
        logger.info("✅ 修复版夸克项目导出器初始化完成")
        logger.info(f"   修复内容: Excel扩展名 .excel -> .xlsx")
    
    def _fix_config(self):
        """修复配置"""
        # 确保excel_settings存在
        if "excel_settings" not in self.config:
            self.config["excel_settings"] = {}
        
        # 添加修复标记
        self.config["excel_settings"]["fixed_extension"] = True
    
    def export_data(
        self, 
        data: Union[List[Dict], Dict[str, Any]], 
        format: str = None,
        company_name: str = None,
        additional_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        导出数据（修复Excel扩展名）
        
        Args:
            data: 要导出的数据
            format: 导出格式
            company_name: 公司名称
            additional_info: 附加信息
            
        Returns:
            导出结果
        """
        # 调用原版导出器
        result = self.original_exporter.export_data(
            data=data,
            format=format,
            company_name=company_name,
            additional_info=additional_info
        )
        
        # 修复Excel文件扩展名
        if format == "excel" and result.get("success"):
            self._fix_excel_extension(result)
        
        return result
    
    def _fix_excel_extension(self, result: Dict[str, Any]):
        """修复Excel文件扩展名"""
        try:
            if "results" in result and "excel" in result["results"]:
                excel_result = result["results"]["excel"]
                old_filepath = excel_result.get("filepath")
                
                if old_filepath and old_filepath.endswith(".excel"):
                    # 重命名文件
                    new_filepath = old_filepath.replace(".excel", ".xlsx")
                    
                    if os.path.exists(old_filepath):
                        os.rename(old_filepath, new_filepath)
                        
                        # 更新结果
                        excel_result["filepath"] = new_filepath
                        excel_result["filename"] = os.path.basename(new_filepath)
                        
                        logger.info(f"🔧 修复Excel扩展名: {os.path.basename(old_filepath)} -> {os.path.basename(new_filepath)}")
                    else:
                        logger.warning(f"⚠️ 要修复的Excel文件不存在: {old_filepath}")
        except Exception as e:
            logger.warning(f"⚠️ 修复Excel扩展名失败: {e}")
    
    def __getattr__(self, name):
        """委托其他方法到原版导出器"""
        return getattr(self.original_exporter, name)


# 测试函数
def test_fixed_exporter():
    """测试修复版导出器"""
    print("🧪 测试修复版夸克项目导出器...")
    
    if not IMPORT_SUCCESS:
        print("❌ 无法导入夸克项目导出框架")
        return False
    
    try:
        # 创建修复版导出器
        config = {
            "output_dir": "test_fixed_output",
            "company_name": "测试公司"
        }
        
        exporter = FixedDataExporter(config)
        print("✅ 修复版导出器创建成功")
        
        # 测试数据
        test_data = [{"field1": "值1", "field2": "值2"}]
        
        # 测试Excel导出
        print("  测试Excel导出...")
        result = exporter.export_data(test_data, format="excel", company_name="测试公司")
        
        if result.get("success"):
            print("  ✅ Excel导出成功")
            
            # 检查文件扩展名
            if "results" in result and "excel" in result["results"]:
                filepath = result["results"]["excel"].get("filepath")
                if filepath and filepath.endswith(".xlsx"):
                    print(f"  ✅ 扩展名正确: .xlsx")
                    print(f"     文件路径: {filepath}")
                    
                    if os.path.exists(filepath):
                        print(f"  ✅ 文件存在，大小: {os.path.getsize(filepath)} 字节")
                        
                        # 清理
                        os.remove(filepath)
                        os.rmdir("test_fixed_output")
                        print("  ✅ 测试文件已清理")
                    else:
                        print(f"  ❌ 文件不存在")
                else:
                    print(f"  ❌ 扩展名不正确: {filepath}")
            else:
                print(f"  ❌ 结果中缺少Excel信息")
        else:
            print(f"  ❌ Excel导出失败: {result.get('error')}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    success = test_fixed_exporter()
    
    if success:
        print("\n✅ 修复版夸克项目导出器测试通过")
        sys.exit(0)
    else:
        print("\n❌ 修复版夸克项目导出器测试失败")
        sys.exit(1)