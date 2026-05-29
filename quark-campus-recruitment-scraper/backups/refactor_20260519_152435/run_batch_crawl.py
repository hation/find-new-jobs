#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接执行第2-10页批量爬取
"""

import os
import sys
import time
from datetime import datetime

def run_direct_batch_crawl():
    """直接执行批量爬取"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("=" * 60)
    print("🚀 直接启动夸克校园招聘第2-10页批量爬取")
    print("=" * 60)
    
    # 创建断点文件
    checkpoint_file = f"checkpoint_{timestamp}.json"
    
    # 直接执行命令
    command = f"""
python3 actual_crawler_enhanced.py \
  --start-page 2 \
  --end-page 10 \
  --checkpoint-file {checkpoint_file} \
  --max-retries 3 \
  --save-interval 5 \
  --auto-start yes
"""
    
    print(f"📋 执行配置:")
    print(f"   起始页码: 2")
    print(f"   结束页码: 10")
    print(f"   目标岗位: 83个")
    print(f"   断点文件: {checkpoint_file}")
    print(f"   自动开始: 是")
    print(f"   时间戳: {timestamp}")
    
    print("\n🚀 立即开始执行...")
    print("=" * 60)
    
    # 执行命令
    os.system(command)

def main():
    """主函数"""
    run_direct_batch_crawl()

if __name__ == "__main__":
    main()