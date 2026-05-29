#!/usr/bin/env python3
"""
Job Search技能 - Excel导出模板（包含岗位描述）
标准化的Excel格式数据导出，包含岗位详细描述和统计分析
"""

import os
import sys
import csv
import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class ExcelExporterWithDescription:
    """Excel格式数据导出器（包含岗位描述）"""
    
    # 标准字段定义 - 包含岗位描述
    STANDARD_COLUMNS = [
        ('序号', 'index', '序号'),
        ('岗位名称', 'jobName', '岗位完整名称'),
        ('公司名称', 'brandName', '公司全名'),
        ('薪资', 'salaryDesc', '薪资范围'),
        ('经验要求', 'jobExperience', '工作经验要求'),
        ('学历要求', 'jobDegree', '学历要求'),
        ('地区', 'areaDistrict', '工作地区'),
        ('公司规模', 'brandScaleName', '公司员工规模'),
        ('融资阶段', 'brandStageName', '公司融资阶段'),
        ('岗位描述', 'jobDescription', '岗位详细描述'),  # 新增：岗位描述
        ('技能要求', 'skills', '岗位技能要求'),
        ('福利待遇', 'welfareList', '公司福利'),
        ('岗位类型', 'jobTypeDesc', '岗位类型'),
        ('Boss姓名', 'bossName', '招聘负责人'),
        ('Boss职位', 'bossTitle', '招聘负责人职位'),
        ('在线状态', 'bossOnline', 'Boss在线状态'),
        ('搜索关键词', 'search_keyword', '搜索关键词'),
        ('来源页数', 'search_page', '搜索结果页码'),
        ('数据时间', 'data_time', '数据获取时间'),
        ('岗位ID', 'encryptJobId', '岗位唯一ID'),
        ('公司ID', 'encryptBrandId', '公司唯一ID'),
        ('岗位链接', 'jobLink', '岗位详情链接'),  # 新增：岗位链接
    ]
    
    def __init__(self, output_dir=None, include_description=True):
        """
        初始化导出器
        
        Args:
            output_dir: 输出目录
            include_description: 是否包含岗位描述（默认包含）
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = Path.home() / "招聘数据" / f"Excel导出_含描述_{timestamp}"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.include_description = include_description
        
    def fetch_job_description(self, job_id: str, security_id: str = None) -> str:
        """
        获取岗位详细描述
        
        Args:
            job_id: 岗位ID (encryptJobId)
            security_id: 安全ID（可选）
        
        Returns:
            岗位描述文本
        """
        if not job_id:
            return "无法获取岗位ID"
            
        try:
            # 使用boss包装器获取岗位详情
            wrapper_path = "/Users/xingan/.openclaw/workspace/skills/find_new_jobs/job-search/scripts/boss_wrapper.py"
            import subprocess
            import sys
            
            # 构建命令
            cmd = [sys.executable, wrapper_path, "detail", job_id]
            if security_id:
                cmd.append(security_id)
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # 解析输出，提取岗位描述
                description = self._extract_description_from_output(result.stdout)
                return description if description else "未能获取详细描述"
            else:
                return f"获取失败: {result.stderr[:100]}"
                
        except Exception as e:
            return f"获取异常: {str(e)}"
    
    def _extract_description_from_output(self, output: str) -> str:
        """从boss-cli输出中提取岗位描述"""
        if not output:
            return ""
        
        # 尝试不同的提取策略
        description_parts = []
        
        # 策略1：查找"岗位描述"、"职位描述"等关键词
        lines = output.split('\n')
        in_description = False
        
        for line in lines:
            line = line.strip()
            
            # 检测描述开始
            if any(keyword in line for keyword in ['岗位描述', '职位描述', '工作职责', '岗位职责']):
                in_description = True
                continue
            
            # 检测描述结束（遇到其他章节或空行后的新章节）
            if in_description:
                if (line.startswith('###') or 
                    line.startswith('##') or 
                    line.startswith('#') or
                    any(keyword in line for keyword in ['任职要求', '薪资福利', '公司介绍', '联系方式'])):
                    break
                
                if line:  # 只添加非空行
                    description_parts.append(line)
        
        if description_parts:
            return '\n'.join(description_parts)
        
        # 策略2：提取大段文本
        paragraphs = re.split(r'\n\s*\n', output)
        long_paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 100]
        
        if long_paragraphs:
            return '\n\n'.join(long_paragraphs[:3])  # 只取前3个长段落
        
        # 策略3：返回前500个字符
        return output[:500] + ('...' if len(output) > 500 else '')
    
    def export_jobs_with_descriptions(self, jobs_data: List[Dict], 
                                    fetch_descriptions: bool = True,
                                    max_jobs_with_desc: int = 50) -> List[str]:
        """
        导出岗位数据，包含岗位描述
        
        Args:
            jobs_data: 岗位数据列表
            fetch_descriptions: 是否获取岗位描述
            max_jobs_with_desc: 最多获取描述的岗位数
        
        Returns:
            导出的文件路径列表
        """
        print("🚀 开始导出Excel格式数据（包含岗位描述）")
        print("=" * 60)
        
        if not jobs_data:
            print("❌ 没有数据可导出")
            return []
        
        print(f"📊 准备导出 {len(jobs_data)} 个岗位数据")
        
        # 如果需要获取岗位描述
        if fetch_descriptions and self.include_description:
            print(f"🔍 获取岗位详细描述（最多 {max_jobs_with_desc} 个）...")
            
            jobs_with_desc = min(len(jobs_data), max_jobs_with_desc)
            fetched_count = 0
            
            for i, job in enumerate(jobs_data[:max_jobs_with_desc]):
                job_id = job.get('encryptJobId')
                security_id = job.get('securityId')
                
                if job_id:
                    print(f"  获取 {i+1}/{jobs_with_desc}: {job.get('jobName', '未知岗位')}")
                    
                    description = self.fetch_job_description(job_id, security_id)
                    job['jobDescription'] = description
                    
                    if description and "未能获取" not in description and "获取失败" not in description:
                        fetched_count += 1
                        print(f"    ✅ 获取成功 ({len(description)} 字符)")
                    else:
                        print(f"    ⚠️  获取失败或描述为空")
                    
                    # 避免请求过快
                    time.sleep(1.5)
                else:
                    job['jobDescription'] = "缺少岗位ID"
                    print(f"    ❌ 缺少岗位ID")
            
            print(f"✅ 成功获取 {fetched_count}/{jobs_with_desc} 个岗位的描述")
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"岗位数据_含描述_导出_{timestamp}.csv"
        csv_path = self.output_dir / filename
        
        # 导出CSV文件
        print(f"💾 导出到: {csv_path}")
        self._export_to_csv_with_description(jobs_data, csv_path)
        
        # 生成统计报告
        output_files = [str(csv_path)]
        
        stats_file = self._generate_statistics_with_description(jobs_data, csv_path)
        output_files.append(stats_file)
        
        preview_file = self._generate_preview_with_description(jobs_data, csv_path)
        output_files.append(preview_file)
        
        print(f"✅ 导出完成！共生成 {len(output_files)} 个文件")
        print(f"📁 输出目录: {self.output_dir}")
        
        return output_files
    
    def _export_to_csv_with_description(self, jobs_data: List[Dict], csv_path: Path):
        """导出数据到CSV文件（包含描述）"""
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = [col[0] for col in self.STANDARD_COLUMNS]
            writer.writerow(headers)
            
            # 写入数据
            for i, job in enumerate(jobs_data, 1):
                row = []
                
                for col_name, field_key, _ in self.STANDARD_COLUMNS:
                    if field_key == 'index':
                        value = i
                    elif field_key == 'data_time':
                        value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    elif field_key == 'jobTypeDesc':
                        value = self._get_job_type_desc(job.get('jobType'))
                    elif field_key == 'bossOnline':
                        value = '在线' if job.get('bossOnline') else '离线'
                    elif field_key == 'jobLink':
                        # 生成岗位链接
                        job_id = job.get('encryptJobId')
                        value = f"https://www.zhipin.com/job_detail/{job_id}.html" if job_id else ""
                    elif field_key in ['skills', 'welfareList']:
                        # 处理列表字段
                        field_data = job.get(field_key, [])
                        if isinstance(field_data, list):
                            value = '、'.join(field_data[:10])  # 限制数量
                        else:
                            value = str(field_data)
                    elif field_key == 'jobDescription':
                        # 处理岗位描述
                        description = job.get(field_key, '')
                        if not description and self.include_description:
                            description = "未获取岗位描述"
                        value = description
                    else:
                        value = job.get(field_key, '')
                    
                    # 清理数据
                    if isinstance(value, str):
                        value = value.replace('\n', ' ').replace('\r', ' ').strip()
                        # 对于描述字段，保留换行符，但限制长度
                        if field_key == 'jobDescription' and len(value) > 1000:
                            value = value[:997] + '...'
                        elif field_key != 'jobDescription' and len(value) > 200:
                            value = value[:197] + '...'
                    
                    row.append(value)
                
                writer.writerow(row)
        
        print(f"✅ CSV文件已生成: {len(jobs_data)} 行数据")
        print(f"📝 包含岗位描述: {'是' if self.include_description else '否'}")
        return csv_path
    
    def _get_job_type_desc(self, job_type):
        """获取岗位类型描述"""
        job_type_map = {
            0: '全职',
            1: '兼职', 
            2: '实习',
            3: '外包',
            4: '实习(在校)',
            5: '实习(毕业)'
        }
        return job_type_map.get(job_type, '未知')
    
    def _generate_statistics_with_description(self, jobs_data: List[Dict], csv_path: Path) -> str:
        """生成统计报告（包含描述统计）"""
        stats_file = csv_path.with_suffix('.统计分析.md')
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("# 岗位数据统计分析报告（包含岗位描述）\n\n")
            f.write("## 导出信息\n")
            f.write(f"- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **数据文件**: {csv_path.name}\n")
            f.write(f"- **总岗位数**: {len(jobs_data)} 个\n")
            f.write(f"- **包含岗位描述**: {'是' if self.include_description else '否'}\n")
            f.write(f"- **数据来源**: BOSS直聘\n\n")
            
            # 描述统计
            if self.include_description:
                f.write("## 岗位描述统计\n")
                
                descriptions = [job.get('jobDescription', '') for job in jobs_data]
                valid_descriptions = [d for d in descriptions if d and d not in ['未获取岗位描述', '未能获取详细描述', '缺少岗位ID']]
                
                f.write(f"- **有有效描述的岗位**: {len(valid_descriptions)} 个 ({len(valid_descriptions)/len(jobs_data)*100:.1f}%)\n")
                f.write(f"- **无描述的岗位**: {len(jobs_data) - len(valid_descriptions)} 个\n")
                
                if valid_descriptions:
                    avg_length = sum(len(d) for d in valid_descriptions) / len(valid_descriptions)
                    max_length = max(len(d) for d in valid_descriptions)
                    min_length = min(len(d) for d in valid_descriptions)
                    
                    f.write(f"- **平均描述长度**: {avg_length:.0f} 字符\n")
                    f.write(f"- **最长描述**: {max_length} 字符\n")
                    f.write(f"- **最短描述**: {min_length} 字符\n")
            
            # 薪资分析
            f.write("\n## 薪资分布分析\n")
            salaries = {}
            for job in jobs_data:
                salary = job.get('salaryDesc', '面议')
                salaries[salary] = salaries.get(salary, 0) + 1
            
            if salaries:
                f.write("| 薪资范围 | 岗位数量 | 占比 |\n")
                f.write("|----------|----------|------|\n")
                for salary, count in sorted(salaries.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs_data) * 100
                    f.write(f"| {salary} | {count} | {percentage:.1f}% |\n")
            else:
                f.write("无薪资数据\n")
            
            # 经验要求分析
            f.write("\n## 经验要求分析\n")
            experiences = {}
            for job in jobs_data:
                exp = job.get('jobExperience', '经验不限')
                experiences[exp] = experiences.get(exp, 0) + 1
            
            if experiences:
                f.write("| 经验要求 | 岗位数量 | 占比 |\n")
                f.write("|----------|----------|------|\n")
                for exp, count in sorted(experiences.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs_data) * 100
                    f.write(f"| {exp} | {count} | {percentage:.1f}% |\n")
            
            # Excel使用指南
            f.write("\n## Excel使用指南（含岗位描述）\n")
            f.write("### 1. 打开文件\n")
            f.write("```\n")
            f.write(f"# 用Excel打开\n")
            f.write(f"open \"{csv_path}\"\n")
            f.write("```\n\n")
            
            f.write("### 2. 查看岗位描述\n")
            f.write("1. 选中'岗位描述'列\n")
            f.write("2. 调整列宽：双击列标题右侧边界自动调整\n")
            f.write("3. 或者手动设置列宽\n")
            f.write("4. 使用'换行文本'格式查看完整描述\n\n")
            
            f.write("### 3. 数据筛选\n")
            f.write("1. 选中表头行（第1行）\n")
            f.write("2. 点击菜单：数据 → 筛选\n")
            f.write("3. 点击列标题的筛选箭头进行筛选\n")
            f.write("4. 在'岗位描述'列可以搜索关键词\n\n")
            
            f.write("### 4. 按描述关键词筛选\n")
            f.write("1. 点击'岗位描述'列的筛选箭头\n")
            f.write("2. 选择'文本筛选' → '包含'\n")
            f.write("3. 输入关键词如：'AI'、'Python'、'机器学习'\n")
            f.write("4. 点击确定查看匹配的岗位\n\n")
            
            f.write("### 5. 保存为Excel格式\n")
            f.write("1. 点击菜单：文件 → 另存为\n")
            f.write("2. 选择保存类型：Excel工作簿 (.xlsx)\n")
            f.write("3. 输入文件名并保存\n")
            f.write("4. 注意：.xlsx格式支持更长的文本内容\n")
        
        print(f"✅ 统计报告已生成: {stats_file}")
        return str(stats_file)
    
    def _generate_preview_with_description(self, jobs_data: List[Dict], csv_path: Path) -> str:
        """生成数据预览（包含描述）"""
        preview_file = csv_path.with_suffix('.数据预览.txt')
        
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write("岗位数据预览（包含岗位描述）\n")
            f.write("=" * 60 + "\n")
            f.write(f"总岗位数: {len(jobs_data)} 个\n")
            f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {csv_path.name}\n")
            f.write(f"包含岗位描述: {'是' if self.include_description else '否'}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("前5个岗位示例（包含描述）:\n\n")
            
            for i, job in enumerate(jobs_data[:5], 1):
                f.write(f"{'='*50}\n")
                f.write(f"【岗位 {i}】\n")
                f.write(f"{'='*50}\n")
                f.write(f"岗位名称: {job.get('jobName', '')}\n")
                f.write(f"公司名称: {job.get('brandName', '')}\n")
                f.write(f"薪资: {job.get('salaryDesc', '面议')}\n")
                f.write(f"经验要求: {job.get('jobExperience', '经验不限')}\n")
                f.write(f"学历要求: {job.get('jobDegree', '学历不限')}\n")
                f.write(f"地区: {job.get('areaDistrict', '深圳')}\n")
                f.write(f"公司规模: {job.get('brandScaleName', '')}\n")
                f.write(f"搜索关键词: {job.get('search_keyword', '')}\n")
                f.write(f"来源页数: 第{job.get('search_page', 1)}页\n")
                
                # 岗位描述
                if self.include_description:
                    description = job.get('jobDescription', '未获取岗位描述')
                    f.write(f"\n【岗位描述】\n")
                    f.write(f"{'-'*30}\n")
                    
                    if description and len(description) > 500:
                        f.write(f"{description[:500]}...\n")
                        f.write(f"...（完整描述共 {len(description)} 字符）\n")
                    else:
                        f.write(f"{description}\n")
                
                f.write("\n\n")
        
        print(f"✅ 数据预览已生成: {preview_file}")
        return str(preview_file)


# 命令行接口
def main():
    """命令行主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='导出BOSS直聘岗位数据到Excel（包含岗位描述）')
    
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--no-description', action='store_true', help='不获取岗位描述')
    parser.add_argument('--max-descriptions', type=int, default=50, help='最多获取描述的岗位数（默认50）')
    
    args = parser.parse_args()
    
    print("🚀 开始导出Excel数据（包含岗位描述）")
    print("=" * 50)
    
    # 加载数据
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取岗位列表
        if isinstance(data, list):
            jobs_data = data
        elif 'data' in data and 'jobList' in data['data']:
            jobs_data = data['data']['jobList']
        elif 'jobList' in data:
            jobs_data = data['jobList']
        else:
            jobs_data = [data] if isinstance(data, dict) else []
            
        print(f"📊 加载 {len(jobs_data)} 个岗位数据")
        
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return
    
    # 创建导出器
    include_description = not args.no_description
    exporter = ExcelExporterWithDescription(
        output_dir=args.output_dir,
        include_description=include_description
    )
    
    # 导出数据
    try:
        output_files = exporter.export_jobs_with_descriptions(
            jobs_data,
            fetch_descriptions=include_description,
            max_jobs_with_desc=args.max_descriptions
        )
        
        print(f"\n🎉 导出成功！")
        print(f"📁 主要文件: {output_files[0]}")
        
        if include_description:
            print(f"📝 包含岗位描述: 是（最多 {args.max_descriptions} 个）")
        else:
            print(f"📝 包含岗位描述: 否")
        
        print(f"\n💡 立即用Excel打开:")
        print(f"  open \"{output_files[0]}\"")
        
        print(f"\n📋 所有生成的文件:")
        for file in output_files:
            print(f"  • {os.path.basename(file)}")
            
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()