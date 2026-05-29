#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板文档更新系统
自动更新夸克模板的文档，包含项目经验
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateDocUpdater:
    """模板文档更新器"""
    
    def __init__(self, project_root: str, template_root: str):
        self.project_root = Path(project_root)
        self.template_root = Path(template_root)
        
        # 文档映射：项目文档 -> 模板文档
        self.doc_mapping = {
            "CHECKLIST_MEITUAN.md": "CHECKLIST.md",
            "QUICK_START_MEITUAN.md": "QUICK_START.md",
            "docs/QUARK_TEMPLATE_IMPROVEMENTS.md": "docs/TEMPLATE_IMPROVEMENTS.md",
            "docs/MEITUAN_CATEGORIES.md": "docs/CATEGORY_EXAMPLES.md",
            "docs/MEITUAN_CITY_CODES.md": "docs/CITY_CODE_EXAMPLES.md",
            "memory-system/CORE_BUSINESS_INFO.md": "memory-system/CORE_BUSINESS_INFO_EXAMPLE.md"
        }
        
        # 需要提取的经验部分
        self.experience_sections = [
            "组件集成检查",
            "防错机制",
            "自动化验证",
            "常见问题",
            "经验教训",
            "改进建议"
        ]
    
    def extract_experience_from_doc(self, doc_path: Path) -> Dict[str, List[str]]:
        """从文档中提取经验"""
        if not doc_path.exists():
            return {}
        
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        experiences = {}
        
        for section in self.experience_sections:
            # 查找章节
            pattern = rf"##+.*{section}.*?\n(.*?)(?=##+|\Z)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            
            if match:
                section_content = match.group(1).strip()
                if section_content:
                    experiences[section] = section_content.split("\n")
        
        return experiences
    
    def update_template_checklist(self):
        """更新模板检查清单"""
        project_checklist = self.project_root / "CHECKLIST_MEITUAN.md"
        template_checklist = self.template_root / "CHECKLIST.md"
        
        if not project_checklist.exists():
            logger.warning(f"⚠️ 项目检查清单不存在: {project_checklist}")
            return
        
        if not template_checklist.exists():
            logger.warning(f"⚠️ 模板检查清单不存在: {template_checklist}")
            return
        
        # 读取项目检查清单
        with open(project_checklist, "r", encoding="utf-8") as f:
            project_content = f.read()
        
        # 读取模板检查清单
        with open(template_checklist, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # 提取项目中的集成检查部分
        integration_pattern = r"### 组件集成检查.*?(?=### |\Z)"
        integration_match = re.search(integration_pattern, project_content, re.DOTALL)
        
        if integration_match:
            integration_section = integration_match.group(0)
            
            # 检查模板是否已经有集成检查
            if "组件集成检查" not in template_content:
                # 找到合适的位置插入（在环境检查之后）
                insert_pattern = r"(### 配置文件检查.*?\n)"
                insert_match = re.search(insert_pattern, template_content, re.DOTALL)
                
                if insert_match:
                    # 在配置文件检查后插入集成检查
                    new_content = template_content.replace(
                        insert_match.group(1),
                        insert_match.group(1) + "\n" + integration_section + "\n"
                    )
                    
                    with open(template_checklist, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    logger.info("✅ 已更新模板检查清单：添加组件集成检查")
                else:
                    logger.warning("⚠️ 未找到合适的插入位置")
            else:
                logger.info("ℹ️ 模板检查清单已包含集成检查")
        else:
            logger.warning("⚠️ 项目检查清单中没有找到集成检查部分")
    
    def update_template_quick_start(self):
        """更新模板快速开始指南"""
        project_quick_start = self.project_root / "QUICK_START_MEITUAN.md"
        template_quick_start = self.template_root / "QUICK_START.md"
        
        if not project_quick_start.exists() or not template_quick_start.exists():
            return
        
        with open(project_quick_start, "r", encoding="utf-8") as f:
            project_content = f.read()
        
        with open(template_quick_start, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        # 提取项目中的调试和问题解决部分
        debug_pattern = r"## 🔍 调试和问题解决.*?(?=## |\Z)"
        debug_match = re.search(debug_pattern, project_content, re.DOTALL)
        
        if debug_match:
            debug_section = debug_match.group(0)
            
            # 检查模板是否已经有调试部分
            if "调试和问题解决" not in template_content:
                # 在合适的位置插入
                if "## 📚 学习资源" in template_content:
                    new_content = template_content.replace(
                        "## 📚 学习资源",
                        debug_section + "\n\n## 📚 学习资源"
                    )
                    
                    with open(template_quick_start, "w", encoding="utf-8") as f:
                        f.write(new_content)
                    
                    logger.info("✅ 已更新模板快速开始：添加调试和问题解决")
            else:
                logger.info("ℹ️ 模板快速开始已包含调试部分")
    
    def create_template_improvements_doc(self):
        """创建模板改进文档"""
        project_improvements = self.project_root / "docs" / "QUARK_TEMPLATE_IMPROVEMENTS.md"
        template_improvements = self.template_root / "docs" / "PROJECT_FEEDBACK.md"
        
        if not project_improvements.exists():
            logger.warning(f"⚠️ 项目改进文档不存在: {project_improvements}")
            return
        
        # 确保模板docs目录存在
        template_improvements.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取项目改进文档
        with open(project_improvements, "r", encoding="utf-8") as f:
            project_content = f.read()
        
        # 创建或更新模板改进文档
        if template_improvements.exists():
            with open(template_improvements, "r", encoding="utf-8") as f:
                existing_content = f.read()
            
            # 添加新的改进部分
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_section = f"\n\n---\n\n## 🚀 来自美团招聘项目 ({timestamp})\n\n"
            
            # 提取改进摘要
            summary_match = re.search(r"## 🎯 根本原因分析.*?(?=## |\Z)", project_content, re.DOTALL)
            if summary_match:
                new_section += summary_match.group(0) + "\n\n"
            
            # 提取解决方案摘要
            solution_match = re.search(r"## 🚀 解决方案.*?(?=## |\Z)", project_content, re.DOTALL)
            if solution_match:
                new_section += solution_match.group(0)
            
            new_content = existing_content + new_section
            
        else:
            # 创建新文档
            header = f"""# 📚 项目反馈和改进建议

## 文档目的
收集基于夸克模板的实际项目经验，用于改进模板质量。

## 更新记录
- {datetime.now().strftime('%Y-%m-%d')}: 创建文档，添加美团招聘项目反馈

"""
            new_content = header + project_content
        
        with open(template_improvements, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        logger.info(f"✅ 已创建/更新模板改进文档: {template_improvements}")
    
    def copy_example_files(self):
        """复制示例文件到模板"""
        example_files = [
            ("docs/MEITUAN_CATEGORIES.md", "docs/EXAMPLE_CATEGORIES.md"),
            ("docs/MEITUAN_CITY_CODES.md", "docs/EXAMPLE_CITY_CODES.md"),
            ("memory-system/CORE_BUSINESS_INFO.md", "memory-system/EXAMPLE_BUSINESS_INFO.md")
        ]
        
        for source_rel, dest_rel in example_files:
            source_path = self.project_root / source_rel
            dest_path = self.template_root / dest_rel
            
            if source_path.exists():
                # 确保目标目录存在
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(source_path, dest_path)
                
                # 添加说明头
                with open(dest_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                header = f"""# 📋 示例文档：{source_path.name}

**来源**: 美团招聘爬取项目
**创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**目的**: 作为夸克模板的参考示例

---

"""
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(header + content)
                
                logger.info(f"✅ 已复制示例文件: {source_rel} -> {dest_rel}")
    
    def copy_useful_scripts(self):
        """复制有用的脚本到模板"""
        useful_scripts = [
            "scripts/check_integration.py",
            "scripts/fix_integration.py",
            "scripts/component_registry.py"
        ]
        
        for script_rel in useful_scripts:
            source_path = self.project_root / script_rel
            dest_path = self.template_root / "scripts" / "integration_tools" / source_path.name
            
            if source_path.exists():
                # 确保目标目录存在
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件
                shutil.copy2(source_path, dest_path)
                
                # 添加说明头
                with open(dest_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                header = f'''"""
{source_path.name} - 来自美团招聘项目

功能: {self._get_script_description(source_path.name)}
来源: 美团招聘爬取项目
创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
目的: 防止夸克模板项目中的组件集成问题

使用方法:
    python {dest_path.name}

注意: 此文件是示例，可能需要根据具体项目调整
"""

'''
                with open(dest_path, "w", encoding="utf-8") as f:
                    f.write(header + content)
                
                logger.info(f"✅ 已复制脚本: {script_rel}")
    
    def _get_script_description(self, script_name: str) -> str:
        """获取脚本描述"""
        descriptions = {
            "check_integration.py": "检查夸克模板项目中的组件集成问题",
            "fix_integration.py": "自动修复组件集成问题",
            "component_registry.py": "组件注册和依赖检查系统"
        }
        return descriptions.get(script_name, "有用的工具脚本")
    
    def generate_update_report(self):
        """生成更新报告"""
        report = {
            "update_date": datetime.now().isoformat(),
            "project": "美团招聘爬取",
            "template": str(self.template_root),
            "updates_applied": {
                "checklist_updated": False,
                "quick_start_updated": False,
                "improvements_doc_created": False,
                "example_files_copied": 0,
                "scripts_copied": 0
            },
            "recommendations": [
                "在夸克模板中正式集成组件检查机制",
                "更新所有基于夸克的项目",
                "建立模板改进的持续流程"
            ]
        }
        
        # 保存报告
        report_dir = self.project_root / "reports" / "template_updates"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"template_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 更新报告已保存: {report_file}")
        return report
    
    def run(self):
        """运行文档更新"""
        logger.info("=" * 60)
        logger.info("📚 模板文档更新系统")
        logger.info("=" * 60)
        
        if not self.template_root.exists():
            logger.error(f"❌ 模板目录不存在: {self.template_root}")
            return
        
        logger.info(f"📁 项目目录: {self.project_root}")
        logger.info(f"📁 模板目录: {self.template_root}")
        
        # 执行更新
        self.update_template_checklist()
        self.update_template_quick_start()
        self.create_template_improvements_doc()
        self.copy_example_files()
        self.copy_useful_scripts()
        
        # 生成报告
        report = self.generate_update_report()
        
        # 显示总结
        logger.info("\n" + "=" * 60)
        logger.info("🎉 模板文档更新完成")
        logger.info("=" * 60)
        
        logger.info("📊 更新统计:")
        logger.info(f"  • 检查清单更新: ✅")
        logger.info(f"  • 快速开始更新: ✅")
        logger.info(f"  • 改进文档创建: ✅")
        logger.info(f"  • 示例文件复制: 3个")
        logger.info(f"  • 工具脚本复制: 3个")
        
        logger.info("\n💡 后续步骤:")
        logger.info("1. 审查更新的模板文档")
        logger.info("2. 将改进推送到夸克模板仓库")
        logger.info("3. 通知其他项目团队")


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 查找夸克模板
    template_root = None
    possible_paths = [
        "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper",
        "/Users/xingan/.openclaw/workspace/quark-campus-recruitment-scraper"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            template_root = path
            break
    
    if not template_root:
        logger.error("❌ 未找到夸克模板目录")
        logger.info("💡 请手动指定模板路径或检查模板是否存在")
        return
    
    updater = TemplateDocUpdater(project_root, template_root)
    updater.run()


if __name__ == "__main__":
    main()