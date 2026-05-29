#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经验收集器 - 夸克项目经验反哺系统
收集项目经验，为模板更新提供数据
"""

import os
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperienceCollector:
    """经验收集器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.experiences = {
            "project_info": {},
            "improvements": [],
            "lessons": [],
            "technical_experiences": [],
            "checklist_updates": [],
            "architecture_updates": [],
            "collected_at": datetime.now().isoformat()
        }
    
    def collect_project_info(self):
        """收集项目基本信息"""
        logger.info("📋 收集项目信息...")
        
        # 从配置文件获取信息
        config_file = self.project_root / "config" / "memory_config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.experiences["project_info"] = {
                    "name": config.get("project_info", {}).get("name", "未知"),
                    "type": config.get("project_info", {}).get("type", "未知"),
                    "created_at": config.get("project_info", {}).get("created_at", ""),
                    "description": config.get("project_info", {}).get("description", "")
                }
        
        # 从架构文档获取信息
        arch_file = self.project_root / "ARCHITECTURE.md"
        if arch_file.exists():
            with open(arch_file, "r", encoding="utf-8") as f:
                content = f.read()
                # 提取项目目标
                if "目标:" in content:
                    target_section = content.split("目标:")[1].split("\n")[0].strip()
                    self.experiences["project_info"]["target"] = target_section
        
        logger.info(f"✅ 项目: {self.experiences['project_info'].get('name', '未知')}")
    
    def collect_improvements(self):
        """收集改进点"""
        logger.info("💡 收集改进点...")
        
        # 检查改进文档
        improvements_file = self.project_root / "docs" / "PROJECT_FEEDBACK.md"
        if improvements_file.exists():
            with open(improvements_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 提取改进建议
                improvements = []
                pattern = r"### 💡 改进建议.*?\n(.*?)(?=###|\n##|\Z)"
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                
                if match:
                    improvements_text = match.group(1)
                    # 解析改进项
                    for line in improvements_text.split("\n"):
                        line = line.strip()
                        if line.startswith("- **["):
                            # 解析格式: - **[HIGH] checklist_addition**: 内容
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                title = parts[0].strip()
                                content = parts[1].strip()
                                
                                # 提取优先级和类型
                                priority_match = re.search(r"\[(HIGH|MEDIUM|LOW)\]", title)
                                type_match = re.search(r"\] (.*?):", title)
                                
                                improvements.append({
                                    "title": title,
                                    "content": content,
                                    "priority": priority_match.group(1) if priority_match else "MEDIUM",
                                    "type": type_match.group(1) if type_match else "unknown",
                                    "source": "PROJECT_FEEDBACK.md"
                                })
                
                self.experiences["improvements"] = improvements
        
        logger.info(f"✅ 收集到 {len(self.experiences['improvements'])} 个改进点")
    
    def collect_lessons(self):
        """收集教训记录"""
        logger.info("📚 收集教训记录...")
        
        # 检查教训文档
        lessons_file = self.project_root / "LESSONS_LEARNED.md"
        if lessons_file.exists():
            with open(lessons_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 提取教训记录
                lessons = []
                # 查找教训记录块
                pattern = r"## 🚨 教训记录.*?\n(.*?)(?=## |\Z)"
                match = re.search(pattern, content, re.DOTALL)
                
                if match:
                    lessons_text = match.group(1)
                    # 分割教训记录
                    lesson_blocks = lessons_text.split("\n---")
                    
                    for block in lesson_blocks:
                        block = block.strip()
                        if not block:
                            continue
                        
                        # 提取教训信息
                        lesson = {
                            "description": "",
                            "cause": "",
                            "impact": "",
                            "solution": "",
                            "prevention": "",
                            "level": "medium"
                        }
                        
                        # 提取描述
                        desc_match = re.search(r"### 错误描述\s*\n(.*?)(?=\n###|\Z)", block, re.DOTALL)
                        if desc_match:
                            lesson["description"] = desc_match.group(1).strip()
                        
                        # 提取原因
                        cause_match = re.search(r"### 错误原因\s*\n(.*?)(?=\n###|\Z)", block, re.DOTALL)
                        if cause_match:
                            lesson["cause"] = cause_match.group(1).strip()
                        
                        # 提取影响
                        impact_match = re.search(r"### 影响范围\s*\n(.*?)(?=\n###|\Z)", block, re.DOTALL)
                        if impact_match:
                            lesson["impact"] = impact_match.group(1).strip()
                        
                        # 提取解决方案
                        solution_match = re.search(r"### 解决方案\s*\n(.*?)(?=\n###|\Z)", block, re.DOTALL)
                        if solution_match:
                            lesson["solution"] = solution_match.group(1).strip()
                        
                        # 提取预防措施
                        prevention_match = re.search(r"### 预防措施\s*\n(.*?)(?=\n###|\Z)", block, re.DOTALL)
                        if prevention_match:
                            lesson["prevention"] = prevention_match.group(1).strip()
                        
                        # 判断严重等级
                        if "严重" in block or "🔴" in block:
                            lesson["level"] = "high"
                        elif "中等" in block or "🟡" in block:
                            lesson["level"] = "medium"
                        elif "轻微" in block or "🟢" in block:
                            lesson["level"] = "low"
                        
                        lessons.append(lesson)
                
                self.experiences["lessons"] = lessons
        
        logger.info(f"✅ 收集到 {len(self.experiences['lessons'])} 个教训")
    
    def collect_technical_experiences(self):
        """收集技术经验"""
        logger.info("🔧 收集技术经验...")
        
        technical_experiences = []
        
        # 检查脚本目录，收集技术实现经验
        scripts_dir = self.project_root / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.py"):
                if script_file.name.startswith("_"):
                    continue
                    
                with open(script_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                    # 检查是否有技术经验注释
                    if "经验:" in content or "经验总结:" in content:
                        # 提取经验部分
                        lines = content.split("\n")
                        experience_lines = []
                        in_experience_section = False
                        
                        for line in lines:
                            if "经验:" in line or "经验总结:" in line:
                                in_experience_section = True
                                experience_lines.append(line.strip())
                            elif in_experience_section and (line.startswith("#") or line.startswith('"""')):
                                break
                            elif in_experience_section:
                                experience_lines.append(line.strip())
                        
                        if experience_lines:
                            technical_experiences.append({
                                "file": script_file.name,
                                "experience": "\n".join(experience_lines),
                                "type": "implementation"
                            })
        
        self.experiences["technical_experiences"] = technical_experiences
        logger.info(f"✅ 收集到 {len(technical_experiences)} 个技术经验")
    
    def collect_checklist_updates(self):
        """收集检查清单更新"""
        logger.info("✅ 收集检查清单更新...")
        
        checklist_file = self.project_root / "CHECKLIST.md"
        if checklist_file.exists():
            with open(checklist_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 检查是否有新增的检查项
                updates = []
                
                # 查找新增的检查项（特别是防错相关的）
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if "新增防错检查" in line or "新增:" in line or "新增检查项" in line:
                        # 获取相关检查项
                        relevant_items = []
                        for j in range(i, min(i + 10, len(lines))):
                            if lines[j].startswith("- [ ]"):
                                relevant_items.append(lines[j].strip())
                        
                        if relevant_items:
                            updates.append({
                                "type": "checklist_addition",
                                "description": line.strip(),
                                "items": relevant_items,
                                "source_line": i + 1
                            })
                
                self.experiences["checklist_updates"] = updates
        
        logger.info(f"✅ 收集到 {len(self.experiences['checklist_updates'])} 个检查清单更新")
    
    def collect_architecture_updates(self):
        """收集架构更新"""
        logger.info("🏗️ 收集架构更新...")
        
        arch_file = self.project_root / "ARCHITECTURE.md"
        if arch_file.exists():
            with open(arch_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # 检查版本更新
                updates = []
                
                # 查找版本变更记录
                if "版本:" in content:
                    version_section = content.split("版本:")[1].split("\n")[0].strip()
                    updates.append({
                        "type": "version_update",
                        "description": f"架构版本更新: {version_section}",
                        "content": version_section
                    })
                
                # 查找新增原则
                if "新增原则" in content or "新增:" in content:
                    # 提取新增内容
                    pattern = r"新增[：:].*?\n(.*?)(?=\n#|\Z)"
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        updates.append({
                            "type": "principle_addition",
                            "description": "新增架构原则",
                            "content": match.group(1).strip()
                        })
                
                self.experiences["architecture_updates"] = updates
        
        logger.info(f"✅ 收集到 {len(self.experiences['architecture_updates'])} 个架构更新")
    
    def save_experiences(self):
        """保存收集到的经验"""
        output_dir = self.project_root / "knowledge" / "collected_experiences"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"experiences_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.experiences, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 经验已保存到: {output_file}")
        return output_file
    
    def run(self):
        """运行经验收集"""
        logger.info("=" * 60)
        logger.info("📚 经验收集器 - 夸克项目经验反哺系统")
        logger.info("=" * 60)
        
        self.collect_project_info()
        self.collect_improvements()
        self.collect_lessons()
        self.collect_technical_experiences()
        self.collect_checklist_updates()
        self.collect_architecture_updates()
        
        output_file = self.save_experiences()
        
        # 生成摘要报告
        summary = {
            "total_experiences": len(self.experiences["improvements"]) + 
                                len(self.experiences["lessons"]) + 
                                len(self.experiences["technical_experiences"]) + 
                                len(self.experiences["checklist_updates"]) + 
                                len(self.experiences["architecture_updates"]),
            "improvements": len(self.experiences["improvements"]),
            "lessons": len(self.experiences["lessons"]),
            "technical_experiences": len(self.experiences["technical_experiences"]),
            "checklist_updates": len(self.experiences["checklist_updates"]),
            "architecture_updates": len(self.experiences["architecture_updates"]),
            "output_file": str(output_file),
            "collected_at": self.experiences["collected_at"]
        }
        
        logger.info("📊 收集摘要:")
        logger.info(f"  • 改进点: {summary['improvements']}")
        logger.info(f"  • 教训记录: {summary['lessons']}")
        logger.info(f"  • 技术经验: {summary['technical_experiences']}")
        logger.info(f"  • 检查清单更新: {summary['checklist_updates']}")
        logger.info(f"  • 架构更新: {summary['architecture_updates']}")
        logger.info(f"  • 总计: {summary['total_experiences']}")
        
        return summary


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = os.getcwd()
    
    collector = ExperienceCollector(project_root)
    collector.run()


if __name__ == "__main__":
    main()