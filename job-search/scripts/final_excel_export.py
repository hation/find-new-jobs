#!/usr/bin/env python3
"""
Job Search技能 - 最终版Excel导出工具（包含登录状态检查和修复）
解决boss命令路径和登录状态问题
"""

import os
import sys
import json
import csv
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

class BossCommandHelper:
    """boss命令辅助类，处理路径和登录状态问题"""
    
    @staticmethod
    def get_boss_path():
        """获取boss命令的完整路径"""
        # 已知的安装位置
        known_paths = [
            "/Users/xingan/Library/Python/3.12/bin/boss",  # 你的安装位置
            f"{Path.home()}/Library/Python/3.12/bin/boss",
            f"{Path.home()}/.local/bin/boss",
            "/usr/local/bin/boss",
            "/usr/bin/boss",
        ]
        
        for path in known_paths:
            if os.path.exists(path):
                return path
        
        # 尝试使用which命令查找
        try:
            result = subprocess.run(
                ["which", "boss"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def check_login_status(boss_path=None):
        """检查登录状态"""
        if not boss_path:
            boss_path = BossCommandHelper.get_boss_path()
        
        if not boss_path:
            return "boss_command_not_found", "boss命令未找到"
        
        try:
            result = subprocess.run(
                [boss_path, "status"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8'
            )
            
            output = result.stdout.lower()
            
            if "已登录" in output and "search=ok" in output:
                return "logged_in", "已登录，search=ok"
            elif "search=fail" in output:
                return "login_expired", "登录已过期，需要重新登录"
            elif "login" in output and "fail" in output:
                return "not_logged_in", "未登录"
            else:
                return "unknown", f"未知状态: {result.stdout[:200]}"
                
        except Exception as e:
            return "error", f"检查登录状态失败: {e}"
    
    @staticmethod
    def run_boss_command(args: List[str], timeout=30):
        """运行boss命令"""
        boss_path = BossCommandHelper.get_boss_path()
        
        if not boss_path:
            return subprocess.CompletedProcess(
                args=["boss"] + args,
                returncode=127,  # 命令未找到
                stdout="",
                stderr="boss命令未找到，请检查安装和PATH"
            )
        
        try:
            cmd = [boss_path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8'
            )
            return result
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=124,  # 超时
                stdout="",
                stderr="命令执行超时"
            )
        except Exception as e:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=f"执行异常: {e}"
            )

class ExcelExporterFinal:
    """最终版Excel导出器，包含完整的错误处理"""
    
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
        ('岗位描述', 'jobDescription', '岗位详细描述'),
        ('技能要求', 'skills', '岗位技能要求'),
        ('福利待遇', 'welfareList', '公司福利'),
        ('岗位类型', 'jobTypeDesc', '岗位类型'),
        ('搜索关键词', 'search_keyword', '搜索关键词'),
        ('来源页数', 'search_page', '搜索结果页码'),
        ('数据时间', 'data_time', '数据获取时间'),
        ('岗位ID', 'encryptJobId', '岗位唯一ID'),
        ('公司ID', 'encryptBrandId', '公司唯一ID'),
        ('岗位链接', 'jobLink', '岗位详情链接'),
    ]
    
    def __init__(self, output_dir=None, include_description=True):
        self.output_dir = Path(output_dir) if output_dir else self._create_output_dir()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.include_description = include_description
        
        # 检查boss命令和登录状态
        self._check_environment()
    
    def _create_output_dir(self):
        """创建输出目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Path.home() / "招聘数据" / f"Excel导出_最终版_{timestamp}"
    
    def _check_environment(self):
        """检查运行环境"""
        print("🔍 检查运行环境...")
        
        # 检查boss命令
        boss_path = BossCommandHelper.get_boss_path()
        if not boss_path:
            print("❌ boss命令未找到")
            print("💡 解决方案:")
            print("  1. 安装boss-cli: python3 -m pip install --user git+https://github.com/zouzhifeng/boss-cli.git")
            print("  2. 或使用完整路径: /Users/xingan/Library/Python/3.12/bin/boss")
            return False
        
        print(f"✅ boss命令: {boss_path}")
        
        # 检查登录状态
        status, message = BossCommandHelper.check_login_status(boss_path)
        print(f"🔑 登录状态: {message}")
        
        if status == "logged_in":
            print("✅ 登录状态正常")
            return True
        elif status == "login_expired":
            print("⚠️  登录已过期")
            print("💡 重新登录流程:")
            print("  1. boss logout")
            print("  2. 在浏览器中登录 https://www.zhipin.com")
            print("  3. boss login --cookie-source chrome")
            return False
        elif status == "boss_command_not_found":
            print("❌ boss命令未找到")
            return False
        else:
            print(f"⚠️  登录状态未知: {message}")
            return False
    
    def fetch_job_description_safe(self, job_id: str, security_id: str = None) -> str:
        """安全地获取岗位描述（包含错误处理）"""
        if not job_id:
            return "缺少岗位ID"
        
        # 检查是否有security_id
        if not security_id:
            return "缺少securityId，无法获取详细描述"
        
        print(f"  🔍 获取描述: {job_id[:20]}...")
        
        # 构建命令
        args = ["detail", security_id]
        
        # 执行命令
        result = BossCommandHelper.run_boss_command(args, timeout=30)
        
        if result.returncode == 0:
            # 尝试从输出中提取描述
            description = self._extract_description_smart(result.stdout)
            if description:
                print(f"    ✅ 获取成功 ({len(description)} 字符)")
                return description
            else:
                print(f"    ⚠️  获取成功但未找到描述")
                return "已获取详情但未找到描述文本"
        else:
            error_msg = result.stderr[:100] if result.stderr else "未知错误"
            print(f"    ❌ 获取失败: {error_msg}")
            
            # 特殊错误处理
            if "环境异常" in error_msg or "__zp_stoken__" in error_msg:
                return "登录过期，需要重新登录"
            elif "未登录" in error_msg:
                return "未登录，请先登录"
            elif "超时" in error_msg:
                return "请求超时，请重试"
            else:
                return f"获取失败: {error_msg}"
    
    def _extract_description_smart(self, text: str) -> str:
        """智能提取岗位描述"""
        if not text:
            return ""
        
        # 尝试解析YAML/JSON
        try:
            import yaml
            data = yaml.safe_load(text)
            
            # 递归查找描述字段
            def find_desc(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        key_str = str(key).lower()
                        if any(kw in key_str for kw in ['description', 'desc', '描述', '职责', '要求']):
                            if isinstance(value, str) and value.strip():
                                return value.strip()
                        
                        # 递归查找
                        if isinstance(value, (dict, list)):
                            result = find_desc(value, f"{path}.{key}")
                            if result:
                                return result
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            result = find_desc(item, f"{path}[{i}]")
                            if result:
                                return result
                
                return None
            
            description = find_desc(data)
            if description:
                return description
        except:
            pass
        
        # 从文本中提取
        lines = text.split('\n')
        description_lines = []
        in_description = False
        
        for line in lines:
            line = line.strip()
            
            # 检测描述开始
            if any(keyword in line for keyword in ['岗位描述', '职位描述', '工作职责', '岗位职责', 'description:']):
                in_description = True
                continue
            
            # 检测描述结束
            if in_description:
                if (line.startswith('  ') or  # YAML缩进结束
                    any(keyword in line.lower() for keyword in ['任职要求', '薪资福利', '公司介绍', '联系方式', '---', '...'])):
                    break
                
                if line and not line.startswith('#'):  # 非注释行
                    description_lines.append(line)
        
        if description_lines:
            return '\n'.join(description_lines)
        
        # 返回大段文本
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            return paragraphs[0][:1000]  # 限制长度
        
        return ""
    
    def export_jobs_final(self, jobs_data: List[Dict], 
                         max_descriptions: int = 30,
                         skip_on_error: bool = True) -> List[str]:
        """最终版导出功能"""
        print("🚀 开始导出Excel数据（最终版）")
        print("=" * 60)
        
        if not jobs_data:
            print("❌ 没有数据可导出")
            return []
        
        print(f"📊 总岗位数: {len(jobs_data)} 个")
        print(f"📝 包含岗位描述: {'是' if self.include_description else '否'}")
        print(f"🔢 最多获取描述: {max_descriptions} 个")
        
        # 预处理数据
        processed_jobs = []
        for i, job in enumerate(jobs_data):
            processed_job = job.copy()
            
            # 确保有必要的字段
            processed_job.setdefault('jobName', f'未知岗位_{i+1}')
            processed_job.setdefault('brandName', '未知公司')
            processed_job.setdefault('salaryDesc', '面议')
            processed_job.setdefault('jobExperience', '经验不限')
            processed_job.setdefault('jobDegree', '学历不限')
            processed_job.setdefault('areaDistrict', '未知地区')
            
            processed_jobs.append(processed_job)
        
        # 获取岗位描述
        if self.include_description:
            print(f"\n🔍 获取岗位描述...")
            
            jobs_to_fetch = min(len(processed_jobs), max_descriptions)
            fetched_count = 0
            
            for i in range(jobs_to_fetch):
                job = processed_jobs[i]
                job_id = job.get('encryptJobId')
                security_id = job.get('securityId')
                
                if job_id and security_id:
                    description = self.fetch_job_description_safe(job_id, security_id)
                    job['jobDescription'] = description
                    
                    if description and "获取失败" not in description and "登录过期" not in description:
                        fetched_count += 1
                    
                    # 延迟避免请求过快
                    if i < jobs_to_fetch - 1:
                        time.sleep(1.5)
                else:
                    missing = []
                    if not job_id:
                        missing.append("岗位ID")
                    if not security_id:
                        missing.append("securityId")
                    job['jobDescription'] = f"缺少{', '.join(missing)}"
                    print(f"  ❌ 缺少必要字段: {', '.join(missing)}")
            
            print(f"✅ 描述获取完成: {fetched_count}/{jobs_to_fetch} 个成功")
        
        # 导出到CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"岗位数据_最终版_{timestamp}.csv"
        csv_path = self.output_dir / csv_filename
        
        print(f"\n💾 导出到CSV: {csv_path}")
        self._export_to_csv_final(processed_jobs, csv_path)
        
        # 生成报告
        output_files = [str(csv_path)]
        
        stats_file = self._generate_final_report(processed_jobs, csv_path, fetched_count if self.include_description else 0)
        output_files.append(stats_file)
        
        print(f"\n🎉 导出完成！")
        print(f"📁 输出目录: {self.output_dir}")
        print(f"📋 生成文件: {len(output_files)} 个")
        
        return output_files
    
    def _export_to_csv_final(self, jobs_data: List[Dict], csv_path: Path):
        """导出到CSV（最终版）"""
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
                    elif field_key == 'jobLink':
                        job_id = job.get('encryptJobId')
                        value = f"https://www.zhipin.com/job_detail/{job_id}.html" if job_id else ""
                    elif field_key in ['skills', 'welfareList']:
                        field_data = job.get(field_key, [])
                        if isinstance(field_data, list):
                            value = '、'.join(field_data[:5])
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
                        elif field_key != 'jobDescription' and len(value) > 200:
                            value = value[:197] + '...'
                    
                    row.append(value)
                
                writer.writerow(row)
        
        print(f"✅ CSV导出完成: {len(jobs_data)} 行数据")
    
    def _generate_final_report(self, jobs_data: List[Dict], csv_path: Path, fetched_desc_count: int = 0) -> str:
        """生成最终报告"""
        report_file = csv_path.with_suffix('.最终报告.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# 岗位数据导出最终报告\n\n")
            f.write("## 导出摘要\n")
            f.write(f"- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"- **总岗位数**: {len(jobs_data)} 个\n")
            f.write(f"- **包含岗位描述**: {'是' if self.include_description else '否'}\n")
            
            if self.include_description:
                f.write(f"- **成功获取描述**: {fetched_desc_count} 个\n")
                if fetched_desc_count > 0:
                    success_rate = fetched_desc_count / min(len(jobs_data), 30) * 100
                    f.write(f"- **描述获取成功率**: {success_rate:.1f}%\n")
            
            f.write(f"- **数据文件**: {csv_path.name}\n")
            f.write(f"- **输出目录**: {self.output_dir}\n\n")
            
            f.write("## 数据质量分析\n")
            
            # 统计字段完整性
            required_fields = ['jobName', 'brandName', 'salaryDesc', 'encryptJobId']
            field_stats = {}
            
            for field in required_fields:
                count = sum(1 for job in jobs_data if job.get(field))
                field_stats[field] = count
            
            f.write("### 字段完整性\n")
            f.write("| 字段名 | 有数据的岗位数 | 完整率 |\n")
            f.write("|--------|----------------|--------|\n")
            
            for field, count in field_stats.items():
                percentage = count / len(jobs_data) * 100
                field_name_map = {
                    'jobName': '岗位名称',
                    'brandName': '公司名称',
                    'salaryDesc': '薪资',
                    'encryptJobId': '岗位ID'
                }
                f.write(f"| {field_name_map.get(field, field)} | {count} | {percentage:.1f}% |\n")
            
            f.write("\n## 薪资分布\n")
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
            
            f.write("\n## 常见问题解决方案\n")
            f.write("### 问题1: 无法获取岗位描述\n")
            f.write("**可能原因**:\n")
            f.write("1. 登录状态过期 (`__zp_stoken__` cookie失效)\n")
            f.write("2. 缺少securityId字段\n")
            f.write("3. boss命令路径问题\n\n")
            
            f.write("**解决方案**:\n")
            f.write("```bash\n")
            f.write("# 1. 登出\n")
            f.write("boss logout\n\n")
            f.write("# 2. 在浏览器中登录BOSS直聘\n")
            f.write("# 访问 https://www.zhipin.com 并登录\n\n")
            f.write("# 3. 通过浏览器获取cookie\n")
            f.write("boss login --cookie-source chrome\n\n")
            f.write("# 4. 验证登录状态\n")
            f.write("boss status  # 应该显示'已登录'和'search=ok'\n")
            f.write("```\n\n")
            
            f.write("### 问题2: boss命令找不到\n")
            f.write("**解决方案**:\n")
            f.write("```bash\n")
            f.write("# 使用完整路径\n")
            f.write("/Users/xingan/Library/Python/3.12/bin/boss --version\n\n")
            f.write("# 或添加到PATH\n")
            f.write("export PATH=\"/Users/xingan/Library/Python/3.12/bin:$PATH\"\n")
            f.write("```\n\n")
            
            f.write("## Excel使用指南\n")
            f.write("1. **打开文件**: 双击CSV文件或用Excel打开\n")
            f.write("2. **查看描述**: 调整'岗位描述'列宽，或设置自动换行\n")
            f.write("3. **数据筛选**: 选中表头行 → 数据 → 筛选\n")
            f.write("4. **保存格式**: 文件 → 另存为 → 选择.xlsx格式\n")
        
        print(f"✅ 最终报告已生成: {report_file}")
        return str(report_file)


# 命令行接口
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='最终版Excel导出工具（解决所有已知问题）')
    
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件路径')
    parser.add_argument('--output-dir', '-o', help='输出目录')
    parser.add_argument('--no-description', action='store_true', help='不获取岗位描述')
    parser.add_argument('--max-desc', type=int, default=30, help='最多获取描述的岗位数（默认30）')
    
    args = parser.parse_args()
    
    print("🚀 最终版Excel导出工具")
    print("=" * 60)
    
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
    exporter = ExcelExporterFinal(
        output_dir=args.output_dir,
        include_description=not args.no_description
    )
    
    # 导出数据
    try:
        output_files = exporter.export_jobs_final(
            jobs_data,
            max_descriptions=args.max_desc,
            skip_on_error=True
        )
        
        if output_files:
            print(f"\n💡 立即用Excel打开:")
            print(f"  open \"{output_files[0]}\"")
            
            print(f"\n📋 生成的文件:")
            for file in output_files:
                print(f"  • {os.path.basename(file)}")
        
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()