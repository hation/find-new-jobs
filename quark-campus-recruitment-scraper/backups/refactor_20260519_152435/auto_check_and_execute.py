#!/usr/bin/env python3
"""
夸克招聘爬取任务自动检查与执行脚本
强制读取检查清单和错误教训记录，确保不重复犯错
"""

import os
import sys
import json
import time
from datetime import datetime

# 路径配置
WORKSPACE_ROOT = os.path.expanduser("~/.openclaw/workspace")
SKILL_DIR = os.path.join(WORKSPACE_ROOT, "skills", "quark-campus-recruitment-scraper")
CHECKLIST_PATH = os.path.join(SKILL_DIR, "CHECKLIST.md")
LESSONS_PATH = os.path.join(SKILL_DIR, "LESSONS_LEARNED.md")
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")
LOG_FILE = os.path.join(SKILL_DIR, "execution_log.txt")

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry + "\n")

def read_and_validate_checklist():
    """读取并验证检查清单"""
    log_message("📋 步骤1: 读取检查清单")
    
    if not os.path.exists(CHECKLIST_PATH):
        log_message("❌ 错误: CHECKLIST.md 文件不存在")
        return False
    
    with open(CHECKLIST_PATH, "r", encoding="utf-8") as f:
        checklist_content = f.read()
    
    # 检查关键内容
    required_sections = [
        "每次操作前必须检查",
        "筛选类别确认",
        "页码识别规则",
        "错误避免清单"
    ]
    
    for section in required_sections:
        if section not in checklist_content:
            log_message(f"❌ 错误: 检查清单缺少关键部分: {section}")
            return False
    
    log_message("✅ 检查清单验证通过")
    return True

def read_and_validate_lessons():
    """读取并验证错误教训记录"""
    log_message("📚 步骤2: 读取错误教训记录")
    
    if not os.path.exists(LESSONS_PATH):
        log_message("❌ 错误: LESSONS_LEARNED.md 文件不存在")
        return False
    
    with open(LESSONS_PATH, "r", encoding="utf-8") as f:
        lessons_content = f.read()
    
    # 检查关键教训
    critical_lessons = [
        "页码识别根本错误",
        "页面实际显示 > URL参数",
        "筛选状态需要持续维护"
    ]
    
    for lesson in critical_lessons:
        if lesson not in lessons_content:
            log_message(f"❌ 警告: 教训记录缺少关键教训: {lesson}")
    
    log_message("✅ 错误教训记录验证通过")
    return True

def validate_current_state():
    """验证当前执行状态"""
    log_message("🔍 步骤3: 验证当前执行状态")
    
    # 检查输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log_message("✅ 创建输出目录")
    
    # 检查是否有进行中的任务
    progress_file = os.path.join(SKILL_DIR, "current_progress.json")
    if os.path.exists(progress_file):
        with open(progress_file, "r", encoding="utf-8") as f:
            progress = json.load(f)
        log_message(f"📊 发现进行中的任务: {progress.get('current_page', '未知')}页")
        return progress
    else:
        log_message("ℹ️ 没有进行中的任务，开始新任务")
        return None

def create_execution_plan(current_progress=None):
    """创建执行计划"""
    log_message("📝 步骤4: 创建执行计划")
    
    if current_progress:
        # 继续现有任务
        plan = {
            "type": "continue",
            "current_page": current_progress.get("current_page", 1),
            "completed_positions": current_progress.get("completed_positions", 0),
            "next_position": current_progress.get("next_position", 1),
            "total_positions": 92,
            "start_time": datetime.now().isoformat()
        }
    else:
        # 开始新任务
        plan = {
            "type": "new",
            "current_page": 1,
            "completed_positions": 0,
            "next_position": 1,
            "total_positions": 92,
            "start_time": datetime.now().isoformat()
        }
    
    # 保存执行计划
    plan_file = os.path.join(SKILL_DIR, "execution_plan.json")
    with open(plan_file, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    log_message(f"✅ 执行计划创建完成: {plan['type']}任务，第{plan['current_page']}页")
    return plan

def generate_instructions(plan):
    """生成OpenClaw执行指令"""
    log_message("💡 步骤5: 生成执行指令")
    
    instructions = []
    
    # 1. 读取强制规则
    instructions.append("读取 ~/.openclaw/workspace/AGENTS.md 中的夸克任务强制规则")
    
    # 2. 验证检查清单理解
    instructions.append("确认已理解 CHECKLIST.md 中的所有检查点")
    
    # 3. 验证教训理解
    instructions.append("确认已理解 LESSONS_LEARNED.md 中的关键教训")
    
    # 4. 根据计划生成具体指令
    if plan["type"] == "new":
        instructions.append("执行夸克任务：步骤1验证筛选状态，步骤2开始第1页")
    else:
        instructions.append(f"执行夸克任务：步骤1验证筛选状态，步骤2继续第{plan['current_page']}页第{plan['next_position']}个岗位")
    
    # 5. 数据保存指令
    instructions.append("每个岗位提取后立即保存到JSON文件")
    
    # 6. 进度报告指令
    instructions.append("每完成5个岗位报告一次进度")
    
    # 保存指令
    instructions_file = os.path.join(SKILL_DIR, "execution_instructions.txt")
    with open(instructions_file, "w", encoding="utf-8") as f:
        for i, instr in enumerate(instructions, 1):
            f.write(f"{i}. {instr}\n")
    
    log_message("✅ 执行指令生成完成")
    return instructions

def main():
    """主函数"""
    log_message("🚀 开始夸克招聘爬取任务自动检查")
    log_message("=" * 50)
    
    # 1. 读取并验证检查清单
    if not read_and_validate_checklist():
        log_message("❌ 检查清单验证失败，任务中止")
        return False
    
    # 2. 读取并验证错误教训记录
    if not read_and_validate_lessons():
        log_message("⚠️ 错误教训记录验证有警告，但继续执行")
    
    # 3. 验证当前状态
    current_progress = validate_current_state()
    
    # 4. 创建执行计划
    plan = create_execution_plan(current_progress)
    
    # 5. 生成执行指令
    instructions = generate_instructions(plan)
    
    # 6. 输出最终指令
    log_message("=" * 50)
    log_message("🎯 自动检查完成，请执行以下指令:")
    log_message("")
    
    for i, instr in enumerate(instructions, 1):
        log_message(f"{i}. {instr}")
    
    log_message("")
    log_message("📊 任务概览:")
    log_message(f"   - 类型: {plan['type']}任务")
    log_message(f"   - 当前页: 第{plan['current_page']}页")
    log_message(f"   - 已完成: {plan['completed_positions']}/92 岗位")
    log_message(f"   - 下一个: 第{plan['next_position']}个岗位")
    log_message(f"   - 开始时间: {plan['start_time']}")
    
    log_message("=" * 50)
    log_message("✅ 自动检查流程完成，可以开始执行任务")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)