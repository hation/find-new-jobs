#!/usr/bin/env python3
"""
夸克招聘爬取自动更新系统
定时自动更新检查清单和错误教训记录
"""

import os
import sys
import time
import json
import schedule
from datetime import datetime, timedelta
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    """自动更新系统"""
    
    def __init__(self):
        self.workspace_root = Path.home() / ".openclaw" / "workspace"
        self.skill_dir = self.workspace_root / "skills" / "quark-campus-recruitment-scraper"
        self.scripts_dir = self.skill_dir / "scripts"
        
        # 配置文件
        self.config_file = self.skill_dir / "updater_config.json"
        self.state_file = self.skill_dir / "updater_state.json"
        
        # 加载配置
        self.config = self._load_config()
        self.state = self._load_state()
        
        # 确保目录存在
        self.skill_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """加载配置"""
        default_config = {
            "update_schedule": {
                "error_detection": "*/15 * * * *",  # 每15分钟检测一次错误
                "checklist_update": "0 */2 * * *",   # 每2小时更新一次检查清单
                "lessons_update": "0 */4 * * *",     # 每4小时更新一次错误教训
                "full_analysis": "0 0 * * *"         # 每天凌晨全面分析
            },
            "error_patterns": [
                {
                    "name": "page_number_mistake",
                    "triggers": ["URL参数", "?page=", "不是底部显示"],
                    "action": "update_checklist"
                },
                {
                    "name": "filter_lost",
                    "triggers": ["筛选丢失", "362个岗位", "不是92个"],
                    "action": "update_checklist"
                },
                {
                    "name": "data_not_saved",
                    "triggers": ["数据未保存", "丢失数据", "没有保存"],
                    "action": "update_lessons"
                },
                {
                    "name": "timeout_error",
                    "triggers": ["超时", "timeout", "等待超时"],
                    "action": "update_both"
                }
            ],
            "auto_update_enabled": True,
            "backup_before_update": True,
            "notify_on_update": True,
            "max_errors_per_day": 50,
            "retention_days": 30
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _load_state(self) -> dict:
        """加载状态"""
        default_state = {
            "last_error_detection": None,
            "last_checklist_update": None,
            "last_lessons_update": None,
            "last_full_analysis": None,
            "total_errors_detected": 0,
            "total_updates_made": 0,
            "errors_today": 0,
            "last_error_date": None,
            "update_history": []
        }
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    user_state = json.load(f)
                    # 合并状态
                    default_state.update(user_state)
            except Exception as e:
                logger.error(f"加载状态文件失败: {e}")
        
        return default_state
    
    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def run_error_detector(self):
        """运行错误检测器"""
        logger.info("运行错误检测器...")
        
        # 检查今日错误数量限制
        today = datetime.now().date().isoformat()
        if self.state.get("last_error_date") != today:
            self.state["errors_today"] = 0
            self.state["last_error_date"] = today
        
        max_errors = self.config.get("max_errors_per_day", 50)
        if self.state["errors_today"] >= max_errors:
            logger.warning(f"今日错误数量已达上限 ({max_errors})，跳过检测")
            return
        
        try:
            # 运行错误检测脚本
            error_detector_path = self.scripts_dir / "error_detector.py"
            if error_detector_path.exists():
                result = subprocess.run(
                    [sys.executable, str(error_detector_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.skill_dir
                )
                
                if result.returncode == 0:
                    # 解析输出，检查是否发现了新错误
                    if "发现" in result.stdout and "个新错误" in result.stdout:
                        # 提取错误数量
                        import re
                        match = re.search(r'发现 (\d+) 个新错误', result.stdout)
                        if match:
                            new_errors = int(match.group(1))
                            self.state["errors_today"] += new_errors
                            self.state["total_errors_detected"] += new_errors
                            logger.info(f"检测到 {new_errors} 个新错误")
                    
                    logger.info("错误检测完成")
                else:
                    logger.error(f"错误检测失败: {result.stderr}")
            
            self.state["last_error_detection"] = datetime.now().isoformat()
            self._save_state()
            
        except Exception as e:
            logger.error(f"运行错误检测器时出错: {e}")
    
    def update_checklist(self):
        """更新检查清单"""
        logger.info("更新检查清单...")
        
        try:
            checklist_path = self.skill_dir / "CHECKLIST.md"
            if not checklist_path.exists():
                logger.error("检查清单文件不存在")
                return
            
            # 备份原文件
            if self.config.get("backup_before_update", True):
                backup_dir = self.skill_dir / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"CHECKLIST.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                import shutil
                shutil.copy2(checklist_path, backup_path)
                logger.info(f"已备份检查清单到: {backup_path}")
            
            # 读取当前检查清单
            with open(checklist_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            updated = False
            
            # 检查是否需要添加基于错误统计的检查点
            errors_today = self.state.get("errors_today", 0)
            if errors_today > 10:
                # 今日错误较多，需要加强检查
                if "### 高频错误预防" not in content:
                    new_section = """
### 高频错误预防
**今日已检测到 {} 个错误，请特别注意以下检查点:**

- [ ] 🔴 每次操作前必须验证页码 (今日高频错误)
- [ ] 🔴 每次操作前必须验证筛选状态
- [ ] 🟡 每个岗位提取后立即保存
- [ ] 🟡 定期检查进度准确性

**额外提醒:**
- 如果连续出现3个以上错误，立即停止并重新验证所有状态
- 记录每个错误的具体上下文，便于分析
""".format(errors_today)
                    
                    # 在"## 每次操作前必须检查"部分后插入
                    if "## 每次操作前必须检查" in content:
                        insert_pos = content.find("## 每次操作前必须检查") + len("## 每次操作前必须检查")
                        content = content[:insert_pos] + new_section + content[insert_pos:]
                        updated = True
            
            # 检查是否需要更新错误避免清单
            total_errors = self.state.get("total_errors_detected", 0)
            if total_errors > 0:
                # 更新统计信息
                stats_section = f"\n**错误统计**: 累计检测到 {total_errors} 个错误，今日 {errors_today} 个"
                
                if "## 错误统计" not in content:
                    # 在文件末尾添加错误统计
                    content += f"\n\n## 错误统计\n{stats_section}"
                    updated = True
                else:
                    # 更新现有的错误统计
                    import re
                    content = re.sub(
                        r'## 错误统计\n.*?\n',
                        f'## 错误统计\n{stats_section}\n',
                        content,
                        flags=re.DOTALL
                    )
                    updated = True
            
            if updated:
                # 写入更新后的文件
                with open(checklist_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.state["total_updates_made"] += 1
                self.state["last_checklist_update"] = datetime.now().isoformat()
                
                # 记录更新历史
                update_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "checklist",
                    "changes": [
                        "添加高频错误预防检查点",
                        "更新错误统计信息"
                    ],
                    "errors_today": errors_today,
                    "total_errors": total_errors
                }
                self.state.setdefault("update_history", []).append(update_record)
                
                # 保留最近30天的记录
                retention_days = self.config.get("retention_days", 30)
                cutoff_date = (datetime.now() - timedelta(days=retention_days)).isoformat()
                self.state["update_history"] = [
                    record for record in self.state["update_history"]
                    if record["timestamp"] > cutoff_date
                ]
                
                self._save_state()
                logger.info("检查清单已更新")
                
                # 通知
                if self.config.get("notify_on_update", True):
                    self._notify_update("检查清单", update_record["changes"])
            else:
                logger.info("检查清单无需更新")
                
        except Exception as e:
            logger.error(f"更新检查清单时出错: {e}")
    
    def update_lessons(self):
        """更新错误教训记录"""
        logger.info("更新错误教训记录...")
        
        try:
            lessons_path = self.skill_dir / "LESSONS_LEARNED.md"
            if not lessons_path.exists():
                logger.error("错误教训记录文件不存在")
                return
            
            # 备份原文件
            if self.config.get("backup_before_update", True):
                backup_dir = self.skill_dir / "backups"
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"LESSONS.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                import shutil
                shutil.copy2(lessons_path, backup_path)
                logger.info(f"已备份错误教训记录到: {backup_path}")
            
            # 读取当前错误教训记录
            with open(lessons_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            updated = False
            
            # 检查是否需要添加基于统计的总结
            total_errors = self.state.get("total_errors_detected", 0)
            if total_errors > 0:
                # 添加统计总结部分
                stats_summary = f"""
## 📊 错误统计总结

### 总体统计
- **累计检测错误数**: {total_errors}
- **今日检测错误数**: {self.state.get("errors_today", 0)}
- **最后检测时间**: {self.state.get("last_error_detection", "从未")}
- **最后更新时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

### 错误趋势分析
"""
                
                # 分析最近7天的错误趋势
                recent_updates = self.state.get("update_history", [])
                if recent_updates:
                    # 按日期分组
                    from collections import defaultdict
                    daily_errors = defaultdict(int)
                    
                    for update in recent_updates:
                        if "errors_today" in update:
                            date = update["timestamp"][:10]  # 取日期部分
                            daily_errors[date] = update["errors_today"]
                    
                    # 添加趋势分析
                    if daily_errors:
                        stats_summary += "\n### 最近7天错误趋势\n"
                        sorted_dates = sorted(daily_errors.keys(), reverse=True)[:7]
                        for date in sorted_dates:
                            count = daily_errors[date]
                            stats_summary += f"- **{date}**: {count} 个错误\n"
                
                # 检查是否已存在统计总结
                if "## 📊 错误统计总结" not in content:
                    # 在文件末尾添加
                    content += stats_summary
                    updated = True
                else:
                    # 更新现有的统计总结
                    import re
                    content = re.sub(
                        r'## 📊 错误统计总结\n.*?\n(?:##|$)',
                        stats_summary + "\n",
                        content,
                        flags=re.DOTALL
                    )
                    updated = True
            
            # 检查是否需要添加高频错误提醒
            errors_today = self.state.get("errors_today", 0)
            if errors_today > 5:
                warning_section = f"""
## ⚠️ 今日高频错误提醒

**检测到今日已有 {errors_today} 个错误，请特别注意以下问题:**

### 最可能出现的错误
1. **页码识别错误** - 不要相信URL参数，以页面显示为准
2. **筛选状态丢失** - 每次操作前验证7个筛选类别
3. **数据保存延迟** - 每个岗位提取后立即保存

### 预防措施
- 操作前暂停3秒，确认当前状态
- 每个操作后验证预期结果
- 发现异常立即停止，重新验证
"""
                
                if "## ⚠️ 今日高频错误提醒" not in content:
                    # 在统计总结后插入
                    if "## 📊 错误统计总结" in content:
                        insert_pos = content.find("## 📊 错误统计总结") + len("## 📊 错误统计总结")
                        # 找到统计总结的结束位置
                        end_pos = content.find("\n##", insert_pos)
                        if end_pos == -1:
                            end_pos = len(content)
                        content = content[:end_pos] + warning_section + content[end_pos:]
                        updated = True
            
            if updated:
                # 写入更新后的文件
                with open(lessons_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.state["total_updates_made"] += 1
                self.state["last_lessons_update"] = datetime.now().isoformat()
                
                # 记录更新历史
                update_record = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "lessons",
                    "changes": [
                        "更新错误统计总结",
                        "添加高频错误提醒" if errors_today > 5 else "更新统计信息"
                    ],
                    "errors_today": errors_today,
                    "total_errors": total_errors
                }
                self.state.setdefault("update_history", []).append(update_record)
                
                self._save_state()
                logger.info("错误教训记录已更新")
                
                # 通知
                if self.config.get("notify_on_update", True):
                    self._notify_update("错误教训记录", update_record["changes"])
            else:
                logger.info("错误教训记录无需更新")
                
        except Exception as e:
            logger.error(f"更新错误教训记录时出错: {e}")
    
    def run_full_analysis(self):
        """运行全面分析"""
        logger.info("运行全面分析...")
        
        try:
            # 运行所有更新和分析
            self.run_error_detector()
            self.update_checklist()
            self.update_lessons()
            
            # 生成分析报告
            self._generate_analysis_report()
            
            self.state["last_full_analysis"] = datetime.now().isoformat()
            self._save_state()
            
            logger.info("全面分析完成")
            
        except Exception as e:
            logger.error(f"运行全面分析时出错: {e}")
    
    def _generate_analysis_report(self):
        """生成分析报告"""
        try:
            report_path = self.skill_dir / "analysis_report.md"
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# 夸克招聘爬取系统分析报告\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("## 📈 系统状态概览\n")
                f.write(f"- 累计检测错误数: {self.state.get('total_errors_detected', 0)}\n")
                f.write(f"- 累计更新次数: {self.state.get('total_updates_made', 0)}\n")
                f.write(f"- 今日错误数: {self.state.get('errors_today', 0)}\n")
                f.write(f"- 最后错误检测: {self.state.get('last_error_detection', '从未')}\n")
                f.write(f"- 最后检查清单更新: {self.state.get('last_checklist_update', '从未')}\n")
                f.write(f"- 最后错误教训更新: {self.state.get('last_lessons_update', '从未')}\n\n")
                
                f.write("## 🔄 更新历史\n")
                updates = self.state.get("update_history", [])
                if updates:
                    for update in updates[-10:]:  # 最近10次更新
                        f.write(f"### {update['timestamp']}\n")
                        f.write(f"- 类型: {update['type']}\n")
                        f.write(f"- 变更: {', '.join(update['changes'])}\n")
                        f.write(f"- 当时错误数: {update.get('errors_today', 0)} 今日 / {update.get('total_errors', 0)} 累计\n\n")
                else:
                    f.write("暂无更新历史\n\n")
                
                f.write("## 📊 建议与改进\n")
                
                errors_today = self.state.get("errors_today", 0)
                if errors_today > 10:
                    f.write("### ⚠️ 需要立即改进\n")
                    f.write("今日错误数超过10个，表明系统存在严重问题:\n")
                    f.write("1. 检查筛选状态验证机制\n")
                    f.write("2. 加强页码识别错误预防\n")
                    f.write("3. 实现更严格的错误检测\n")
                elif errors_today > 5:
                    f.write("### 🟡 需要注意\n")
                    f.write("今日错误数较多，建议:\n")
                    f.write("1. 增加操作前验证步骤\n")
                    f.write("2. 加强数据保存验证\n")
                    f.write("3. 优化错误处理流程\n")
                else:
                    f.write("### ✅ 状态良好\n")
                    f.write("今日错误数在可接受范围内，继续保持。\n")
                
                f.write("\n## 🎯 下一步计划\n")
                f.write("1. 继续监控错误趋势\n")
                f.write("2. 根据错误模式优化检查清单\n")
                f.write("3. 定期更新错误教训记录\n")
                f.write("4. 持续改进系统稳定性\n")
            
            logger.info(f"分析报告已生成: {report_path}")
            
        except Exception as e:
            logger.error(f"生成分析报告时出错: {e}")
    
    def _notify_update(self, file_type: str, changes: list):
        """通知更新"""
        try:
            notification_file = self.skill_dir / "last_update_notification.txt"
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                f.write(f"📢 系统更新通知\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"更新文件: {file_type}\n")
                f.write(f"变更内容:\n")
                for change in changes:
                    f.write(f"  - {change}\n")
                f.write(f"\n当前统计:\n")
                f.write(f"  今日错误数: {self.state.get('errors_today', 0)}\n")
                f.write(f"  累计错误数: {self.state.get('total_errors_detected', 0)}\n")
                f.write(f"  累计更新数: {self.state.get('total_updates_made', 0)}\n")
            
            logger.info(f"更新通知已保存: {notification_file}")
            
        except Exception as e:
            logger.error(f"生成更新通知时出错: {e}")
    
    def start_scheduler(self):
        """启动调度器"""
        logger.info("启动自动更新调度器...")
        
        # 设置调度任务
        schedule_config = self.config.get("update_schedule", {})
        
        # 错误检测
        schedule.every().minute.do(self.run_error_detector).tag('error_detection')
        
        # 检查清单更新
        schedule.every(2).hours.do(self.update_checklist).tag('checklist_update')
        
        # 错误教训更新
        schedule.every(4).hours.do(self.update_lessons).tag('lessons_update')
        
        # 全面分析
        schedule.every().day.at("00:00").do(self.run_full_analysis).tag('full_analysis')
        
        logger.info("调度器已启动")
        logger.info(f"错误检测: 每15分钟")
        logger.info(f"检查清单更新: 每2小时")
        logger.info(f"错误教训更新: 每4小时")
        logger.info(f"全面分析: 每天00:00")
        
        # 运行调度器
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"调度器运行出错: {e}")

def main():
    """主函数"""
    print("🚀 夸克招聘爬取自动更新系统")
    print("=" * 50)
    
    updater = AutoUpdater()
    
    # 检查是否启用自动更新
    if not updater.config.get("auto_update_enabled", True):
        print("自动更新已禁用，使用手动模式")
        
        # 手动运行一次全面分析
        updater.run_full_analysis()
        return
    
    # 启动调度器
    updater.start_scheduler()

if __name__ == "__main__":
    main()