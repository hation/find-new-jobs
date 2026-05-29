#!/usr/bin/env python3
"""
实时搜索并导出Excel工具
在登录有效期内快速完成搜索、获取描述、导出Excel
"""

import os
import sys
import json
import csv
import subprocess
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class LiveSearchExporter:
    """实时搜索导出器"""
    
    def __init__(self, boss_path=None):
        self.boss_path = boss_path or "/Users/xingan/Library/Python/3.12/bin/boss"
        self.env_set = False
    
    def setup_environment(self):
        """设置环境"""
        if not self.env_set:
            boss_dir = os.path.dirname(self.boss_path)
            os.environ["PATH"] = f"{boss_dir}:{os.environ.get('PATH', '')}"
            self.env_set = True
    
    def check_and_login(self):
        """检查并确保登录状态"""
        self.setup_environment()
        
        print("🔍 检查登录状态...")
        result = subprocess.run(
            [self.boss_path, "status"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        
        if "已登录" in output and "search=ok" in output:
            print("✅ 登录状态正常")
            return True
        elif "search=fail" in output or "环境异常" in output:
            print("❌ 登录过期，需要重新登录")
            print("\n💡 重新登录步骤:")
            print("1. boss logout")
            print("2. 在浏览器中登录 https://www.zhipin.com")
            print("3. boss login --cookie-source chrome")
            print("4. boss status  # 确认显示'已登录'和'search=ok'")
            return False
        else:
            print(f"⚠️  未知登录状态: {output[:200]}")
            return False
    
    def live_search(self, keyword: str, city: str = "深圳", pages: int = 3) -> List[Dict]:
        """实时搜索并获取岗位数据"""
        print(f"🔍 实时搜索: '{keyword}' ({city}), {pages}页")
        
        all_jobs = []
        
        for page in range(1, pages + 1):
            print(f"📄 正在获取第{page}页...")
            
            cmd = [
                self.boss_path,
                "search",
                keyword,
                "--city", city,
                "--page", str(page),
                "--json"
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    encoding='utf-8'
                )
                
                if result.returncode == 0:
                    try:
                        data = json.loads(result.stdout)
                        if 'data' in data and 'jobList' in data['data']:
                            page_jobs = data['data']['jobList']
                            all_jobs.extend(page_jobs)
                            print(f"  ✅ 获取 {len(page_jobs)} 个岗位")
                        else:
                            print(f"  ⚠️  第{page}页无数据或格式异常")
                    except json.JSONDecodeError as e:
                        print(f"  ❌ JSON解析失败: {e}")
                        print(f"    输出: {result.stdout[:200]}")
                else:
                    print(f"  ❌ 第{page}页搜索失败: {result.stderr[:100]}")
                
                # 页间延迟
                if page < pages:
                    time.sleep(2)
                    
            except Exception as e:
                print(f"  ❌ 第{page}页异常: {e}")
        
        print(f"\n📊 搜索完成，共获取 {len(all_jobs)} 个岗位")
        return all_jobs
    
    def get_description_for_index(self, index: int) -> str:
        """获取指定索引岗位的描述"""
        print(f"  👁️  获取第{index}个岗位详情...")
        
        cmd = [self.boss_path, "show", str(index)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                description = self._extract_description(result.stdout)
                if description:
                    return description
                else:
                    return "已获取详情但未找到描述文本"
            else:
                error_msg = result.stderr[:100] if result.stderr else "未知错误"
                return f"获取失败: {error_msg}"
                
        except Exception as e:
            return f"获取异常: {e}"
    
    def _extract_description(self, text: str) -> str:
        """从文本中提取岗位描述"""
        if not text:
            return ""
        
        # 方法1: 查找标准格式
        lines = text.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            line = line.strip()
            
            # 开始标记
            if any(marker in line for marker in ['岗位描述', '职位描述', '工作职责', '岗位职责']):
                in_description = True
                continue
            
            # 结束标记
            if in_description:
                if any(marker in line.lower() for marker in ['任职要求', '薪资福利', '公司介绍', '联系方式', '---', '...']):
                    break
                
                if line and not line.startswith('#'):
                    description_lines.append(line)
        
        if description_lines:
            return '\n'.join(description_lines)
        
        # 方法2: 查找大段文本
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            # 优先选择包含中文的段落
            chinese_paragraphs = [p for p in paragraphs if re.search(r'[\u4e00-\u9fff]', p)]
            if chinese_paragraphs:
                return chinese_paragraphs[0][:1500]
            return paragraphs[0][:1500]
        
        # 方法3: 返回非空内容
        non_empty = [line.strip() for line in lines if line.strip() and len(line.strip()) > 20]
        if non_empty:
            return '\n'.join(non_empty[:10])  # 最多10行
        
        return ""
    
    def add_descriptions_to_jobs(self, jobs: List[Dict], max_descriptions: int = 20) -> List[Dict]:
        """为岗位添加描述"""
        if not jobs or max_descriptions <= 0:
            return jobs
        
        print(f"\n📝 开始为前{min(len(jobs), max_descriptions)}个岗位获取描述...")
        
        jobs_with_desc = []
        success_count = 0
        
        for i, job in enumerate(jobs[:max_descriptions]):
            print(f"  [{i+1}/{min(len(jobs), max_descriptions)}] {job.get('jobName', f'岗位{i+1}')}")
            
            # 获取描述
            description = self.get_description_for_index(i + 1)
            
            # 更新岗位数据
            job_copy = job.copy()
            job_copy['jobDescription'] = description
            
            # 检查是否成功
            desc_len = len(description)
            if (desc_len > 50 and 
                "未能" not in description and 
                "失败" not in description and 
                "异常" not in description):
                success_count += 1
                print(f"    ✅ 成功 ({desc_len} 字符)")
            else:
                print(f"    ⚠️  可能失败: {description[:80]}")
            
            jobs_with_desc.append(job_copy)
            
            # 延迟避免请求过快
            if i < len(jobs[:max_descriptions]) - 1:
                time.sleep(2.5)
        
        print(f"\n📊 描述获取完成: {success_count}/{min(len(jobs), max_descriptions)} 个成功")
        
        # 添加剩余的岗位（无描述）
        if len(jobs) > max_descriptions:
            remaining_jobs = jobs[max_descriptions:]
            for job in remaining_jobs:
                job_copy = job.copy()
                job_copy['jobDescription'] = "未获取描述（超过最大数量）"
                jobs_with_desc.append(job_copy)
            
            print(f"📋 还有 {len(remaining_jobs)} 个岗位未获取描述")
        
        return jobs_with_desc
    
    def export_to_excel(self, jobs: List[Dict], output_dir: Path = None) -> str:
        """导出到Excel格式的CSV"""
        if not jobs:
            return ""
        
        # 创建输出目录
        if not output_dir:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path.home() / "招聘数据" / f"实时搜索导出_{timestamp}"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义列
        columns = [
            ('序号', 'index'),
            ('岗位名称', 'jobName'),
            ('公司名称', 'brandName'),
            ('薪资', 'salaryDesc'),
            ('经验要求', 'jobExperience'),
            ('学历要求', 'jobDegree'),
            ('地区', 'areaDistrict'),
            ('公司规模', 'brandScaleName'),
            ('融资阶段', 'brandStageName'),
            ('岗位描述', 'jobDescription'),
            ('技能要求', 'skills'),
            ('福利待遇', 'welfareList'),
            ('岗位类型', 'jobTypeDesc'),
            ('Boss姓名', 'bossName'),
            ('Boss职位', 'bossTitle'),
            ('在线状态', 'bossOnline'),
            ('岗位ID', 'encryptJobId'),
            ('公司ID', 'encryptBrandId'),
            ('岗位链接', 'jobLink'),
            ('搜索时间', 'searchTime'),
        ]
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"岗位数据_实时搜索_{timestamp}.csv"
        csv_path = output_dir / csv_filename
        
        print(f"\n💾 导出到CSV: {csv_path}")
        
        # 写入CSV
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow([col[0] for col in columns])
            
            # 写入数据
            for i, job in enumerate(jobs, 1):
                row = []
                
                for col_name, field_key in columns:
                    if field_key == 'index':
                        value = i
                    elif field_key == 'jobLink':
                        job_id = job.get('encryptJobId', '')
                        value = f"https://www.zhipin.com/job_detail/{job_id}.html" if job_id else ""
                    elif field_key == 'searchTime':
                        value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    elif field_key in ['skills', 'welfareList']:
                        field_data = job.get(field_key, [])
                        if isinstance(field_data, list):
                            value = '、'.join([str(item) for item in field_data[:5]])
                        else:
                            value = str(field_data)
                    elif field_key == 'jobDescription':
                        value = job.get(field_key, '未获取描述')
                    else:
                        value = job.get(field_key, '')
                    
                    # 清理数据
                    if isinstance(value, str):
                        value = value.replace('\n', ' ').replace('\r', ' ').strip()
                        if field_key == 'jobDescription' and len(value) > 2000:
                            value = value[:1997] + '...'
                    
                    row.append(value)
                
                writer.writerow(row)
        
        print(f"✅ CSV导出完成: {len(jobs)} 行数据")
        
        # 生成报告
        self._generate_report(jobs, csv_path, output_dir)
        
        return str(csv_path)
    
    def _generate_report(self, jobs: List[Dict], csv_path: Path, output_dir: Path):
        """生成报告"""
        report_file = output_dir / f"{csv_path.stem}_报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 实时搜索导出报告\n\n")
            f.write("## 导出摘要\n")
            f.write(f"- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **总岗位数**: {len(jobs)} 个\n")
            
            # 描述统计
            jobs_with_desc = [job for job in jobs if job.get('jobDescription')]
            valid_desc_count = sum(1 for job in jobs_with_desc 
                                  if len(job['jobDescription']) > 50 and
                                  "未获取" not in job['jobDescription'] and
                                  "失败" not in job['jobDescription'] and
                                  "异常" not in job['jobDescription'])
            
            f.write(f"- **包含岗位描述**: {len(jobs_with_desc)} 个\n")
            f.write(f"- **有效描述**: {valid_desc_count} 个\n")
            
            if jobs_with_desc:
                success_rate = valid_desc_count / len(jobs_with_desc) * 100
                f.write(f"- **描述获取成功率**: {success_rate:.1f}%\n")
            
            f.write(f"- **数据文件**: {csv_path.name}\n")
            f.write(f"- **输出目录**: {output_dir}\n\n")
            
            f.write("## 薪资分布\n")
            
            # 统计薪资
            salary_stats = {}
            for job in jobs:
                salary = job.get('salaryDesc', '面议')
                salary_stats[salary] = salary_stats.get(salary, 0) + 1
            
            if salary_stats:
                f.write("| 薪资范围 | 岗位数量 | 占比 |\n")
                f.write("|----------|----------|------|\n")
                total = len(jobs)
                for salary, count in sorted(salary_stats.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / total * 100
                    f.write(f"| {salary} | {count} | {percentage:.1f}% |\n")
            
            f.write("\n## 数据预览\n")
            f.write("前5个岗位:\n\n")
            
            for i, job in enumerate(jobs[:5], 1):
                f.write(f"### {i}. {job.get('jobName', '未知岗位')}\n")
                f.write(f"- **公司**: {job.get('brandName', '未知公司')}\n")
                f.write(f"- **薪资**: {job.get('salaryDesc', '面议')}\n")
                f.write(f"- **经验**: {job.get('jobExperience', '经验不限')}\n")
                f.write(f"- **学历**: {job.get('jobDegree', '学历不限')}\n")
                
                desc = job.get('jobDescription', '')
                if desc and len(desc) > 50:
                    f.write(f"- **描述预览**: {desc[:200]}...\n")
                
                f.write("\n")
        
        print(f"📋 报告已生成: {report_file}")
    
    def run_live_export(self, keyword: str, city: str = "深圳", 
                       pages: int = 3, max_descriptions: int = 15):
        """运行完整的实时搜索导出流程"""
        print("🚀 实时搜索导出流程开始")
        print("=" * 60)
        
        # 1. 检查登录状态
        if not self.check_and_login():
            print("\n❌ 请先登录后再运行")
            return
        
        # 2. 实时搜索
        jobs = self.live_search(keyword, city, pages)
        
        if not jobs:
            print("\n❌ 未搜索到岗位数据")
            return
        
        # 3. 获取描述
        jobs_with_desc = self.add_descriptions_to_jobs(jobs, max_descriptions)
        
        # 4. 导出Excel
        csv_file = self.export_to_excel(jobs_with_desc)
        
        if csv_file:
            print(f"\n🎉 导出完成！")
            print(f"📁 输出目录: {os.path.dirname(csv_file)}")
            print(f"📋 数据文件: {os.path.basename(csv_file)}")
            print(f"\n💡 用Excel打开:")
            print(f"  open \"{csv_file}\"")
        else:
            print("\n❌ 导出失败")

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='实时搜索并导出Excel')
    
    parser.add_argument('--keyword', '-k', required=True, help='搜索关键词')
    parser.add_argument('--city', '-c', default='深圳', help='城市（默认:深圳）')
    parser.add_argument('--pages', '-p', type=int, default=3, help='搜索页数（默认:3）')
    parser.add_argument('--max-desc', '-m', type=int, default=15, help='最多获取描述的岗位数（默认:15）')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建导出器
    exporter = LiveSearchExporter()
    
    # 运行导出流程
    exporter.run_live_export(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages,
        max_descriptions=args.max_desc
    )

if __name__ == "__main__":
    main()