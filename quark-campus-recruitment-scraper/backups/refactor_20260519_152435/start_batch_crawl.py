#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动第2-10页批量爬取脚本
"""

import os
import sys
import subprocess
from datetime import datetime

def start_batch_crawl():
    """启动批量爬取"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("=" * 60)
    print("🚀 启动夸克校园招聘第2-10页批量爬取")
    print("=" * 60)
    
    # 检查环境
    print("\n📋 环境检查:")
    print("   1. 检查当前目录...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"      当前目录: {current_dir}")
    
    print("   2. 检查增强版脚本...")
    enhanced_script = os.path.join(current_dir, "actual_crawler_enhanced.py")
    if os.path.exists(enhanced_script):
        print(f"      找到脚本: actual_crawler_enhanced.py")
    else:
        print(f"      ❌ 脚本不存在")
        return False
    
    print("   3. 检查输出目录...")
    output_dir = os.path.join(current_dir, "../output")
    os.makedirs(output_dir, exist_ok=True)
    print(f"      输出目录: {output_dir}")
    
    print("   4. 检查第1页数据...")
    page1_files = [f for f in os.listdir(output_dir) if "page1" in f and f.endswith(".json")]
    if page1_files:
        print(f"      找到第1页数据: {page1_files[0]}")
    else:
        print(f"      ⚠️ 未找到第1页数据文件")
    
    # 执行参数
    checkpoint_file = f"checkpoint_{timestamp}.json"
    
    print("\n⚙️ 爬取配置:")
    print(f"   起始页码: 2")
    print(f"   结束页码: 10")
    print(f"   目标岗位: 83个")
    print(f"   断点文件: {checkpoint_file}")
    print(f"   错误重试: 3次")
    print(f"   进度保存: 每5个岗位自动保存")
    
    print("\n⏰ 时间预估:")
    print(f"   第2-3页 (20岗位): 1-1.5小时")
    print(f"   第4-10页 (63岗位): 3-4小时")
    print(f"   总计: 4-5.5小时")
    
    print("\n📊 数据整合:")
    print(f"   第1页数据: 已保存")
    print(f"   第2-10页数据: 待爬取")
    print(f"   最终数据: 93个岗位合并文件")
    
    # 确认执行
    print("\n" + "=" * 60)
    print("确认执行批量爬取？")
    print(f"   1. 保持当前浏览器状态 (t1标签页)")
    print(f"   2. 筛选条件已应用 (7个类别)")
    print(f"   3. 显示共93个岗位")
    print("=" * 60)
    
    # 执行命令
    command = [
        "python3", "actual_crawler_enhanced.py",
        "--start-page", "2",
        "--end-page", "10",
        "--checkpoint-file", checkpoint_file,
        "--max-retries", "3",
        "--save-interval", "5"
    ]
    
    print(f"\n💻 执行命令:")
    print(f"   {' '.join(command)}")
    
    # 启动爬取
    print("\n🚀 启动批量爬取...")
    print("=" * 60)
    
    try:
        # 执行脚本
        result = subprocess.run(command, capture_output=False, text=True, cwd=current_dir)
        
        if result.returncode == 0:
            print("\n✅ 批量爬取完成！")
            return True
        else:
            print(f"\n❌ 批量爬取失败，返回码: {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\n⏸️ 用户中断，爬取已停止")
        print("💾 进度已保存到断点文件，可恢复执行")
        return False
    except Exception as e:
        print(f"\n❌ 执行错误: {e}")
        return False

def main():
    """主函数"""
    success = start_batch_crawl()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 第2-10页批量爬取成功完成！")
        print("=" * 60)
        print("\n📁 下一步:")
        print("   1. 合并第1-10页数据")
        print("   2. 生成完整的Excel文件")
        print("   3. 创建最终数据报告")
    else:
        print("\n" + "=" * 60)
        print("❌ 批量爬取失败或中断")
        print("=" * 60)
        print("\n🔧 故障排除:")
        print("   1. 检查浏览器是否正常运行")
        print("   2. 确认筛选条件已正确应用")
        print("   3. 检查断点文件状态")
        print("   4. 从断点文件恢复执行")

if __name__ == "__main__":
    main()