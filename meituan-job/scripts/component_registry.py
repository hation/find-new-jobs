#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组件注册和依赖检查系统
防止夸克模板项目中的集成问题
"""

import os
import sys
import json
import importlib
import inspect
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComponentRegistry:
    """组件注册系统"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.components = {}
        self.dependencies = {}
        self.load_components()
    
    def load_components(self):
        """自动发现项目中的组件"""
        logger.info("🔍 扫描项目组件...")
        
        # 扫描src目录
        src_dir = os.path.join(self.project_root, "src")
        if not os.path.exists(src_dir):
            logger.warning(f"❌ src目录不存在: {src_dir}")
            return
        
        # 查找所有Python文件
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    module_path = os.path.relpath(os.path.join(root, file), src_dir)
                    module_name = module_path.replace("/", ".").replace(".py", "")
                    
                    # 跳过框架目录
                    if module_name.startswith("framework."):
                        continue
                    
                    # 尝试导入模块并发现组件
                    self.discover_components_in_module(module_name)
    
    def discover_components_in_module(self, module_name: str):
        """发现模块中的组件"""
        try:
            module = importlib.import_module(f"src.{module_name}")
            
            # 查找类定义
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # 检查是否是组件（根据命名约定）
                if name.endswith("Crawler") or name.endswith("Exporter") or name.endswith("Selector"):
                    component_info = {
                        "module": module_name,
                        "class": name,
                        "type": self._classify_component(name),
                        "methods": [m for m in dir(obj) if not m.startswith("_")],
                        "docstring": inspect.getdoc(obj) or ""
                    }
                    
                    self.components[name] = component_info
                    logger.info(f"✅ 发现组件: {name} ({component_info['type']})")
                    
        except Exception as e:
            logger.warning(f"⚠️ 无法导入模块 {module_name}: {e}")
    
    def _classify_component(self, class_name: str) -> str:
        """分类组件类型"""
        if "API" in class_name or "Api" in class_name:
            return "api_crawler"
        elif "Browser" in class_name:
            return "browser_crawler"
        elif "Exporter" in class_name:
            return "data_exporter"
        elif "Selector" in class_name:
            return "crawler_selector"
        else:
            return "unknown"
    
    def check_integration(self) -> Dict[str, Any]:
        """检查组件集成状态"""
        logger.info("🔧 检查组件集成状态...")
        
        results = {
            "missing_components": [],
            "unused_components": [],
            "integration_issues": [],
            "dependency_issues": []
        }
        
        # 1. 检查智能爬取器是否引用了所有必要的组件
        selector_path = os.path.join(self.project_root, "src", "meituan_crawler.py")
        if os.path.exists(selector_path):
            with open(selector_path, "r", encoding="utf-8") as f:
                selector_code = f.read()
            
            # 检查是否引用了API爬取器
            if "MeituanAPICrawler" in self.components:
                if "MeituanAPICrawler" not in selector_code:
                    results["integration_issues"].append({
                        "component": "MeituanAPICrawler",
                        "issue": "未在智能爬取器中引用",
                        "severity": "high"
                    })
            
            # 检查是否引用了浏览器爬取器
            browser_components = [c for c in self.components.keys() if "Browser" in c]
            for browser_component in browser_components:
                if browser_component not in selector_code:
                    results["integration_issues"].append({
                        "component": browser_component,
                        "issue": "未在智能爬取器中引用",
                        "severity": "medium"
                    })
        
        # 2. 检查组件之间的依赖关系
        for component_name, component_info in self.components.items():
            if component_info["type"] == "api_crawler":
                # API爬取器应该被智能爬取器引用
                if not self._is_component_referenced(component_name):
                    results["unused_components"].append({
                        "component": component_name,
                        "type": component_info["type"],
                        "issue": "组件已实现但未被引用"
                    })
        
        return results
    
    def _is_component_referenced(self, component_name: str) -> bool:
        """检查组件是否被其他文件引用"""
        # 检查主要入口文件
        entry_files = [
            "src/meituan_crawler.py",
            "src/main.py",
            "scripts/test_meituan_small.py"
        ]
        
        for file_path in entry_files:
            full_path = os.path.join(self.project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if component_name in content:
                        return True
        
        return False
    
    def generate_fix_suggestions(self, issues: Dict[str, Any]) -> List[str]:
        """生成修复建议"""
        suggestions = []
        
        for issue in issues.get("integration_issues", []):
            if issue["component"] == "MeituanAPICrawler":
                suggestions.append(f"""
🔧 修复建议: 在智能爬取器中集成 {issue['component']}

1. 在 src/meituan_crawler.py 中添加导入:
```python
from meituan_api_crawler import MeituanAPICrawler
```

2. 在 _initialize_primary_crawler() 方法中使用:
```python
self.primary_crawler = MeituanAPICrawler()
```

3. 在 _initialize_fallback_crawler() 方法中添加浏览器爬取器（如果存在）
""")
        
        for unused in issues.get("unused_components", []):
            suggestions.append(f"""
⚠️ 警告: {unused['component']} ({unused['type']}) 已实现但未被引用

建议:
1. 检查是否需要此组件
2. 如果不需要，考虑删除文件
3. 如果需要，在智能爬取器中引用它
""")
        
        return suggestions
    
    def run_validation(self):
        """运行完整的验证"""
        logger.info("=" * 60)
        logger.info("🔍 夸克模板项目组件验证")
        logger.info("=" * 60)
        
        # 发现组件
        self.load_components()
        
        # 检查集成
        issues = self.check_integration()
        
        # 显示结果
        logger.info(f"\n📊 发现 {len(self.components)} 个组件:")
        for name, info in self.components.items():
            logger.info(f"  • {name} ({info['type']})")
        
        if issues["integration_issues"]:
            logger.info(f"\n🚨 发现 {len(issues['integration_issues'])} 个集成问题:")
            for issue in issues["integration_issues"]:
                logger.info(f"  • {issue['component']}: {issue['issue']} ({issue['severity']})")
        
        if issues["unused_components"]:
            logger.info(f"\n⚠️ 发现 {len(issues['unused_components'])} 个未使用组件:")
            for unused in issues["unused_components"]:
                logger.info(f"  • {unused['component']}: {unused['issue']}")
        
        # 生成修复建议
        suggestions = self.generate_fix_suggestions(issues)
        if suggestions:
            logger.info("\n💡 修复建议:")
            for suggestion in suggestions:
                logger.info(suggestion)
        
        # 总结
        total_issues = len(issues["integration_issues"]) + len(issues["unused_components"])
        if total_issues == 0:
            logger.info("\n✅ 所有组件集成正常！")
        else:
            logger.info(f"\n🔧 需要修复 {total_issues} 个问题")
        
        return issues


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    registry = ComponentRegistry(project_root)
    
    # 运行验证
    issues = registry.run_validation()
    
    # 保存结果到文件
    output_file = os.path.join(project_root, "logs", "component_validation.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "components": registry.components,
            "issues": issues
        }, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n📁 验证结果已保存到: {output_file}")
    
    # 返回退出码
    total_issues = len(issues["integration_issues"]) + len(issues["unused_components"])
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    import time
    main()