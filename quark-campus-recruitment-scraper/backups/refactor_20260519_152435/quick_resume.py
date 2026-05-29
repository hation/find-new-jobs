#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速恢复脚本 - Gateway重启后立即执行
恢复第1页剩余4个岗位的爬取
"""

import json
import os
from datetime import datetime

def get_current_status():
    """获取当前状态"""
    status = {
        "timestamp": datetime.now().isoformat(),
        "status": "interrupted",
        "completed": 6,
        "pending": 4,
        "total": 10,
        "completion_rate": 60.0,
        "next_position": 7,
        "next_position_name": "千问事业部-千问-用户增长BP/PMO（PC&web）",
        "next_position_ref": "e60",
        "pending_positions": [
            {
                "id": 7,
                "name": "千问事业部-千问-用户增长BP/PMO（PC&web）",
                "ref": "e60",
                "status": "clicked_needs_snapshot"
            },
            {
                "id": 8,
                "name": "千问事业部-媒体业务-流量商务专员",
                "ref": "e61",
                "status": "pending"
            },
            {
                "id": 9,
                "name": "阿里千问C端事业群-商务合作BD-市场部",
                "ref": "e62",
                "status": "pending"
            },
            {
                "id": 10,
                "name": "千问事业部-书旗小说用户增长渠道运营-北京",
                "ref": "e63",
                "status": "pending"
            }
        ],
        "completed_positions": [
            "千问事业部-商业数据分析-信息流搜索业务-北京/广州",
            "千问事业部-C端用户产品-网盘相册方向",
            "千问事业部-AI Native 产品经理-北京",
            "千问事业部-AI 产品经理 - 千问语音Agent-北京/杭州",
            "千问事业部-用户产品经理-书旗小说APP",
            "千问事业部-千问C端主对话产品经理-北京/杭州"
        ],
        "resume_steps": [
            "1. 重启Gateway: openclaw gateway restart",
            "2. 检查状态: openclaw status",
            "3. 打开列表页: https://talent.quark.cn/off-campus/position-list?lang=zh",
            "4. 重新应用7个类别筛选条件",
            "5. 继续处理岗位7 (已点击，需要获取详情页快照)",
            "6. 处理岗位8-10",
            "7. 生成完整Excel文件"
        ],
        "estimated_time": "15-20分钟",
        "target": "完成第1页全部10个岗位"
    }
    return status

def save_status_file(status):
    """保存状态文件"""
    output_dir = "../output"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"resume_status_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
    
    return filepath

def print_resume_guide():
    """打印恢复指南"""
    print("\n" + "=" * 60)
    print("🚀 夸克招聘爬取器 - 恢复执行指南")
    print("=" * 60)
    
    status = get_current_status()
    
    print(f"\n📊 当前进度:")
    print(f"   已完成: {status['completed']}/{status['total']} 个岗位")
    print(f"   完成率: {status['completion_rate']}%")
    print(f"   待处理: {status['pending']} 个岗位")
    
    print(f"\n✅ 已完成的岗位:")
    for i, pos in enumerate(status['completed_positions'], 1):
        print(f"   {i}. {pos}")
    
    print(f"\n⏳ 待处理的岗位:")
    for pos in status['pending_positions']:
        print(f"   {pos['id']}. {pos['name']} ({pos['status']})")
    
    print(f"\n🚨 中断状态:")
    print(f"   当前处理: 岗位{status['next_position']} - {status['next_position_name']}")
    print(f"   状态: {status['pending_positions'][0]['status']}")
    print(f"   ref: {status['next_position_ref']}")
    
    print(f"\n🔧 恢复步骤:")
    for step in status['resume_steps']:
        print(f"   {step}")
    
    print(f"\n📁 文件位置:")
    print(f"   状态文件: output/resume_status_*.json")
    print(f"   数据文件: output/quark_page1_*")
    print(f"   恢复指南: RESUME_GUIDE.md")
    
    print(f"\n⏰ 预计时间:")
    print(f"   完成剩余岗位: {status['estimated_time']}")
    print(f"   目标: {status['target']}")
    
    print(f"\n💡 提示:")
    print(f"   1. Gateway重启后立即执行")
    print(f"   2. 先检查浏览器服务状态")
    print(f"   3. 重新应用筛选条件")
    print(f"   4. 继续从岗位7开始")
    
    print("\n" + "=" * 60)

def main():
    """主函数"""
    print_resume_guide()
    
    # 保存状态文件
    status = get_current_status()
    status_file = save_status_file(status)
    
    print(f"\n📄 状态文件已保存: {status_file}")
    print(f"📋 恢复指南已保存: RESUME_GUIDE.md")
    print(f"\n🎯 准备恢复执行...")

if __name__ == "__main__":
    main()