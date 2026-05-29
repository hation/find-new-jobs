#!/usr/bin/env python3
"""
夸克校园招聘爬取器 - 自动进度检查脚本
每半小时自动运行，检查：
1. 进度是否正常推进
2. 数据是否保存到本地
3. 是否有卡住或错误
4. 生成检查报告
"""

import json
import os
import time
from datetime import datetime
import sys

def load_progress():
    """加载进度文件"""
    progress_path = os.path.expanduser("~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/live_progress.json")
    if not os.path.exists(progress_path):
        return {"error": "进度文件不存在"}
    
    with open(progress_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_data_files():
    """检查数据文件"""
    output_dir = os.path.expanduser("~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/output")
    
    # 查找最新的数据文件
    json_files = [f for f in os.listdir(output_dir) if f.endswith('.json') and f.startswith('quark_')]
    if not json_files:
        return {"error": "无数据文件"}
    
    # 按修改时间排序
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(output_dir, x)), reverse=True)
    latest_file = json_files[0]
    latest_path = os.path.join(output_dir, latest_file)
    
    file_stats = os.stat(latest_path)
    last_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    # 检查文件内容
    with open(latest_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            positions_count = len(data) if isinstance(data, list) else 0
        except:
            positions_count = 0
    
    return {
        "latest_file": latest_file,
        "last_modified": last_modified,
        "positions_count": positions_count,
        "file_size_kb": file_stats.st_size / 1024
    }

def check_execution_log():
    """检查执行日志"""
    log_path = os.path.expanduser("~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/execution_log.txt")
    if not os.path.exists(log_path):
        return {"error": "执行日志不存在"}
    
    file_stats = os.stat(log_path)
    last_modified = datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
    
    # 读取最后10行
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[-10:]
    
    return {
        "last_modified": last_modified,
        "recent_entries": lines,
        "file_size_kb": file_stats.st_size / 1024
    }

def generate_report():
    """生成检查报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 收集所有检查结果
    progress = load_progress()
    data_files = check_data_files()
    exec_log = check_execution_log()
    
    # 分析状态
    status = "正常"
    issues = []
    
    # 检查进度更新时间
    if "last_update" in progress:
        last_update = datetime.fromisoformat(progress["last_update"].replace('+08:00', ''))
        now = datetime.now()
        time_diff = (now - last_update).total_seconds() / 60  # 分钟
        
        if time_diff > 30:
            issues.append(f"进度文件超过{time_diff:.1f}分钟未更新")
            status = "警告"
    
    # 检查数据文件
    if "error" in data_files:
        issues.append(f"数据文件检查失败: {data_files['error']}")
        status = "错误"
    elif data_files.get("positions_count", 0) == 0:
        issues.append("数据文件中无岗位数据")
        status = "警告"
    
    # 检查执行日志
    if "error" in exec_log:
        issues.append(f"执行日志检查失败: {exec_log['error']}")
        status = "警告"
    
    # 生成报告
    report = {
        "check_time": timestamp,
        "status": status,
        "issues": issues,
        "progress": {
            "completed": progress.get("completed_positions", 0),
            "total": progress.get("total_positions", 0),
            "rate": progress.get("completion_rate", 0),
            "last_update": progress.get("last_update", "未知")
        },
        "data_files": data_files,
        "execution_log": {
            "last_modified": exec_log.get("last_modified", "未知"),
            "entries_count": len(exec_log.get("recent_entries", []))
        }
    }
    
    return report

def save_report(report):
    """保存检查报告"""
    report_dir = os.path.expanduser("~/.openclaw/workspace/skills/quark-campus-recruitment-scraper/check_reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"check_report_{timestamp}.json")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 同时生成简化的文本报告
    txt_report = f"""
=== 自动进度检查报告 ===
检查时间: {report['check_time']}
状态: {report['status']}

📊 进度统计:
  已完成: {report['progress']['completed']}/{report['progress']['total']} ({report['progress']['rate']}%)
  最后更新: {report['progress']['last_update']}

📁 数据文件:
  最新文件: {report['data_files'].get('latest_file', '无')}
  最后修改: {report['data_files'].get('last_modified', '未知')}
  岗位数量: {report['data_files'].get('positions_count', 0)}

📝 执行日志:
  最后修改: {report['execution_log']['last_modified']}
  最近条目: {report['execution_log']['entries_count']} 条

🚨 问题清单:
"""
    
    if report['issues']:
        for i, issue in enumerate(report['issues'], 1):
            txt_report += f"  {i}. {issue}\n"
    else:
        txt_report += "  无问题\n"
    
    txt_report += "=" * 40
    
    txt_path = os.path.join(report_dir, f"check_report_{timestamp}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_report)
    
    return report_path, txt_path

def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始自动进度检查...")
    
    report = generate_report()
    json_path, txt_path = save_report(report)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查完成")
    print(f"  状态: {report['status']}")
    print(f"  进度: {report['progress']['completed']}/{report['progress']['total']}")
    print(f"  数据文件: {report['data_files'].get('latest_file', '无')}")
    print(f"  报告保存: {txt_path}")
    
    # 如果有问题，在控制台突出显示
    if report['issues']:
        print("\n🚨 检测到问题:")
        for issue in report['issues']:
            print(f"  • {issue}")
    
    return report['status'] == "正常"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)