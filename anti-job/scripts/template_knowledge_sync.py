#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板知识同步系统
将项目经验回流到夸克模板
"""

import os
import json
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateKnowledgeSync:
    """模板知识同步系统"""
    
    def __init__(self, project_root: str, template_path: str = None):
        self.project_root = Path(project_root)
        self.template_path = Path(template_path) if template_path else self._find_template_path()
        
        # 知识库目录
        self.knowledge_dir = self.project_root / "knowledge" / "template_updates"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 同步记录
        self.sync_history = []
    
    def _find_template_path(self) -> Optional[Path]:
        """查找夸克模板路径"""
        # 可能的模板位置
        possible_paths = [
            Path.home() / ".openclaw" / "workspace" / "skills" / "quark-campus-recruitment-scraper",
            Path.home() / ".openclaw" / "workspace" / "quark-campus-recruitment-scraper",
            self.project_root.parent / "quark-campus-recruitment-scraper",
            Path("/Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper")
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "SKILL.md").exists():
                logger.info(f"✅ 找到夸克模板: {path}")
                return path
        
        logger.warning("⚠️ 未找到夸克模板路径")
        return None
    
    def collect_project_knowledge(self) -> Dict[str, any]:
        """收集项目知识"""
        logger.info("📚 收集项目知识...")
        
        knowledge = {
            "project_name": "蚂蚁国际招聘爬取",
            "template_version": "v1.0.0",
            "collection_date": datetime.now().isoformat(),
            "improvements": [],
            "issues_found": [],
            "solutions": [],
            "new_components": [],
            "updated_docs": []
        }
        
        # 1. 收集改进点
        improvements_file = self.project_root / "docs" / "QUARK_TEMPLATE_IMPROVEMENTS.md"
        if improvements_file.exists():
            with open(improvements_file, "r", encoding="utf-8") as f:
                content = f.read()
                knowledge["improvements_summary"] = content[:1000]  # 前1000字符
        
        # 2. 收集发现的问题
        integration_report = self.project_root / "logs" / "integration_check.json"
        if integration_report.exists():
            with open(integration_report, "r", encoding="utf-8") as f:
                report = json.load(f)
                knowledge["issues_found"] = report.get("issues", [])
        
        # 3. 收集新组件
        src_dir = self.project_root / "src"
        if src_dir.exists():
            for py_file in src_dir.rglob("*.py"):
                if py_file.name.startswith("__"):
                    continue
                
                # 检查是否是美团特定的组件
                if "meituan" in py_file.name.lower():
                    knowledge["new_components"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "size": py_file.stat().st_size,
                        "type": self._classify_component(py_file.name)
                    })
        
        # 4. 收集更新的文档
        docs_dir = self.project_root / "docs"
        if docs_dir.exists():
            for md_file in docs_dir.rglob("*.md"):
                if "meituan" in md_file.name.lower() or "CHECKLIST" in md_file.name:
                    knowledge["updated_docs"].append({
                        "file": str(md_file.relative_to(self.project_root)),
                        "size": md_file.stat().st_size,
                        "is_template_related": "quark" in md_file.name.lower() or "template" in md_file.name.lower()
                    })
        
        # 5. 收集脚本改进
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            new_scripts = []
            for script_file in scripts_dir.rglob("*.py"):
                if any(keyword in script_file.name.lower() for keyword in ["integration", "registry", "fix", "check"]):
                    new_scripts.append(str(script_file.relative_to(self.project_root)))
            knowledge["new_scripts"] = new_scripts
        
        logger.info(f"✅ 收集到 {len(knowledge['improvements'])} 个改进点")
        logger.info(f"✅ 收集到 {len(knowledge['new_components'])} 个新组件")
        
        return knowledge
    
    def _classify_component(self, filename: str) -> str:
        """分类组件类型"""
        if "api" in filename.lower():
            return "api_crawler"
        elif "browser" in filename.lower():
            return "browser_crawler"
        elif "crawler" in filename.lower():
            return "smart_selector"
        elif "exporter" in filename.lower():
            return "data_exporter"
        else:
            return "other"
    
    def generate_template_update_patch(self, knowledge: Dict[str, any]) -> Dict[str, any]:
        """生成模板更新补丁"""
        logger.info("🔧 生成模板更新补丁...")
        
        patch = {
            "metadata": {
                "generated_by": "TemplateKnowledgeSync",
                "generated_at": datetime.now().isoformat(),
                "source_project": "meituan-job",
                "template_version": "v1.0.0"
            },
            "files_to_add": [],
            "files_to_update": [],
            "docs_to_update": [],
            "recommendations": []
        }
        
        # 1. 建议添加到模板的文件
        if knowledge.get("new_scripts"):
            for script in knowledge["new_scripts"]:
                if "integration" in script.lower() or "registry" in script.lower():
                    patch["files_to_add"].append({
                        "source": script,
                        "destination": f"scripts/{Path(script).name}",
                        "reason": "防止组件集成问题",
                        "priority": "high"
                    })
        
        # 2. 建议更新的文档
        improvements_file = self.project_root / "docs" / "QUARK_TEMPLATE_IMPROVEMENTS.md"
        if improvements_file.exists():
            patch["docs_to_update"].append({
                "source": "docs/QUARK_TEMPLATE_IMPROVEMENTS.md",
                "destination": "docs/TEMPLATE_IMPROVEMENTS_FROM_PROJECTS.md",
                "reason": "收集项目反馈，改进模板",
                "priority": "medium"
            })
        
        # 3. 建议添加到检查清单
        checklist_file = self.project_root / "CHECKLIST_MEITUAN.md"
        if checklist_file.exists():
            with open(checklist_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 提取集成检查部分
                if "组件集成检查" in content:
                    patch["recommendations"].append({
                        "type": "checklist_addition",
                        "content": "在模板检查清单中添加组件集成检查项",
                        "reason": "防止'已实现但未集成'问题",
                        "priority": "high"
                    })
        
        # 4. 建议的模板改进
        if knowledge.get("issues_found"):
            patch["recommendations"].append({
                "type": "template_architecture",
                "content": "添加组件自动发现和集成验证机制",
                "reason": f"发现 {len(knowledge['issues_found'])} 个集成问题",
                "priority": "high"
            })
        
        logger.info(f"✅ 生成 {len(patch['files_to_add'])} 个文件添加建议")
        logger.info(f"✅ 生成 {len(patch['recommendations'])} 个改进建议")
        
        return patch
    
    def save_knowledge_to_template(self, knowledge: Dict[str, any], patch: Dict[str, any]):
        """保存知识到模板"""
        if not self.template_path:
            logger.warning("⚠️ 未找到模板路径，无法保存知识")
            return
        
        logger.info(f"💾 保存知识到模板: {self.template_path}")
        
        # 1. 在模板中创建知识目录
        template_knowledge_dir = self.template_path / "knowledge" / "from_projects"
        template_knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # 2. 保存知识文件
        knowledge_file = template_knowledge_dir / f"meituan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(knowledge_file, "w", encoding="utf-8") as f:
            json.dump({
                "project": knowledge,
                "patch": patch,
                "sync_date": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
        
        # 3. 更新模板的改进文档
        template_improvements_file = self.template_path / "docs" / "PROJECT_FEEDBACK.md"
        if not template_improvements_file.parent.exists():
            template_improvements_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取或创建改进文档
        if template_improvements_file.exists():
            with open(template_improvements_file, "r", encoding="utf-8") as f:
                existing_content = f.read()
        else:
            existing_content = "# 📚 项目反馈和改进建议\n\n来自实际项目的经验反馈\n\n"
        
        # 添加美团项目的反馈
        new_content = f"\n\n## 🚀 蚂蚁国际招聘爬取项目反馈\n**反馈时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if knowledge.get("issues_found"):
            new_content += f"### 🔍 发现的问题 ({len(knowledge['issues_found'])}个)\n"
            for issue in knowledge["issues_found"][:5]:  # 只显示前5个
                new_content += f"- **{issue.get('type', '未知')}**: {issue.get('description', '无描述')}\n"
        
        if patch.get("recommendations"):
            new_content += f"\n### 💡 改进建议 ({len(patch['recommendations'])}个)\n"
            for rec in patch["recommendations"]:
                new_content += f"- **[{rec['priority'].upper()}] {rec['type']}**: {rec['content']}\n  *原因*: {rec['reason']}\n"
        
        # 写回文件
        with open(template_improvements_file, "w", encoding="utf-8") as f:
            f.write(existing_content + new_content)
        
        # 4. 如果模板有检查清单，建议更新
        template_checklist = self.template_path / "CHECKLIST.md"
        if template_checklist.exists():
            with open(template_checklist, "r", encoding="utf-8") as f:
                checklist_content = f.read()
            
            # 检查是否已经有集成检查
            if "组件集成检查" not in checklist_content:
                logger.info("💡 建议在模板检查清单中添加组件集成检查项")
        
        logger.info(f"✅ 知识已保存到模板: {knowledge_file}")
        self.sync_history.append({
            "timestamp": datetime.now().isoformat(),
            "knowledge_file": str(knowledge_file.relative_to(self.template_path)),
            "improvements_count": len(knowledge.get("improvements", [])),
            "issues_count": len(knowledge.get("issues_found", []))
        })
    
    def copy_useful_files_to_template(self, patch: Dict[str, any]):
        """复制有用的文件到模板"""
        if not self.template_path:
            return
        
        logger.info("📁 复制有用文件到模板...")
        
        for file_info in patch.get("files_to_add", []):
            if file_info["priority"] == "high":
                source_file = self.project_root / file_info["source"]
                dest_file = self.template_path / file_info["destination"]
                
                if source_file.exists():
                    # 创建目标目录
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 复制文件
                    shutil.copy2(source_file, dest_file)
                    logger.info(f"✅ 复制文件: {source_file.name} -> {dest_file}")
                    
                    # 添加说明注释
                    with open(dest_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    header = f'''"""
{file_info["reason"]}
来自: 蚂蚁国际招聘爬取项目
复制时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
'''
                    
                    with open(dest_file, "w", encoding="utf-8") as f:
                        f.write(header + content)
    
    def generate_sync_report(self) -> Dict[str, any]:
        """生成同步报告"""
        report = {
            "sync_date": datetime.now().isoformat(),
            "template_path": str(self.template_path) if self.template_path else None,
            "project_name": "美团招聘爬取",
            "knowledge_collected": {
                "improvements": self.sync_history[-1].get("improvements_count", 0) if self.sync_history else 0,
                "issues": self.sync_history[-1].get("issues_count", 0) if self.sync_history else 0,
                "new_components": 0,
                "updated_docs": 0
            },
            "files_copied": [],
            "docs_updated": [],
            "recommendations": [
                "在夸克模板中添加组件集成检查机制",
                "更新模板检查清单，包含集成验证",
                "建立模板知识回流流程"
            ],
            "next_steps": [
                "将改进反馈给夸克模板维护者",
                "在团队中分享经验",
                "建立模板改进的持续流程"
            ]
        }
        
        # 保存报告
        report_file = self.knowledge_dir / f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 同步报告已保存: {report_file}")
        return report
    
    def run(self):
        """运行知识同步"""
        logger.info("=" * 60)
        logger.info("🔄 模板知识同步系统")
        logger.info("=" * 60)
        
        # 1. 收集知识
        knowledge = self.collect_project_knowledge()
        
        # 2. 生成更新补丁
        patch = self.generate_template_update_patch(knowledge)
        
        # 3. 保存到模板
        if self.template_path:
            self.save_knowledge_to_template(knowledge, patch)
            self.copy_useful_files_to_template(patch)
        else:
            logger.warning("⚠️ 未找到模板，知识将保存在本地")
            # 保存到本地
            local_knowledge_file = self.knowledge_dir / "knowledge.json"
            with open(local_knowledge_file, "w", encoding="utf-8") as f:
                json.dump({"knowledge": knowledge, "patch": patch}, f, ensure_ascii=False, indent=2)
        
        # 4. 生成报告
        report = self.generate_sync_report()
        
        # 5. 显示总结
        logger.info("\n" + "=" * 60)
        logger.info("🎉 知识同步完成")
        logger.info("=" * 60)
        
        if self.template_path:
            logger.info(f"✅ 知识已同步到模板: {self.template_path}")
        else:
            logger.info("💾 知识已保存到本地")
        
        logger.info(f"📊 同步统计:")
        logger.info(f"  • 改进点: {len(knowledge.get('improvements', []))}")
        logger.info(f"  • 发现问题: {len(knowledge.get('issues_found', []))}")
        logger.info(f"  • 新组件: {len(knowledge.get('new_components', []))}")
        logger.info(f"  • 建议更新: {len(patch.get('recommendations', []))}")
        
        logger.info("\n💡 后续建议:")
        logger.info("1. 将改进反馈给夸克模板项目")
        logger.info("2. 在团队中分享经验教训")
        logger.info("3. 建立定期的模板知识回流机制")


def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 尝试找到夸克模板
    template_path = None
    possible_paths = [
        "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper",
        "/Users/xingan/.openclaw/workspace/quark-campus-recruitment-scraper"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            template_path = path
            break
    
    sync = TemplateKnowledgeSync(project_root, template_path)
    sync.run()


if __name__ == "__main__":
    main()