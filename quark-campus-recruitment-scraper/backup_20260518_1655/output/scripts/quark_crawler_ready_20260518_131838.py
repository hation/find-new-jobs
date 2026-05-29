#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸克校园招聘 - 可直接执行的爬取脚本
"""

import json
import re
import time
import random
from datetime import datetime
from typing import List, Dict, Any
import os
import pandas as pd

class QuarkCrawler:
    """夸克校园招聘爬虫"""
    
    def __init__(self):
        self.positions = []
        self.start_time = time.time()
        
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def extract_from_snapshot(self, snapshot_text: str, page_num: int = 1) -> List[Dict[str, Any]]:
        """
        从快照中提取岗位信息
        
        注意：这里需要实际的浏览器快照
        在实际使用中，应该：
        1. 使用 browser(snapshot) 获取页面内容
        2. 将内容传递给这个函数
        """
        positions = []
        lines = snapshot_text.split('\n')
        
        current_pos = None
        
        for line in lines:
            line = line.strip()
            
            # 提取岗位名称
            if line.startswith("千问事业部-"):
                if current_pos:
                    positions.append(current_pos)
                
                current_pos = {
                    "岗位id": f"quark_{int(time.time())}_{len(positions):04d}",
                    "岗位名称": line,
                    "页码": page_num,
                    "提取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            # 提取岗位详情
            elif "更新于" in line and current_pos:
                # 解析: "更新于 2026-05-18 产品类-商业型 北京"
                pattern = r"更新于\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+(.+)"
                match = re.search(pattern, line)
                
                if match:
                    current_pos["更新时间"] = match.group(1)
                    
                    # 类别
                    category_info = match.group(2)
                    if "-" in category_info:
                        current_pos["职位类别"] = category_info.split("-")[0]
                        current_pos["子类别"] = category_info.split("-")[1]
                    else:
                        current_pos["职位类别"] = category_info
                    
                    # 地点
                    location = match.group(3)
                    current_pos["办公地点"] = location
        
        if current_pos:
            positions.append(current_pos)
        
        return positions
    
    def save_results(self):
        """保存结果"""
        output_dir = "./output/final_results"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. 保存JSON
        json_file = os.path.join(output_dir, f"quark_final_{timestamp}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2)
        
        # 2. 保存Excel
        excel_file = os.path.join(output_dir, f"quark_final_{timestamp}.xlsx")
        
        # 定义完整的12个字段
        all_fields = [
            "岗位id", "岗位名称", "职位类别", "办公地点", "所属部门",
            "学历要求", "工作年限", "更新时间", "页码",
            "职位描述", "职位要求", "岗位详情链接"
        ]
        
        # 创建DataFrame
        df_data = []
        for pos in self.positions:
            row = {field: pos.get(field, "待获取") for field in all_fields}
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_excel(excel_file, index=False)
        
        # 3. 保存报告
        report_file = os.path.join(output_dir, f"quark_report_{timestamp}.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("夸克校园招聘 - 最终数据报告\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"爬取耗时: {time.time() - self.start_time:.1f} 秒\n")
            f.write(f"岗位总数: {len(self.positions)}\n")
            f.write(f"筛选条件: 产品类、运营类、数据类、市场拓展、销售类、游戏类、金融类\n\n")
            
            f.write("📊 数据统计:\n")
            if self.positions:
                # 类别统计
                categories = {}
                for pos in self.positions:
                    cat = pos.get("职位类别", "未知")
                    categories[cat] = categories.get(cat, 0) + 1
                
                f.write("  类别分布:\n")
                for cat, count in sorted(categories.items()):
                    f.write(f"    {cat}: {count} 个\n")
                
                # 数据完整性
                sample = self.positions[0]
                complete = sum(1 for v in sample.values() if v != "待获取")
                total = len(sample)
                f.write(f"\n  数据完整性: {complete}/{total} 个字段\n")
            
            f.write(f"\n📁 输出文件:\n")
            f.write(f"  JSON: {json_file}\n")
            f.write(f"  Excel: {excel_file}\n")
            f.write(f"  报告: {report_file}\n")
        
        self.log(f"✅ 结果已保存: {len(self.positions)} 个岗位")
        
        return {
            "json": json_file,
            "excel": excel_file,
            "report": report_file,
            "count": len(self.positions)
        }

def main():
    """主函数 - 需要实际浏览器数据才能运行"""
    print("=" * 60)
    print("夸克校园招聘爬虫 - 准备执行")
    print("=" * 60)
    
    crawler = QuarkCrawler()
    crawler.log("爬虫初始化完成")
    crawler.log("筛选条件: 7个类别，92个岗位")
    
    print("\n⚠️  注意: 这个脚本需要实际的浏览器数据")
    print("在实际执行前，需要:")
    print("1. 确保浏览器已打开夸克网站")
    print("2. 筛选条件已应用（92个岗位）")
    print("3. 获取页面快照并传递给extract_from_snapshot()")
    
    print("\n📋 执行流程:")
    print("1. 获取第1页快照 -> 提取数据")
    print("2. 点击岗位获取详情 -> 补充数据")
    print("3. 翻页 -> 重复1-2")
    print("4. 保存所有数据 -> 生成Excel")
    
    print("\n" + "=" * 60)
    print("准备就绪，可以开始爬取!")
    print("=" * 60)
    
    return crawler

if __name__ == "__main__":
    main()
