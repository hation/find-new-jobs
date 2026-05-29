#!/usr/bin/env python3
"""
扩展Excel导出器 - 35个完整字段
基于boss detail返回的完整数据，提供更全面的岗位信息导出
"""

import os
import sys
import csv
import json
import time
from datetime import datetime
from pathlib import Path

# 添加父目录到路径，以便导入现有导出器
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_to_excel import ExcelExporter

class ExtendedExcelExporter(ExcelExporter):
    """扩展的Excel导出器 - 35个完整字段"""
    
    # 扩展字段定义 (21个原有字段 + 14个新增字段)
    EXTENDED_COLUMNS = [
        # 1. 基础信息 (6个字段)
        ('序号', 'index', '自动编号'),
        ('岗位名称', 'jobName', '完整岗位名称'),
        ('薪资范围', 'salaryDesc', '薪资描述（如15-30K）'),
        ('工作经验', 'experienceName', '经验要求'),
        ('学历要求', 'degreeName', '学历要求'),
        ('职位类型', 'positionName', '职位分类'),
        
        # 2. 公司信息 (8个字段)
        ('公司名称', 'brandName', '公司全名'),
        ('公司规模', 'scaleName', '员工规模'),
        ('融资阶段', 'stageName', '融资状态'),
        ('所属行业', 'industryName', '行业分类'),
        ('公司介绍', 'introduce', '公司简介'),
        ('福利待遇', 'welfareList', '福利列表（逗号分隔）'),
        ('公司标签', 'brandLabels', '公司特色标签'),
        ('公司ID', 'encryptBrandId', '公司唯一标识'),
        
        # 3. 工作地点 (5个字段)
        ('工作地区', 'locationName', '地区名称'),
        ('详细地址', 'address', '完整地址'),
        ('经度', 'longitude', '地理位置经度'),
        ('纬度', 'latitude', '地理位置纬度'),
        ('地图URL', 'staticMapUrl', '静态地图链接'),
        
        # 4. 岗位详情 (8个字段)
        ('岗位描述', 'postDescription', '完整岗位描述'),
        ('技能要求', 'showSkills', '技能列表（逗号分隔）'),
        ('岗位状态', 'jobStatusDesc', '招聘状态'),
        ('岗位ID', 'encryptJobId', '职位唯一标识'),
        ('安全ID', 'securityId', 'API调用的securityId'),
        ('岗位来源', 'jobSource', '来源URL或分类'),
        ('岗位有效期', 'jobValid', '招聘有效期'),
        ('岗位标签', 'jobLabels', '岗位特色标签'),
        
        # 5. 招聘者信息 (5个字段)
        ('招聘者姓名', 'bossName', '招聘负责人'),
        ('招聘者职位', 'bossTitle', '负责人职位'),
        ('招聘者头像', 'bossAvatar', '头像URL'),
        ('活跃状态', 'bossActive', '最近活跃时间'),
        ('在线状态', 'bossOnline', '是否在线'),
        
        # 6. 搜索元数据 (3个字段)
        ('搜索关键词', 'searchKeyword', '搜索关键词'),
        ('来源页数', 'searchPage', '搜索结果页码'),
        ('数据时间', 'dataTime', '数据获取时间戳'),
    ]
    
    def __init__(self, output_dir=None):
        """初始化扩展导出器"""
        super().__init__(output_dir)
        # 使用扩展字段
        self.STANDARD_COLUMNS = self.EXTENDED_COLUMNS
        
    def extract_from_detail_json(self, detail_json, search_keyword="AI", search_page=1):
        """
        从boss detail JSON中提取35个字段数据
        
        Args:
            detail_json: boss detail返回的完整JSON数据
            search_keyword: 搜索关键词
            search_page: 搜索结果页码
        
        Returns:
            包含35个字段的数据字典
        """
        if not detail_json or not detail_json.get('ok'):
            return None
        
        data = detail_json['data']
        job_info = data.get('jobInfo', {})
        brand_info = data.get('brandComInfo', {})
        boss_info = data.get('bossInfo', {})
        
        # 提取数据
        extracted = {
            # 基础信息
            'jobName': job_info.get('jobName', ''),
            'salaryDesc': job_info.get('salaryDesc', ''),
            'experienceName': job_info.get('experienceName', ''),
            'degreeName': job_info.get('degreeName', ''),
            'positionName': job_info.get('positionName', ''),
            
            # 公司信息
            'brandName': brand_info.get('brandName', ''),
            'scaleName': brand_info.get('scaleName', ''),
            'stageName': brand_info.get('stageName', ''),
            'industryName': brand_info.get('industryName', ''),
            'introduce': brand_info.get('introduce', ''),
            'welfareList': self._list_to_str(brand_info.get('labels', [])),
            'brandLabels': self._list_to_str(brand_info.get('labels', [])),
            'encryptBrandId': brand_info.get('encryptBrandId', ''),
            
            # 工作地点
            'locationName': job_info.get('locationName', ''),
            'address': job_info.get('address', ''),
            'longitude': job_info.get('longitude', ''),
            'latitude': job_info.get('latitude', ''),
            'staticMapUrl': job_info.get('staticMapUrl', ''),
            
            # 岗位详情
            'postDescription': job_info.get('postDescription', ''),
            'showSkills': self._list_to_str(job_info.get('showSkills', [])),
            'jobStatusDesc': job_info.get('jobStatusDesc', ''),
            'encryptJobId': job_info.get('encryptId', ''),
            'securityId': data.get('securityId', ''),
            'jobSource': job_info.get('locationUrl', ''),
            'jobValid': job_info.get('jobValidStatus', ''),
            'jobLabels': self._list_to_str(job_info.get('jobLabels', [])),
            
            # 招聘者信息
            'bossName': boss_info.get('name', ''),
            'bossTitle': boss_info.get('title', ''),
            'bossAvatar': boss_info.get('tiny', ''),
            'bossActive': boss_info.get('activeTimeDesc', ''),
            'bossOnline': '是' if boss_info.get('bossOnline') else '否',
            
            # 搜索元数据
            'searchKeyword': search_keyword,
            'searchPage': search_page,
            'dataTime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        return extracted
    
    def _list_to_str(self, items, max_items=10, separator='、'):
        """将列表转换为字符串"""
        if not items:
            return ''
        
        if isinstance(items, list):
            # 限制项目数量
            limited_items = items[:max_items]
            result = separator.join(str(item) for item in limited_items)
            
            if len(items) > max_items:
                result += f'... (共{len(items)}项)'
            
            return result
        else:
            return str(items)
    
    def _export_to_csv(self, jobs_data, csv_path):
        """导出数据到CSV文件（重写以处理扩展字段）"""
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # 写入表头
            headers = [col[0] for col in self.EXTENDED_COLUMNS]
            writer.writerow(headers)
            
            # 写入数据
            for i, job in enumerate(jobs_data, 1):
                row = []
                
                for col_name, field_key, _ in self.EXTENDED_COLUMNS:
                    if field_key == 'index':
                        value = i
                    elif field_key in ['bossOnline']:
                        # 特殊字段处理
                        if field_key in job:
                            value = '在线' if job[field_key] == '是' else '离线'
                        else:
                            value = ''
                    elif field_key in ['postDescription', 'introduce']:
                        # 长文本字段，需要特殊处理
                        value = job.get(field_key, '')
                        if isinstance(value, str):
                            # 清理换行符，限制长度
                            value = value.replace('\n', ' ').replace('\r', ' ').strip()
                            if len(value) > 500:  # 岗位描述和公司介绍可能很长
                                value = value[:497] + '...'
                    else:
                        value = job.get(field_key, '')
                    
                    # 通用数据清理
                    if isinstance(value, str):
                        value = value.strip()
                    
                    row.append(value)
                
                writer.writerow(row)
        
        print(f"✅ 扩展CSV文件已生成: {len(jobs_data)} 行 × {len(self.EXTENDED_COLUMNS)} 列")
        return csv_path
    
    def export_detail_data(self, detail_data_list, search_keyword="AI", search_page=1, 
                          filename=None, include_stats=True):
        """
        导出boss detail数据到Excel
        
        Args:
            detail_data_list: boss detail JSON数据列表
            search_keyword: 搜索关键词
            search_page: 搜索结果页码
            filename: 输出文件名
            include_stats: 是否包含统计报告
        
        Returns:
            导出的文件路径列表
        """
        print(f"🚀 开始导出扩展Excel数据")
        print(f"📊 处理 {len(detail_data_list)} 个职位详情")
        
        # 提取数据
        extracted_data = []
        for i, detail_json in enumerate(detail_data_list, 1):
            print(f"  提取第 {i}/{len(detail_data_list)} 个职位...", end='\r')
            data = self.extract_from_detail_json(detail_json, search_keyword, search_page)
            if data:
                extracted_data.append(data)
        
        print(f"\n✅ 成功提取 {len(extracted_data)} 个职位数据")
        
        if not extracted_data:
            print("❌ 没有可导出的数据")
            return []
        
        # 导出Excel
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"深圳_{search_keyword}_岗位_完整数据_{timestamp}.csv"
        
        return self.export_jobs_to_excel(extracted_data, filename, include_stats)


# 命令行工具
def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='扩展Excel导出工具 - 35个字段')
    parser.add_argument('--json-files', nargs='+', help='boss detail JSON文件列表')
    parser.add_argument('--search-keyword', default='AI', help='搜索关键词')
    parser.add_argument('--search-page', type=int, default=1, help='搜索结果页码')
    parser.add_argument('--output-dir', help='输出目录')
    parser.add_argument('--output-name', help='输出文件名')
    
    args = parser.parse_args()
    
    if not args.json_files:
        print("❌ 请提供JSON文件路径")
        parser.print_help()
        return
    
    # 创建导出器
    exporter = ExtendedExcelExporter(args.output_dir)
    
    # 加载JSON数据
    detail_data_list = []
    for json_file in args.json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                detail_data_list.append(data)
                print(f"✅ 加载: {json_file}")
        except Exception as e:
            print(f"❌ 加载失败 {json_file}: {e}")
    
    if not detail_data_list:
        print("❌ 没有有效的JSON数据")
        return
    
    # 导出数据
    output_files = exporter.export_detail_data(
        detail_data_list,
        search_keyword=args.search_keyword,
        search_page=args.search_page,
        filename=args.output_name
    )
    
    if output_files:
        print(f"\n🎉 导出完成！")
        print(f"📁 主文件: {output_files[0]}")
        print(f"📊 共生成 {len(output_files)} 个文件")


if __name__ == "__main__":
    main()