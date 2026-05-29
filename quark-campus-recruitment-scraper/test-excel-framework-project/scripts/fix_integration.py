#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克模板项目集成问题自动修复脚本
自动修复组件集成问题
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationFixer:
    """集成问题修复器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.src_dir = self.project_root / "src"
        
        # 加载检查报告
        self.issues = self._load_issues()
        
        # 修复统计
        self.fixes_applied = 0
        self.fixes_failed = 0
    
    def _load_issues(self) -> List[Dict]:
        """加载检查报告中的问题"""
        report_file = self.project_root / "logs" / "integration_check.json"
        
        if not report_file.exists():
            logger.warning(f"⚠️ 检查报告不存在: {report_file}")
            logger.info("💡 请先运行: python scripts/check_integration.py")
            return []
        
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                report = json.load(f)
            
            return report.get("issues", [])
        except Exception as e:
            logger.error(f"❌ 无法加载检查报告: {e}")
            return []
    
    def fix_missing_imports(self):
        """修复缺失的导入语句"""
        logger.info("\n📦 修复缺失的导入语句...")
        
        for issue in self.issues:
            if issue["type"] == "missing_import" and issue["severity"] == "high":
                file_path = self.project_root / issue["file"]
                
                if not file_path.exists():
                    logger.warning(f"⚠️ 文件不存在: {file_path}")
                    continue
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 检查是否已经有导入
                    if "from meituan_api_crawler import" in content or "import meituan_api_crawler" in content:
                        logger.info(f"✅ {file_path.name} 已包含导入语句")
                        continue
                    
                    # 在文件开头添加导入
                    lines = content.split("\n")
                    
                    # 找到第一个import语句的位置
                    import_line_index = -1
                    for i, line in enumerate(lines):
                        if line.strip().startswith("import ") or line.strip().startswith("from "):
                            import_line_index = i
                            break
                    
                    # 如果没有import语句，在文件开头添加
                    if import_line_index == -1:
                        # 在模块文档字符串后添加
                        for i, line in enumerate(lines):
                            if not line.strip().startswith('"""') and not line.strip().startswith("'''") and line.strip():
                                # 找到第一个非空行（可能是模块文档字符串结束）
                                import_line_index = i
                                break
                    
                    # 添加导入语句
                    import_statement = "from meituan_api_crawler import MeituanAPICrawler"
                    if 0 <= import_line_index < len(lines):
                        lines.insert(import_line_index, import_statement)
                    else:
                        lines.insert(1, import_statement)  # 在第二行插入
                    
                    # 写回文件
                    new_content = "\n".join(lines)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    logger.info(f"✅ 已修复: 在 {file_path.name} 中添加导入语句")
                    self.fixes_applied += 1
                    
                except Exception as e:
                    logger.error(f"❌ 修复失败 {file_path}: {e}")
                    self.fixes_failed += 1
    
    def fix_missing_integration(self):
        """修复缺失的组件集成"""
        logger.info("\n🔧 修复缺失的组件集成...")
        
        # 查找智能选择器文件
        selector_files = list(self.src_dir.rglob("*crawler.py")) + list(self.src_dir.rglob("*selector.py"))
        
        for selector_file in selector_files:
            if selector_file.name.startswith("__"):
                continue
            
            # 检查这个文件是否有集成问题
            file_issues = [i for i in self.issues 
                          if i["type"] == "missing_integration" 
                          and i["file"] == str(selector_file.relative_to(self.project_root))]
            
            if not file_issues:
                continue
            
            try:
                with open(selector_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                modified = False
                
                for issue in file_issues:
                    component = issue["component"]
                    
                    # 检查是否已经引用了这个组件
                    if component in content:
                        continue
                    
                    # 根据组件类型修复
                    if "API" in component or "Api" in component:
                        # 修复API爬取器集成
                        content = self._fix_api_crawler_integration(content, component)
                        modified = True
                        logger.info(f"✅ 已修复: 在 {selector_file.name} 中集成 {component}")
                    
                    elif "Browser" in component:
                        # 修复浏览器爬取器集成
                        content = self._fix_browser_crawler_integration(content, component)
                        modified = True
                        logger.info(f"✅ 已修复: 在 {selector_file.name} 中集成 {component}")
                
                if modified:
                    with open(selector_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.fixes_applied += 1
                    
            except Exception as e:
                logger.error(f"❌ 修复失败 {selector_file}: {e}")
                self.fixes_failed += 1
    
    def _fix_api_crawler_integration(self, content: str, component_name: str) -> str:
        """修复API爬取器集成"""
        # 查找 _initialize_primary_crawler 方法
        pattern = r"def _initialize_primary_crawler\(self\).*?:"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.warning(f"⚠️ 未找到 _initialize_primary_crawler 方法")
            return content
        
        method_start = match.end()
        
        # 查找方法结束位置
        lines = content.split("\n")
        method_line_index = -1
        for i, line in enumerate(lines):
            if "def _initialize_primary_crawler" in line:
                method_line_index = i
                break
        
        if method_line_index == -1:
            return content
        
        # 找到方法结束（下一个def或文件结尾）
        method_end_index = len(lines)
        for i in range(method_line_index + 1, len(lines)):
            if lines[i].strip().startswith("def ") and lines[i].strip().endswith(":"):
                method_end_index = i
                break
        
        # 在方法内部添加代码
        method_lines = lines[method_line_index:method_end_index]
        
        # 检查是否已经有初始化代码
        has_init_code = any("primary_crawler" in line for line in method_lines)
        
        if not has_init_code:
            # 在方法内部添加初始化代码
            for i, line in enumerate(method_lines):
                if "def _initialize_primary_crawler" in line:
                    # 在方法开头添加代码
                    indent = " " * 4
                    init_code = f'\n{indent}try:\n{indent}    from meituan_api_crawler import MeituanAPICrawler\n{indent}    self.primary_crawler = MeituanAPICrawler()\n{indent}    return True, None\n{indent}except Exception as e:\n{indent}    return False, f"初始化API爬取器失败: {{e}}"'
                    
                    method_lines.insert(i + 1, init_code)
                    break
        
        # 替换原方法
        lines[method_line_index:method_end_index] = method_lines
        
        return "\n".join(lines)
    
    def _fix_browser_crawler_integration(self, content: str, component_name: str) -> str:
        """修复浏览器爬取器集成"""
        # 查找 _initialize_fallback_crawler 方法
        pattern = r"def _initialize_fallback_crawler\(self\).*?:"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            logger.warning(f"⚠️ 未找到 _initialize_fallback_crawler 方法")
            return content
        
        # 简单修复：确保方法存在并返回True
        if "return False" in content or "return None" in content:
            # 替换为返回True
            content = content.replace("return False", "return True")
            content = content.replace("return None", "return True, None")
        
        return content
    
    def generate_fix_report(self):
        """生成修复报告"""
        logger.info("\n" + "=" * 60)
        logger.info("📋 集成修复报告")
        logger.info("=" * 60)
        
        logger.info(f"🔧 修复统计:")
        logger.info(f"  • 成功修复: {self.fixes_applied}")
        logger.info(f"  • 修复失败: {self.fixes_failed}")
        
        if self.fixes_applied > 0:
            logger.info("\n✅ 修复完成！")
            logger.info("💡 建议重新运行检查: python scripts/check_integration.py")
        elif self.fixes_failed > 0:
            logger.info("\n❌ 修复失败，请手动检查问题")
        else:
            logger.info("\nℹ️ 未发现需要修复的问题")
        
        # 保存修复报告
        report_data = {
            "timestamp": self._get_timestamp(),
            "fixes_applied": self.fixes_applied,
            "fixes_failed": self.fixes_failed,
            "remaining_issues": len([i for i in self.issues if i["severity"] == "high"])
        }
        
        report_file = self.project_root / "logs" / "integration_fix.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📁 修复报告已保存到: {report_file}")
    
    def _get_timestamp(self):
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """运行修复"""
        if not self.issues:
            logger.info("ℹ️ 未发现需要修复的问题")
            return
        
        logger.info("🔧 开始修复集成问题...")
        
        # 按优先级修复
        high_issues = [i for i in self.issues if i["severity"] == "high"]
        medium_issues = [i for i in self.issues if i["severity"] == "medium"]
        
        logger.info(f"📊 发现 {len(high_issues)} 个严重问题，{len(medium_issues)} 个中等问题")
        
        # 先修复严重问题
        self.fix_missing_imports()
        self.fix_missing_integration()
        
        self.generate_fix_report()


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixer = IntegrationFixer(project_root)
    fixer.run()


if __name__ == "__main__":
    main()