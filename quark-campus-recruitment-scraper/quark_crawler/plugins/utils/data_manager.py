#!/usr/bin/env python3
# 🏗️ 夸克爬取器 - 数据管理器插件
# 版本: 1.0
# 创建时间: 2026-05-19
# 基于: 标准化数据管理，解决文件组织混乱问题

import os
import sys
import json
import time
import csv
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import asdict

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from core.interfaces import IDataManager, PositionData, DataError


class StandardDataManager(IDataManager):
    """标准化数据管理器 - 解决文件组织混乱问题"""
    
    def __init__(self):
        self.initialized = False
        self.output_dir = None
        self.project_name = "夸克校园招聘爬取器"
        
        # 目录结构
        self.dirs = {
            "positions": "positions",     # 岗位级数据
            "pages": "pages",             # 页面级数据  
            "final": "final",             # 最终汇总
            "reports": "reports",         # 报告文件
            "backups": "backups",         # 备份文件
            "logs": "logs",               # 日志文件
            "temp": "temp"                # 临时文件
        }
        
        # 文件命名规范
        self.filename_templates = {
            "position": "quark_page{page}_position_{index}_{timestamp}",
            "page": "quark_page{page}_data_{timestamp}",
            "full": "quark_all_positions_{timestamp}",
            "report": "quark_report_{timestamp}",
            "stats": "quark_stats_{timestamp}"
        }
        
        # 状态跟踪
        self.position_count = 0
        self.page_count = 0
        self.last_save_time = None
        self.backup_count = 0
        
        print(f"📁 初始化标准化数据管理器")
        print(f"📝 项目: {self.project_name}")
    
    def initialize(self, output_dir: str) -> bool:
        """初始化数据管理器"""
        try:
            self.output_dir = output_dir
            
            print(f"📂 设置输出目录: {output_dir}")
            
            # 创建目录结构
            print("📁 创建目录结构...")
            self._create_directory_structure()
            
            # 验证目录权限
            print("🔍 验证目录权限...")
            self._validate_permissions()
            
            # 加载现有数据
            print("📊 加载现有数据...")
            self._load_existing_data()
            
            # 创建初始报告
            print("📈 创建初始报告...")
            self._create_initial_report()
            
            self.initialized = True
            self.last_save_time = datetime.now()
            
            print(f"✅ 数据管理器初始化完成")
            print(f"📊 目录结构: {len(self.dirs)} 个目录")
            print(f"📈 现有数据: {self.position_count} 个岗位, {self.page_count} 个页面")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据管理器初始化失败: {e}")
            return False
    
    def _create_directory_structure(self) -> None:
        """创建标准化目录结构"""
        base_dir = self.output_dir
        
        # 确保基础目录存在
        os.makedirs(base_dir, exist_ok=True)
        
        # 创建所有子目录
        for dir_name, dir_path in self.dirs.items():
            full_path = os.path.join(base_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
            
            # 创建README文件
            readme_path = os.path.join(full_path, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {dir_name.upper()} 目录\n\n")
                    f.write(f"此目录用于存储: {self._get_directory_description(dir_name)}\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"项目: {self.project_name}\n")
            
            print(f"  📁 创建目录: {dir_path}")
    
    def _get_directory_description(self, dir_name: str) -> str:
        """获取目录描述"""
        descriptions = {
            "positions": "单个岗位的详细数据文件 (JSON格式)",
            "pages": "按页面组织的岗位数据文件 (每页一个文件)",
            "final": "最终汇总的数据文件 (JSON和Excel格式)",
            "reports": "数据分析报告和统计信息",
            "backups": "数据备份文件 (按时间戳备份)",
            "logs": "执行日志和错误记录",
            "temp": "临时文件 (可定期清理)"
        }
        return descriptions.get(dir_name, "未定义目录")
    
    def _validate_permissions(self) -> None:
        """验证目录权限"""
        base_dir = self.output_dir
        
        # 检查写入权限
        test_file = os.path.join(base_dir, ".permission_test")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print("  ✅ 写入权限验证通过")
        except Exception as e:
            raise DataError(f"目录写入权限不足: {e}")
        
        # 检查磁盘空间
        try:
            import shutil
            total, used, free = shutil.disk_usage(base_dir)
            free_gb = free / (1024**3)
            
            if free_gb < 1:  # 小于1GB
                print(f"  ⚠️  磁盘空间不足: {free_gb:.2f} GB 可用")
            else:
                print(f"  ✅ 磁盘空间充足: {free_gb:.2f} GB 可用")
        except:
            print("  ⚠️  无法检查磁盘空间")
    
    def _load_existing_data(self) -> None:
        """加载现有数据"""
        try:
            # 统计positions目录
            positions_dir = os.path.join(self.output_dir, self.dirs["positions"])
            if os.path.exists(positions_dir):
                position_files = [f for f in os.listdir(positions_dir) if f.endswith('.json')]
                self.position_count = len(position_files)
                print(f"  📊 positions目录: {self.position_count} 个文件")
            
            # 统计pages目录
            pages_dir = os.path.join(self.output_dir, self.dirs["pages"])
            if os.path.exists(pages_dir):
                page_files = [f for f in os.listdir(pages_dir) if f.endswith('.json')]
                self.page_count = len(page_files)
                print(f"  📊 pages目录: {self.page_count} 个文件")
            
            # 查找最新汇总文件
            final_dir = os.path.join(self.output_dir, self.dirs["final"])
            if os.path.exists(final_dir):
                final_files = [f for f in os.listdir(final_dir) if f.endswith('.json')]
                if final_files:
                    latest_file = max(final_files)
                    print(f"  📊 final目录: 最新文件 {latest_file}")
            
        except Exception as e:
            print(f"  ⚠️  加载现有数据失败: {e}")
    
    def _create_initial_report(self) -> None:
        """创建初始报告"""
        try:
            report_content = f"""# 📊 {self.project_name} - 数据管理报告
## 项目信息
- **项目名称**: {self.project_name}
- **输出目录**: {self.output_dir}
- **初始化时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **数据管理器版本**: 1.0

## 目录结构
```
{self.output_dir}/
├── {self.dirs['positions']}/      # 单个岗位数据 (JSON)
├── {self.dirs['pages']}/          # 页面级数据 (JSON)
├── {self.dirs['final']}/          # 最终汇总数据 (JSON/Excel)
├── {self.dirs['reports']}/        # 分析报告
├── {self.dirs['backups']}/        # 数据备份
├── {self.dirs['logs']}/           # 执行日志
└── {self.dirs['temp']}/           # 临时文件
```

## 初始状态
- **现有岗位数据**: {self.position_count} 个
- **现有页面数据**: {self.page_count} 个
- **目录创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 文件命名规范
1. **岗位文件**: `quark_page{page}_position_{index}_{timestamp}.json`
2. **页面文件**: `quark_page{page}_data_{timestamp}.json`
3. **汇总文件**: `quark_all_positions_{timestamp}.json`
4. **报告文件**: `quark_report_{timestamp}.txt`

## 使用说明
1. 所有数据文件使用UTF-8编码
2. JSON文件使用2空格缩进
3. 定期备份重要数据
4. 临时文件可定期清理

---
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            report_dir = os.path.join(self.output_dir, self.dirs["reports"])
            report_file = os.path.join(report_dir, "data_manager_initial_report.md")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"  📄 创建初始报告: {report_file}")
            
        except Exception as e:
            print(f"  ⚠️  创建初始报告失败: {e}")
    
    def save_position(self, data: PositionData) -> str:
        """保存单个岗位数据"""
        if not self.initialized:
            raise DataError("数据管理器未初始化")
        
        try:
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.filename_templates["position"].format(
                page=data.page_number,
                index=data.position_index,
                timestamp=timestamp
            ) + ".json"
            
            # 确定保存路径
            save_dir = os.path.join(self.output_dir, self.dirs["positions"])
            file_path = os.path.join(save_dir, filename)
            
            # 准备数据
            data_dict = asdict(data)
            
            # 添加元数据
            data_dict["_metadata"] = {
                "saved_at": datetime.now().isoformat(),
                "file_path": file_path,
                "field_count": len([v for v in data_dict.values() if v]),
                "data_manager_version": "1.0"
            }
            
            # 验证数据完整性
            missing_fields = data.validate()
            if missing_fields:
                data_dict["_metadata"]["missing_fields"] = missing_fields
                data_dict["_metadata"]["validation_status"] = "partial"
            else:
                data_dict["_metadata"]["validation_status"] = "complete"
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data_dict, f, ensure_ascii=False, indent=2)
            
            # 更新统计
            self.position_count += 1
            self.last_save_time = datetime.now()
            
            # 创建简化版本（用于快速查看）
            simple_file = file_path.replace('.json', '_simple.json')
            simple_data = {
                "position_id": data.position_id,
                "position_name": data.position_name,
                "work_location": data.work_location,
                "department": data.department,
                "education_requirement": data.education_requirement,
                "extraction_time": data.extraction_time
            }
            
            with open(simple_file, 'w', encoding='utf-8') as f:
                json.dump(simple_data, f, ensure_ascii=False, indent=2)
            
            print(f"  💾 保存岗位数据: {filename}")
            print(f"    📍 位置: {os.path.relpath(file_path, self.output_dir)}")
            
            if missing_fields:
                print(f"    ⚠️  数据不完整，缺失字段: {missing_fields}")
            else:
                print(f"    ✅ 数据完整 (12个字段)")
            
            return file_path
            
        except Exception as e:
            print(f"❌ 保存岗位数据失败: {e}")
            raise DataError(f"保存岗位数据失败: {e}")
    
    def save_page_data(self, page_number: int, positions: List[PositionData]) -> str:
        """保存页面数据"""
        if not self.initialized:
            raise DataError("数据管理器未初始化")
        
        try:
            if not positions:
                print(f"⚠️  第 {page_number} 页没有数据可保存")
                return ""
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.filename_templates["page"].format(
                page=page_number,
                timestamp=timestamp
            ) + ".json"
            
            # 确定保存路径
            save_dir = os.path.join(self.output_dir, self.dirs["pages"])
            file_path = os.path.join(save_dir, filename)
            
            # 准备数据
            page_data = {
                "page_number": page_number,
                "total_positions": len(positions),
                "extraction_time": datetime.now().isoformat(),
                "positions": [asdict(pos) for pos in positions]
            }
            
            # 添加统计信息
            complete_positions = 0
            partial_positions = 0
            empty_positions = 0
            
            for pos in positions:
                missing = pos.validate()
                if not missing:
                    complete_positions += 1
                elif len(missing) < 6:
                    partial_positions += 1
                else:
                    empty_positions += 1
            
            page_data["statistics"] = {
                "complete": complete_positions,
                "partial": partial_positions,
                "empty": empty_positions,
                "completion_rate": (complete_positions / len(positions)) * 100 if positions else 0
            }
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, ensure_ascii=False, indent=2)
            
            # 更新统计
            self.page_count += 1
            
            print(f"📄 保存页面数据: 第 {page_number} 页 ({len(positions)} 个岗位)")
            print(f"   📊 数据完整性: {complete_positions}完整/{partial_positions}部分/{empty_positions}空")
            print(f"   📍 位置: {os.path.relpath(file_path, self.output_dir)}")
            
            return file_path
            
        except Exception as e:
            print(f"❌ 保存页面数据失败: {e}")
            raise DataError(f"保存页面数据失败: {e}")
    
    def save_full_data(self, all_positions: List[PositionData]) -> str:
        """保存完整数据"""
        if not self.initialized:
            raise DataError("数据管理器未初始化")
        
        try:
            if not all_positions:
                print("⚠️  没有数据可保存")
                return ""
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_filename = self.filename_templates["full"].format(timestamp=timestamp) + ".json"
            excel_filename = self.filename_templates["full"].format(timestamp=timestamp) + ".xlsx"
            
            # 确定保存路径
            save_dir = os.path.join(self.output_dir, self.dirs["final"])
            json_path = os.path.join(save_dir, json_filename)
            excel_path = os.path.join(save_dir, excel_filename)
            
            # 准备数据
            full_data = {
                "project": self.project_name,
                "total_positions": len(all_positions),
                "generated_at": datetime.now().isoformat(),
                "data_manager_version": "1.0",
                "positions": [asdict(pos) for pos in all_positions]
            }
            
            # 添加详细统计
            position_stats = {
                "by_page": {},
                "by_department": {},
                "by_location": {},
                "by_education": {},
                "field_completion": {}
            }
            
            # 统计字段完成情况
            field_names = [
                "position_name", "work_location", "position_category", "publish_time",
                "department", "education_requirement", "work_experience",
                "job_responsibilities", "job_requirements", "other_info"
            ]
            
            for field in field_names:
                completed = sum(1 for pos in all_positions if getattr(pos, field, ""))
                position_stats["field_completion"][field] = {
                    "completed": completed,
                    "total": len(all_positions),
                    "rate": (completed / len(all_positions)) * 100 if all_positions else 0
                }
            
            # 按页面统计
            for pos in all_positions:
                page = pos.page_number
                if page not in position_stats["by_page"]:
                    position_stats["by_page"][page] = 0
                position_stats["by_page"][page] += 1
            
            # 按部门统计
            for pos in all_positions:
                dept = pos.department
                if dept:
                    if dept not in position_stats["by_department"]:
                        position_stats["by_department"][dept] = 0
                    position_stats["by_department"][dept] += 1
            
            full_data["statistics"] = position_stats
            
            # 保存JSON文件
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, ensure_ascii=False, indent=2)
            
            # 保存Excel文件（如果可能）
            try:
                import pandas as pd
                
                # 转换为DataFrame
                data_list = [asdict(pos) for pos in all_positions]
                df = pd.DataFrame(data_list)
                
                # 保存为Excel
                df.to_excel(excel_path, index=False, engine='openpyxl')
                
                print(f"📊 保存Excel文件: {excel_filename}")
            except ImportError:
                print("⚠️  未安装pandas，跳过Excel导出")
                excel_path = None
            except Exception as e:
                print(f"⚠️  Excel导出失败: {e}")
                excel_path = None
            
            # 创建CSV版本（备用）
            csv_filename = self.filename_templates["full"].format(timestamp=timestamp) + ".csv"
            csv_path = os.path.join(save_dir, csv_filename)
            
            try:
                if data_list:
                    # 获取所有字段
                    fieldnames = set()
                    for item in data_list:
                        fieldnames.update(item.keys())
                    
                    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
                        writer.writeheader()
                        writer.writerows(data_list)
                    
                    print(f"📊 保存CSV文件: {csv_filename}")
            except Exception as e:
                print(f"⚠️  CSV导出失败: {e}")
            
            print(f"📦 保存完整数据: {len(all_positions)} 个岗位")
            print(f"   📄 JSON: {os.path.relpath(json_path, self.output_dir)}")
            if excel_path:
                print(f"   📊 Excel: {os.path.relpath(excel_path, self.output_dir)}")
            if os.path.exists(csv_path):
                print(f"   📊 CSV: {os.path.relpath(csv_path, self.output_dir)}")
            
            return json_path
            
        except Exception as e:
            print(f"❌ 保存完整数据失败: {e}")
            raise DataError(f"保存完整数据失败: {e}")
    
    def generate_report(self, positions: List[PositionData]) -> str:
        """生成报告"""
        if not self.initialized:
            raise DataError("数据管理器未初始化")
        
        try:
            if not positions:
                print("⚠️  没有数据可生成报告")
                return ""
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.filename_templates["report"].format(timestamp=timestamp) + ".txt"
            
            # 确定保存路径
            save_dir = os.path.join(self.output_dir, self.dirs["reports"])
            file_path = os.path.join(save_dir, filename)
            
            # 生成报告内容
            report_lines = []
            
            # 标题
            report_lines.append("=" * 60)
            report_lines.append(f"📊 {self.project_name} - 数据提取报告")
            report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("=" * 60)
            report_lines.append("")
            
            # 总体统计
            report_lines.append("## 📈 总体统计")
            report_lines.append(f"- 总岗位数: {len(positions)}")
            
            # 数据完整性统计
            complete_count = 0
            partial_count = 0
            empty_count = 0
            
            for pos in positions:
                missing = pos.validate()
                if not missing:
                    complete_count += 1
                elif len(missing) < 6:
                    partial_count += 1
                else:
                    empty_count += 1
            
            report_lines.append(f"- 完整数据: {complete_count} ({complete_count/len(positions)*100:.1f}%)")
            report_lines.append(f"- 部分数据: {partial_count} ({partial_count/len(positions)*100:.1f}%)")
            report_lines.append(f"- 空数据: {empty_count} ({empty_count/len(positions)*100:.1f}%)")
            report_lines.append("")
            
            # 按页面统计
            report_lines.append("## 📄 按页面统计")
            page_stats = {}
            for pos in positions:
                page = pos.page_number
                if page not in page_stats:
                    page_stats[page] = 0
                page_stats[page] += 1
            
            for page in sorted(page_stats.keys()):
                report_lines.append(f"- 第 {page} 页: {page_stats[page]} 个岗位")
            report_lines.append("")
            
            # 字段完成率
            report_lines.append("## ✅ 字段完成率")
            field_names = [
                "position_name", "work_location", "position_category", "publish_time",
                "department", "education_requirement", "work_experience",
                "job_responsibilities", "job_requirements", "other_info"
            ]
            
            field_labels = {
                "position_name": "岗位名称",
                "work_location": "工作地点",
                "position_category": "岗位类别",
                "publish_time": "发布时间",
                "department": "部门信息",
                "education_requirement": "学历要求",
                "work_experience": "工作经验",
                "job_responsibilities": "工作职责",
                "job_requirements": "任职要求",
                "other_info": "其他信息"
            }
            
            for field in field_names:
                completed = sum(1 for pos in positions if getattr(pos, field, ""))
                rate = (completed / len(positions)) * 100
                label = field_labels.get(field, field)
                bar = "█" * int(rate / 5) + "░" * (20 - int(rate / 5))
                report_lines.append(f"- {label}: {bar} {rate:.1f}% ({completed}/{len(positions)})")
            report_lines.append("")
            
            # 数据质量警告
            report_lines.append("## ⚠️ 数据质量警告")
            
            if empty_count > 0:
                report_lines.append(f"- 有 {empty_count} 个岗位数据为空或几乎为空")
            
            low_completion_fields = []
            for field in field_names:
                completed = sum(1 for pos in positions if getattr(pos, field, ""))
                rate = (completed / len(positions)) * 100
                if rate < 50:
                    low_completion_fields.append(field_labels.get(field, field))
            
            if low_completion_fields:
                report_lines.append(f"- 以下字段完成率低于50%: {', '.join(low_completion_fields)}")
            
            if not low_completion_fields and empty_count == 0:
                report_lines.append("- 所有字段完成率良好，无数据质量问题")
            report_lines.append("")
            
            # 文件信息
            report_lines.append("## 📁 文件信息")
            report_lines.append(f"- 输出目录: {self.output_dir}")
            report_lines.append(f"- 数据管理器版本: 1.0")
            report_lines.append(f"- 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_lines.append("")
            
            # 建议
            report_lines.append("## 💡 建议")
            if empty_count > 0:
                report_lines.append(f"1. 重新提取 {empty_count} 个空数据的岗位")
            
            if low_completion_fields:
                report_lines.append(f"2. 优化以下字段的提取逻辑: {', '.join(low_completion_fields)}")
            
            if complete_count / len(positions) < 0.8:
                report_lines.append("3. 整体数据完整性需要提升，建议检查提取流程")
            else:
                report_lines.append("3. 数据完整性良好，可以继续进行")
            
            report_lines.append("4. 定期备份数据到backups目录")
            report_lines.append("")
            
            report_lines.append("=" * 60)
            report_lines.append(f"报告结束 - {self.project_name}")
            report_lines.append("=" * 60)
            
            # 保存报告
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            print(f"📈 生成数据报告: {filename}")
            print(f"   📍 位置: {os.path.relpath(file_path, self.output_dir)}")
            
            return file_path
            
        except Exception as e:
            print(f"❌ 生成报告失败: {e}")
            raise DataError(f"生成报告失败: {e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """获取进度信息"""
        return {
            "initialized": self.initialized,
            "output_dir": self.output_dir,
            "position_count": self.position_count,
            "page_count": self.page_count,
            "last_save_time": self.last_save_time.isoformat() if self.last_save_time else None,
            "backup_count": self.backup_count,
            "directories": self.dirs,
            "timestamp": datetime.now().isoformat()
        }
    
    def backup_data(self, backup_dir: str = None) -> bool:
        """备份数据"""
        if not self.initialized:
            raise DataError("数据管理器未初始化")
        
        try:
            # 确定备份目录
            if backup_dir is None:
                backup_dir = os.path.join(self.output_dir, self.dirs["backups"])
            
            # 创建时间戳备份目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
            
            print(f"💾 创建数据备份: {backup_path}")
            
            # 复制重要目录
            dirs_to_backup = ["positions", "pages", "final", "reports"]
            
            for dir_name in dirs_to_backup:
                source_dir = os.path.join(self.output_dir, self.dirs[dir_name])
                target_dir = os.path.join(backup_path, dir_name)
                
                if os.path.exists(source_dir) and os.listdir(source_dir):
                    shutil.copytree(source_dir, target_dir)
                    print(f"  📁 备份目录: {dir_name} ({len(os.listdir(source_dir))} 个文件)")
            
            # 创建备份元数据
            metadata = {
                "backup_time": datetime.now().isoformat(),
                "source_dir": self.output_dir,
                "backup_dir": backup_path,
                "position_count": self.position_count,
                "page_count": self.page_count,
                "data_manager_version": "1.0",
                "directories_backed_up": dirs_to_backup
            }
            
            metadata_file = os.path.join(backup_path, "backup_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.backup_count += 1
            
            print(f"✅ 数据备份完成: {backup_path}")
            print(f"📊 备份元数据: {metadata_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据备份失败: {e}")
            return False
    
    def cleanup(self) -> None:
        """清理临时文件"""
        try:
            temp_dir = os.path.join(self.output_dir, self.dirs["temp"])
            
            if os.path.exists(temp_dir):
                # 删除超过1天的临时文件
                now = time.time()
                deleted_count = 0
                
                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    
                    # 检查文件年龄
                    if os.path.isfile(file_path):
                        file_age = now - os.path.getmtime(file_path)
                        
                        if file_age > 86400:  # 1天
                            os.remove(file_path)
                            deleted_count += 1
                
                if deleted_count > 0:
                    print(f"🧹 清理临时文件: {deleted_count} 个")
            
            print("✅ 数据管理器清理完成")
            
        except Exception as e:
            print(f"⚠️  清理临时文件失败: {e}")