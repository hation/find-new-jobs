#!/usr/bin/env python3
"""
夸克招聘爬取错误检测与学习系统
自动检测错误模式，更新检查清单和错误教训记录
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib

class ErrorDetector:
    """错误检测与学习系统"""
    
    def __init__(self):
        self.workspace_root = os.path.expanduser("~/.openclaw/workspace")
        self.skill_dir = os.path.join(self.workspace_root, "skills", "quark-campus-recruitment-scraper")
        self.checklist_path = os.path.join(self.skill_dir, "CHECKLIST.md")
        self.lessons_path = os.path.join(self.skill_dir, "LESSONS_LEARNED.md")
        self.errors_db_path = os.path.join(self.skill_dir, "errors_database.json")
        self.execution_log_path = os.path.join(self.skill_dir, "execution_log.txt")
        
        # 错误模式定义
        self.error_patterns = {
            "page_number_mistake": {
                "patterns": [
                    r"以为URL参数.*page=.*就是第.*页",
                    r"URL参数.*page=.*",
                    r"不是URL参数"
                ],
                "category": "页码识别",
                "severity": "致命",
                "solution": "永远以底部显示的页码为准，不是URL参数"
            },
            "filter_lost": {
                "patterns": [
                    r"筛选.*丢失",
                    r"筛选条件.*丢失",
                    r"显示.*362个岗位",
                    r"不是.*92个岗位"
                ],
                "category": "筛选状态",
                "severity": "重要",
                "solution": "重新应用7个筛选类别，验证显示'共92个岗位'"
            },
            "data_not_saved": {
                "patterns": [
                    r"数据.*未保存",
                    r"没有保存.*数据",
                    r"丢失.*数据"
                ],
                "category": "数据完整性",
                "severity": "重要",
                "solution": "每个岗位提取后立即保存到JSON文件"
            },
            "progress_tracking_error": {
                "patterns": [
                    r"进度.*错误",
                    r"错误.*计算进度",
                    r"进度.*不准确"
                ],
                "category": "进度跟踪",
                "severity": "一般",
                "solution": "基于实际完成岗位数计算：(已完成/92)×100%"
            }
        }
        
        # 加载错误数据库
        self.errors_db = self._load_errors_db()
    
    def _load_errors_db(self) -> Dict:
        """加载错误数据库"""
        if os.path.exists(self.errors_db_path):
            try:
                with open(self.errors_db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"errors": [], "statistics": {}, "last_updated": None}
        return {"errors": [], "statistics": {}, "last_updated": None}
    
    def _save_errors_db(self):
        """保存错误数据库"""
        self.errors_db["last_updated"] = datetime.now().isoformat()
        with open(self.errors_db_path, 'w', encoding='utf-8') as f:
            json.dump(self.errors_db, f, ensure_ascii=False, indent=2)
    
    def analyze_execution_log(self) -> List[Dict]:
        """分析执行日志，检测错误"""
        if not os.path.exists(self.execution_log_path):
            return []
        
        errors_found = []
        
        with open(self.execution_log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 按时间戳分割日志条目
        log_entries = re.findall(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\](.*?)(?=\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]|$)', 
                                log_content, re.DOTALL)
        
        for timestamp, entry in log_entries:
            entry = entry.strip()
            
            # 跳过成功和正常条目
            if any(success_word in entry for success_word in ["✅", "成功", "完成", "正常"]):
                continue
            
            # 检测错误模式
            for error_id, pattern_info in self.error_patterns.items():
                for pattern in pattern_info["patterns"]:
                    if re.search(pattern, entry, re.IGNORECASE):
                        # 计算错误内容的哈希，用于去重
                        error_hash = hashlib.md5(f"{error_id}:{entry[:100]}".encode()).hexdigest()
                        
                        # 检查是否已记录
                        if not any(e.get("hash") == error_hash for e in self.errors_db.get("errors", [])):
                            error_data = {
                                "id": error_id,
                                "timestamp": timestamp,
                                "content": entry[:500],  # 截取前500字符
                                "category": pattern_info["category"],
                                "severity": pattern_info["severity"],
                                "solution": pattern_info["solution"],
                                "hash": error_hash,
                                "detected_at": datetime.now().isoformat(),
                                "occurrences": 1
                            }
                            errors_found.append(error_data)
                            
                            # 添加到数据库
                            self.errors_db.setdefault("errors", []).append(error_data)
                            
                            # 更新统计
                            self.errors_db.setdefault("statistics", {})
                            self.errors_db["statistics"].setdefault(error_id, 0)
                            self.errors_db["statistics"][error_id] += 1
                            
                            # 更新分类统计
                            self.errors_db["statistics"].setdefault(f"category_{pattern_info['category']}", 0)
                            self.errors_db["statistics"][f"category_{pattern_info['category']}"] += 1
                            
                            # 更新严重程度统计
                            self.errors_db["statistics"].setdefault(f"severity_{pattern_info['severity']}", 0)
                            self.errors_db["statistics"][f"severity_{pattern_info['severity']}"] += 1
        
        if errors_found:
            self._save_errors_db()
        
        return errors_found
    
    def update_checklist(self, errors: List[Dict]) -> bool:
        """根据检测到的错误更新检查清单"""
        if not errors:
            return False
        
        try:
            with open(self.checklist_path, 'r', encoding='utf-8') as f:
                checklist_content = f.read()
            
            updated = False
            
            # 检查是否需要添加新的检查点
            for error in errors:
                error_id = error["id"]
                category = error["category"]
                solution = error["solution"]
                
                # 根据错误类型确定检查点位置
                if error_id == "page_number_mistake":
                    # 在页码识别规则部分添加检查点
                    if "❌ 不要相信URL参数" not in checklist_content:
                        checklist_content = checklist_content.replace(
                            "### 页码识别规则",
                            "### 页码识别规则\n- [ ] ❌ 不要相信URL参数 `?page=X`\n- [ ] ✅ 永远以底部显示的\"X/10\"为准"
                        )
                        updated = True
                
                elif error_id == "filter_lost":
                    # 在筛选状态部分添加检查点
                    if "每次操作前验证筛选状态" not in checklist_content:
                        checklist_content = checklist_content.replace(
                            "### 筛选状态维护",
                            "### 筛选状态维护\n- [ ] 每次操作前验证筛选状态\n- [ ] 如果丢失，重新应用7个筛选类别"
                        )
                        updated = True
                
                elif error_id == "data_not_saved":
                    # 在数据完整性部分添加检查点
                    if "每个岗位提取后立即保存" not in checklist_content:
                        checklist_content = checklist_content.replace(
                            "### 数据完整性规则",
                            "### 数据完整性规则\n- [ ] 每个岗位提取后立即保存到JSON文件\n- [ ] 文件名必须包含时间戳"
                        )
                        updated = True
            
            if updated:
                # 备份原文件
                backup_path = f"{self.checklist_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(checklist_content)
                
                # 写入更新后的文件
                with open(self.checklist_path, 'w', encoding='utf-8') as f:
                    f.write(checklist_content)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"更新检查清单失败: {e}")
            return False
    
    def update_lessons(self, errors: List[Dict]) -> bool:
        """根据检测到的错误更新错误教训记录"""
        if not errors:
            return False
        
        try:
            with open(self.lessons_path, 'r', encoding='utf-8') as f:
                lessons_content = f.read()
            
            updated = False
            new_lessons = []
            
            for error in errors:
                error_id = error["id"]
                timestamp = error["timestamp"]
                content = error["content"]
                category = error["category"]
                severity = error["severity"]
                solution = error["solution"]
                
                # 检查是否已记录此教训
                lesson_title = f"### {timestamp}: {category} - {severity}错误"
                if lesson_title not in lessons_content:
                    # 创建新教训条目
                    new_lesson = f"""
{lesson_title}
**错误描述**: {content}
**根本原因**: {self._get_root_cause(error_id)}
**解决方案**: {solution}
**预防措施**: {self._get_prevention_measures(error_id)}
**检测时间**: {error['detected_at']}
"""
                    new_lessons.append(new_lesson)
                    updated = True
            
            if updated and new_lessons:
                # 找到"## 错误记录"部分，在它之后插入新教训
                if "## 错误记录" in lessons_content:
                    # 在错误记录部分后插入
                    insert_pos = lessons_content.find("## 错误记录") + len("## 错误记录")
                    updated_content = (lessons_content[:insert_pos] + 
                                     "\n" + "\n".join(new_lessons) + 
                                     lessons_content[insert_pos:])
                else:
                    # 在文件末尾添加错误记录部分
                    updated_content = lessons_content + "\n\n## 错误记录\n" + "\n".join(new_lessons)
                
                # 备份原文件
                backup_path = f"{self.lessons_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(lessons_content)
                
                # 写入更新后的文件
                with open(self.lessons_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"更新错误教训记录失败: {e}")
            return False
    
    def _get_root_cause(self, error_id: str) -> str:
        """获取错误根本原因"""
        root_causes = {
            "page_number_mistake": "错误地将URL参数作为页码判断依据，而不是页面实际显示",
            "filter_lost": "假设筛选状态会持久保存，没有持续验证",
            "data_not_saved": "没有实现即时数据持久化机制",
            "progress_tracking_error": "基于错误状态计算进度，而不是实际完成数"
        }
        return root_causes.get(error_id, "需要进一步分析")
    
    def _get_prevention_measures(self, error_id: str) -> str:
        """获取预防措施"""
        prevention_measures = {
            "page_number_mistake": "1. 永远以页面底部显示的页码为准 2. 不信任URL参数 3. 每次操作前验证页码",
            "filter_lost": "1. 每次操作前验证筛选状态 2. 如果丢失立即重新应用 3. 持续监控显示状态",
            "data_not_saved": "1. 每个岗位提取后立即保存 2. 实现自动保存机制 3. 定期验证数据完整性",
            "progress_tracking_error": "1. 基于实际保存的文件数计算进度 2. 定期验证进度准确性 3. 实现自动进度跟踪"
        }
        return prevention_measures.get(error_id, "需要制定具体预防措施")
    
    def generate_error_report(self) -> str:
        """生成错误分析报告"""
        if not self.errors_db.get("errors"):
            return "✅ 未发现新的错误"
        
        total_errors = len(self.errors_db["errors"])
        statistics = self.errors_db.get("statistics", {})
        
        report = [
            "📊 错误分析报告",
            "=" * 40,
            f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"总错误数: {total_errors}",
            ""
        ]
        
        # 按严重程度分类
        severity_stats = {k:v for k,v in statistics.items() if k.startswith("severity_")}
        if severity_stats:
            report.append("📈 严重程度分布:")
            for stat, count in severity_stats.items():
                severity = stat.replace("severity_", "")
                report.append(f"  {severity}: {count}次")
            report.append("")
        
        # 按类别分类
        category_stats = {k:v for k,v in statistics.items() if k.startswith("category_")}
        if category_stats:
            report.append("📂 错误类别分布:")
            for stat, count in category_stats.items():
                category = stat.replace("category_", "")
                report.append(f"  {category}: {count}次")
            report.append("")
        
        # 最近错误
        recent_errors = sorted(self.errors_db["errors"], 
                              key=lambda x: x.get("detected_at", ""), 
                              reverse=True)[:5]
        
        if recent_errors:
            report.append("🆕 最近发现的错误:")
            for i, error in enumerate(recent_errors, 1):
                report.append(f"{i}. [{error['timestamp']}] {error['category']} - {error['severity']}")
                report.append(f"   内容: {error['content'][:100]}...")
                report.append(f"   解决方案: {error['solution']}")
                report.append("")
        
        report.append("=" * 40)
        return "\n".join(report)

def main():
    """主函数"""
    print("🔍 开始错误检测与学习...")
    print("-" * 40)
    
    detector = ErrorDetector()
    
    # 1. 分析执行日志，检测错误
    print("📝 分析执行日志...")
    errors_found = detector.analyze_execution_log()
    
    if errors_found:
        print(f"✅ 发现 {len(errors_found)} 个新错误")
        
        # 2. 更新检查清单
        print("📋 更新检查清单...")
        if detector.update_checklist(errors_found):
            print("✅ 检查清单已更新")
        else:
            print("ℹ️ 检查清单无需更新")
        
        # 3. 更新错误教训记录
        print("📚 更新错误教训记录...")
        if detector.update_lessons(errors_found):
            print("✅ 错误教训记录已更新")
        else:
            print("ℹ️ 错误教训记录无需更新")
        
        # 4. 生成报告
        print("\n📊 生成错误报告...")
        report = detector.generate_error_report()
        print(report)
        
        # 5. 保存报告
        report_path = os.path.join(detector.skill_dir, "error_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 报告已保存到: {report_path}")
        
    else:
        print("✅ 未发现新的错误")
    
    print("-" * 40)
    print("🎯 错误检测与学习完成")

if __name__ == "__main__":
    main()