#!/usr/bin/env python3
"""
检查方案B数据完整性
"""

import os

def check_data_completeness():
    # 设置工作目录
    data_dir = "/Users/xingan/招聘数据/方案B_立即执行_20260515_010114"
    os.chdir(data_dir)
    
    print("📊 方案B数据完整性检查")
    print("=" * 50)
    
    # 检查pure_security_ids.txt
    pure_file = "pure_security_ids.txt"
    if os.path.exists(pure_file):
        with open(pure_file, 'r', encoding='utf-8') as f:
            pure_ids = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        print(f"📋 总职位数: {len(pure_ids)}")
    else:
        print(f"❌ 文件不存在: {pure_file}")
        return
    
    # 检查fetched_encryptids.txt
    encryptid_file = "fetched_encryptids.txt"
    if os.path.exists(encryptid_file):
        with open(encryptid_file, 'r', encoding='utf-8') as f:
            fetched_encryptids = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        print(f"📥 已获取encryptId数: {len(fetched_encryptids)}")
    else:
        print(f"⚠️  文件不存在: {encryptid_file}")
        fetched_encryptids = []
    
    # 检查fetched_security_ids.txt
    record_file = "fetched_security_ids.txt"
    if os.path.exists(record_file):
        with open(record_file, 'r', encoding='utf-8') as f:
            records = [l.strip() for l in f if l.strip()]
        print(f"📝 获取记录数: {len(records)}")
    else:
        print(f"⚠️  文件不存在: {record_file}")
    
    # 检查职位详情目录
    detail_dir = "职位详情"
    if os.path.exists(detail_dir):
        detail_files = [f for f in os.listdir(detail_dir) if f.endswith('.json')]
        print(f"💾 详情文件数: {len(detail_files)}")
    else:
        print(f"⚠️  目录不存在: {detail_dir}")
        detail_files = []
    
    # 计算数据完整性
    if pure_ids:
        completeness = len(fetched_encryptids) / len(pure_ids) * 100
        print(f"\n📈 数据完整性: {len(fetched_encryptids)}/{len(pure_ids)} ({completeness:.1f}%)")
        
        # 计算距离50%目标
        target_50 = int(len(pure_ids) * 0.5)
        if len(fetched_encryptids) >= target_50:
            print(f"🎯 达到50%目标!")
        else:
            needed = target_50 - len(fetched_encryptids)
            print(f"🎯 距离50%目标还需: {needed}个")
    
    # 检查Excel文件
    excel_file = "深圳_ai.xlsx"
    if os.path.exists(excel_file):
        file_size = os.path.getsize(excel_file)
        print(f"\n📄 Excel文件: {excel_file} ({file_size/1024:.1f} KB)")
    else:
        print(f"\n⚠️  Excel文件不存在: {excel_file}")
    
    print("\n💡 建议:")
    if len(fetched_encryptids) < target_50:
        print("1. 运行获取脚本: python3 fetch_details_optimized_v2.py")
        print("2. 确保token有效（重新登录BOSS直聘）")
        print(f"3. 从第{max(60, len(fetched_encryptids))}个开始获取")
    else:
        print("1. 运行合并脚本: python3 final_fix_excel.py")
        print("2. 验证数据质量")
        print("3. 备份数据文件")

if __name__ == "__main__":
    check_data_completeness()