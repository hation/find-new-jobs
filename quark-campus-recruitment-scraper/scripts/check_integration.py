"""
防止组件集成问题
来自: 蚂蚁国际招聘爬取项目
复制时间: 2026-05-22 13:10:22
"""
"""
防止组件集成问题
来自: 美团招聘爬取项目
复制时间: 2026-05-22 09:55:51
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克模板项目集成检查脚本
自动检查组件集成问题，防止"已实现但未集成"问题
"""

import os
import sys
import ast
import json
import logging
from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationChecker:
    """集成检查器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        self.scripts_dir = self.project_root / "scripts"
        
        # 组件映射
        self.components = {
            "api_crawlers": set(),
            "browser_crawlers": set(),
            "exporters": set(),
            "selectors": set(),
            "other_components": set()
        }
        
        # 依赖关系
        self.dependencies = {}
        
        # 问题记录
        self.issues = []
    
    def discover_components(self):
        """发现项目中的所有组件"""
        logger.info("🔍 发现项目组件...")
        
        if not self.src_dir.exists():
            logger.error(f"❌ src目录不存在: {self.src_dir}")
            return
        
        # 扫描Python文件
        for py_file in self.src_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            # 解析Python文件
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    tree = ast.parse(content)
                
                # 查找类定义
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        relative_path = py_file.relative_to(self.src_dir)
                        
                        # 分类组件
                        component_type = self._classify_component(class_name, str(relative_path))
                        
                        # 添加到对应集合
                        if component_type == "api_crawler":
                            self.components["api_crawlers"].add(class_name)
                        elif component_type == "browser_crawler":
                            self.components["browser_crawlers"].add(class_name)
                        elif component_type == "exporter":
                            self.components["exporters"].add(class_name)
                        elif component_type == "selector":
                            self.components["selectors"].add(class_name)
                        else:
                            self.components["other_components"].add(class_name)
                        
                        # 记录依赖关系
                        self.dependencies[class_name] = {
                            "file": str(relative_path),
                            "type": component_type,
                            "imports": self._extract_imports(tree)
                        }
                        
                        logger.info(f"✅ 发现组件: {class_name} ({component_type}) in {relative_path}")
                        
            except Exception as e:
                logger.warning(f"⚠️ 无法解析文件 {py_file}: {e}")
    
    def _classify_component(self, class_name: str, file_path: str) -> str:
        """分类组件类型"""
        class_lower = class_name.lower()
        file_lower = file_path.lower()
        
        if "api" in class_lower or "api" in file_lower:
            return "api_crawler"
        elif "browser" in class_lower or "browser" in file_lower:
            return "browser_crawler"
        elif "exporter" in class_lower or "export" in class_lower:
            return "exporter"
        elif "selector" in class_lower or "crawler" in class_lower:
            return "selector"
        elif "smart" in class_lower:
            return "selector"
        else:
            return "other"
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """提取导入语句"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        
        return imports
    
    def check_smart_selector_integration(self):
        """检查智能选择器是否集成了所有组件"""
        logger.info("\n🔧 检查智能选择器集成...")
        
        # 查找智能选择器文件
        selector_files = []
        for pattern in ["*crawler.py", "*selector.py", "main.py"]:
            selector_files.extend(self.src_dir.rglob(pattern))
        
        for selector_file in selector_files:
            if selector_file.name.startswith("__"):
                continue
            
            try:
                with open(selector_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 检查是否引用了API爬取器（只检查业务文件，不检查框架文件）
                if "framework" not in str(selector_file) and selector_file.name != "main.py":
                    for api_crawler in self.components["api_crawlers"]:
                        if api_crawler in content:
                            logger.info(f"✅ {selector_file.name} 引用了API爬取器: {api_crawler}")
                        else:
                            self.issues.append({
                                "type": "missing_integration",
                                "component": api_crawler,
                                "file": str(selector_file.relative_to(self.project_root)),
                                "severity": "high",
                                "description": f"智能选择器未引用已实现的API爬取器 {api_crawler}"
                            })
                            logger.warning(f"⚠️ {selector_file.name} 未引用API爬取器: {api_crawler}")
                
                # 检查是否引用了浏览器爬取器
                for browser_crawler in self.components["browser_crawlers"]:
                    if browser_crawler in content:
                        logger.info(f"✅ {selector_file.name} 引用了浏览器爬取器: {browser_crawler}")
                    else:
                        self.issues.append({
                            "type": "missing_integration",
                            "component": browser_crawler,
                            "file": str(selector_file.relative_to(self.project_root)),
                            "severity": "medium",
                            "description": f"智能选择器未引用已实现的浏览器爬取器 {browser_crawler}"
                        })
                        logger.warning(f"⚠️ {selector_file.name} 未引用浏览器爬取器: {browser_crawler}")
                
            except Exception as e:
                logger.error(f"❌ 无法检查文件 {selector_file}: {e}")
    
    def check_unused_components(self):
        """检查未使用的组件"""
        logger.info("\n📊 检查未使用组件...")
        
        # 收集所有被引用的组件
        referenced_components = set()
        
        # 检查所有Python文件
        for py_file in self.project_root.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 检查每个组件是否被引用
                for component_type, components in self.components.items():
                    for component in components:
                        if component in content and py_file.name != f"{component.lower()}.py":
                            referenced_components.add(component)
                            
            except Exception as e:
                logger.warning(f"⚠️ 无法读取文件 {py_file}: {e}")
        
        # 找出未使用的组件
        all_components = set()
        for components in self.components.values():
            all_components.update(components)
        
        unused_components = all_components - referenced_components
        
        for component in unused_components:
            # 查找组件文件
            component_file = None
            for comp_name, comp_info in self.dependencies.items():
                if comp_name == component:
                    component_file = comp_info["file"]
                    break
            
            self.issues.append({
                "type": "unused_component",
                "component": component,
                "file": component_file or "unknown",
                "severity": "low",
                "description": f"组件 {component} 已实现但未被任何文件引用"
            })
            logger.warning(f"⚠️ 未使用组件: {component} ({component_file})")
    
    def check_import_statements(self):
        """检查导入语句是否正确"""
        logger.info("\n📦 检查导入语句...")
        
        # 检查智能选择器是否导入了必要的组件
        selector_file = self.src_dir / "meituan_crawler.py"
        if selector_file.exists():
            try:
                with open(selector_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 检查是否导入了API爬取器
                if "from meituan_api_crawler import" not in content and "import meituan_api_crawler" not in content:
                    self.issues.append({
                        "type": "missing_import",
                        "component": "meituan_api_crawler",
                        "file": "src/meituan_crawler.py",
                        "severity": "high",
                        "description": "智能选择器未导入API爬取器模块",
                        "fix": "添加: from meituan_api_crawler import MeituanAPICrawler"
                    })
                    logger.warning("⚠️ 智能选择器未导入API爬取器模块")
                else:
                    logger.info("✅ 智能选择器已导入API爬取器模块")
                    
            except Exception as e:
                logger.error(f"❌ 无法检查导入语句: {e}")
    
    def generate_report(self):
        """生成检查报告"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 集成检查报告")
        logger.info("=" * 60)
        
        # 组件统计
        total_components = sum(len(comps) for comps in self.components.values())
        logger.info(f"📊 组件统计:")
        logger.info(f"  • API爬取器: {len(self.components['api_crawlers'])}")
        logger.info(f"  • 浏览器爬取器: {len(self.components['browser_crawlers'])}")
        logger.info(f"  • 数据导出器: {len(self.components['exporters'])}")
        logger.info(f"  • 智能选择器: {len(self.components['selectors'])}")
        logger.info(f"  • 其他组件: {len(self.components['other_components'])}")
        logger.info(f"  • 总计: {total_components}")
        
        # 问题统计
        high_issues = [i for i in self.issues if i["severity"] == "high"]
        medium_issues = [i for i in self.issues if i["severity"] == "medium"]
        low_issues = [i for i in self.issues if i["severity"] == "low"]
        
        logger.info(f"\n🚨 问题统计:")
        logger.info(f"  • 严重问题: {len(high_issues)}")
        logger.info(f"  • 中等问题: {len(medium_issues)}")
        logger.info(f"  • 轻微问题: {len(low_issues)}")
        logger.info(f"  • 总计: {len(self.issues)}")
        
        # 显示严重问题
        if high_issues:
            logger.info("\n🔴 严重问题:")
            for issue in high_issues:
                logger.info(f"  • {issue['component']}: {issue['description']}")
                if "fix" in issue:
                    logger.info(f"    修复: {issue['fix']}")
        
        # 显示中等问题
        if medium_issues:
            logger.info("\n🟡 中等问题:")
            for issue in medium_issues:
                logger.info(f"  • {issue['component']}: {issue['description']}")
        
        # 生成修复建议
        if self.issues:
            logger.info("\n💡 修复建议:")
            logger.info("1. 运行修复脚本: python scripts/fix_integration.py")
            logger.info("2. 手动检查并修复上述问题")
            logger.info("3. 重新运行检查: python scripts/check_integration.py")
        
        # 保存报告
        report_data = {
            "timestamp": self._get_timestamp(),
            "components": {k: list(v) for k, v in self.components.items()},
            "issues": self.issues,
            "summary": {
                "total_components": total_components,
                "high_issues": len(high_issues),
                "medium_issues": len(medium_issues),
                "low_issues": len(low_issues),
                "total_issues": len(self.issues)
            }
        }
        
        report_file = self.project_root / "logs" / "integration_check.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📁 报告已保存到: {report_file}")
        
        # 返回退出码
        if len(high_issues) > 0:
            logger.info("\n❌ 检查失败: 存在严重问题需要修复")
            return 1
        elif len(self.issues) > 0:
            logger.info("\n⚠️ 检查警告: 存在问题但可以继续")
            return 2
        else:
            logger.info("\n✅ 检查通过: 所有组件集成正常")
            return 0
    
    def _get_timestamp(self):
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """运行检查"""
        self.discover_components()
        self.check_smart_selector_integration()
        self.check_unused_components()
        self.check_import_statements()
        return self.generate_report()


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    checker = IntegrationChecker(project_root)
    
    exit_code = checker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()