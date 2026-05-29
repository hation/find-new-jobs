#!/usr/bin/env python3
"""
Job Search技能 - Excel导出模板
标准化的Excel格式数据导出，包含所有必要字段和统计分析
"""

import os
import sys
import csv
import json
import time
from datetime import datetime
from pathlib import Path

class ExcelExporter:
    """Excel格式数据导出器"""
    
    # 标准字段定义
    STANDARD_COLUMNS = [
        ('序号', 'index', '序号'),
        ('岗位名称', 'jobName', '岗位名称'),
        ('公司名称', 'brandName', '公司名称'),
        ('薪资', 'salaryDesc', '薪资范围'),
        ('经验要求', 'jobExperience', '工作经验要求'),
        ('学历要求', 'jobDegree', '学历要求'),
        ('地区', 'areaDistrict', '工作地区'),
        ('公司规模', 'brandScaleName', '公司员工规模'),
        ('融资阶段', 'brandStageName', '公司融资阶段'),
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
    ]
    
    def __init__(self, output_dir=None):
        """初始化导出器"""
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = Path.home() / "招聘数据" / f"Excel导出_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_jobs_to_excel(self, jobs_data, filename=None, include_stats=True):
        """
        导出岗位数据到Excel格式（CSV）
        
        Args:
            jobs_data: 岗位数据列表
            filename: 输出文件名（可选）
            include_stats: 是否包含统计报告
        
        Returns:
            导出的文件路径列表
        """
        print("🚀 开始导出Excel格式数据")
        print("=" * 60)
        
        if not jobs_data:
            print("❌ 没有数据可导出")
            return []
        
        print(f"📊 准备导出 {len(jobs_data)} 个岗位数据")
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"岗位数据_导出_{timestamp}.csv"
        
        csv_path = self.output_dir / filename
        
        # 导出CSV文件
        print(f"💾 导出到: {csv_path}")
        self._export_to_csv(jobs_data, csv_path)
        
        # 生成统计报告
        output_files = [str(csv_path)]
        
        if include_stats:
            stats_file = self._generate_statistics(jobs_data, csv_path)
            output_files.append(stats_file)
            
            preview_file = self._generate_preview(jobs_data, csv_path)
            output_files.append(preview_file)
            
            config_file = self._generate_config_file()
            output_files.append(config_file)
        
        print(f"✅ 导出完成！共生成 {len(output_files)} 个文件")
        print(f"📁 输出目录: {self.output_dir}")
        
        return output_files
    
    def _export_to_csv(self, jobs_data, csv_path):
        """导出数据到CSV文件"""
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
                    elif field_key in ['skills', 'welfareList']:
                        # 处理列表字段
                        field_data = job.get(field_key, [])
                        if isinstance(field_data, list):
                            value = '、'.join(field_data[:10])  # 限制数量
                        else:
                            value = str(field_data)
                    else:
                        value = job.get(field_key, '')
                    
                    # 清理数据
                    if isinstance(value, str):
                        value = value.replace('\n', ' ').replace('\r', ' ').strip()
                        if len(value) > 200:  # 限制长度
                            value = value[:197] + '...'
                    
                    row.append(value)
                
                writer.writerow(row)
        
        print(f"✅ CSV文件已生成: {len(jobs_data)} 行数据")
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
    
    def _generate_statistics(self, jobs_data, csv_path):
        """生成统计报告"""
        stats_file = csv_path.with_suffix('.统计分析.md')
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            f.write("# 岗位数据统计分析报告\n\n")
            f.write("## 导出信息\n")
            f.write(f"- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **数据文件**: {csv_path.name}\n")
            f.write(f"- **总岗位数**: {len(jobs_data)} 个\n")
            f.write(f"- **数据来源**: BOSS直聘\n\n")
            
            # 薪资分析
            f.write("## 薪资分布分析\n")
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
            
            # 地区分布分析
            f.write("\n## 地区分布分析\n")
            areas = {}
            for job in jobs_data:
                area = job.get('areaDistrict', '未知')
                areas[area] = areas.get(area, 0) + 1
            
            if areas:
                f.write("| 工作地区 | 岗位数量 | 占比 |\n")
                f.write("|----------|----------|------|\n")
                for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs_data) * 100
                    f.write(f"| {area} | {count} | {percentage:.1f}% |\n")
            
            # 公司规模分析
            f.write("\n## 公司规模分析\n")
            company_sizes = {}
            for job in jobs_data:
                size = job.get('brandScaleName', '')
                if size:
                    company_sizes[size] = company_sizes.get(size, 0) + 1
            
            if company_sizes:
                f.write("| 公司规模 | 岗位数量 | 占比 |\n")
                f.write("|----------|----------|------|\n")
                for size, count in sorted(company_sizes.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs_data) * 100
                    f.write(f"| {size} | {count} | {percentage:.1f}% |\n")
            
            # Excel使用指南
            f.write("\n## Excel使用指南\n")
            f.write("### 1. 打开文件\n")
            f.write("```\n")
            f.write(f"# 用Excel打开\n")
            f.write(f"open \"{csv_path}\"\n")
            f.write("```\n\n")
            
            f.write("### 2. 数据筛选\n")
            f.write("1. 选中表头行（第1行）\n")
            f.write("2. 点击菜单：数据 → 筛选\n")
            f.write("3. 点击列标题的筛选箭头进行筛选\n\n")
            
            f.write("### 3. 常用筛选条件\n")
            f.write("- **按薪资筛选**: 点击'薪资'列筛选箭头\n")
            f.write("- **按经验筛选**: 点击'经验要求'列筛选箭头\n")
            f.write("- **按地区筛选**: 点击'地区'列筛选箭头\n")
            f.write("- **按公司规模筛选**: 点击'公司规模'列筛选箭头\n\n")
            
            f.write("### 4. 数据透视表（高级分析）\n")
            f.write("1. 选中数据区域\n")
            f.write("2. 点击菜单：插入 → 数据透视表\n")
            f.write("3. 拖拽字段到行、列、值区域\n")
            f.write("4. 示例：行区域放\"地区\"，值区域放\"薪资\"\n")
