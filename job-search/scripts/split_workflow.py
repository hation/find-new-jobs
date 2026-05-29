#!/usr/bin/env python3
"""
方案B：分步工作流完整实现
将搜索和详情获取分离，避免token过期影响
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class SplitWorkflow:
    """分步工作流工具"""
    
    def __init__(self, output_base=None):
        """初始化工具"""
        self.setup_environment()
        
        if output_base:
            self.output_base = Path(output_base)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_base = Path.home() / "招聘数据" / f"分步采集_{timestamp}"
        
        self.output_base.mkdir(parents=True, exist_ok=True)
        
        # 导入扩展导出器
        skill_dir = Path(__file__).parent
        sys.path.insert(0, str(skill_dir))
        
        try:
            from extended_excel_exporter import ExtendedExcelExporter
            self.Exporter = ExtendedExcelExporter
            print("✅ 扩展导出器加载成功")
        except ImportError as e:
            print(f"⚠️  扩展导出器加载失败: {e}")
            self.Exporter = None
    
    def setup_environment(self):
        """设置环境变量"""
        boss_path = "/Users/xingan/Library/Python/3.12/bin"
        if boss_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{boss_path}:{os.environ.get('PATH', '')}"
    
    def run_boss_command(self, cmd_args, timeout=30, retries=1):
        """运行boss命令"""
        cmd = ["boss"] + cmd_args
        
        for attempt in range(retries + 1):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    error_msg = result.stderr or "未知错误"
                    
                    if "环境异常" in error_msg or "__zp_stoken__" in error_msg:
                        print(f"    ⚠️  Token过期 (尝试 {attempt+1}/{retries+1})")
                        if attempt < retries:
                            print(f"    ⏳ 等待2秒后重试...")
                            time.sleep(2)
                            continue
                    
                    return False, error_msg
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏱️  命令超时 (尝试 {attempt+1}/{retries+1})")
                if attempt < retries:
                    print(f"    ⏳ 等待2秒后重试...")
                    time.sleep(2)
                continue
            except Exception as e:
                return False, str(e)
        
        return False, "所有重试都失败"
    
    def login_and_check(self):
        """登录并检查状态"""
        print("🔑 执行登录...")
        
        # 尝试从浏览器获取cookie
        login_success, login_result = self.run_boss_command(
            ["login", "--cookie-source", "chrome"],
            timeout=60,
            retries=0
        )
        
        if login_success:
            print("✅ 登录成功")
            
            # 检查登录状态
            status_success, status_result = self.run_boss_command(["status"], timeout=10)
            
            if status_success and "search=ok" in status_result:
                print("✅ 登录状态正常 (search=ok)")
                return True
            else:
                print("⚠️  登录成功但状态异常")
                if status_result:
                    print(f"状态输出: {status_result[:100]}")
                return False
        else:
            print(f"❌ 登录失败: {login_result[:100]}")
            print("💡 请确保已在Chrome浏览器中登录BOSS直聘")
            return False
    
    def step1_search_only(self, keyword, city, pages=1, max_jobs_per_page=15):
        """
        步骤1：只搜索，不获取详情
        
        Returns:
            (success, security_ids_dict)
        """
        print(f"\n📋 步骤1：搜索职位（不获取详情）")
        print(f"🔍 搜索: {keyword} - {city}")
        
        all_security_ids = {}
        search_data_files = []
        
        for page in range(1, pages + 1):
            print(f"\n📄 搜索第 {page}/{pages} 页")
            
            # 搜索职位
            search_cmd = [
                "search", keyword,
                "--city", city,
                "--page", str(page),
                "--json"
            ]
            
            success, result = self.run_boss_command(search_cmd, timeout=30, retries=0)
            
            if not success:
                print(f"❌ 第{page}页搜索失败: {result[:50]}")
                continue
            
            try:
                data = json.loads(result)
                
                if data.get('ok'):
                    jobs = data.get('data', {}).get('jobList', [])
                    
                    if jobs:
                        print(f"✅ 找到 {len(jobs)} 个职位")
                        
                        # 保存搜索数据
                        search_file = self.output_base / f"搜索数据_第{page}页.json"
                        with open(search_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        search_data_files.append(search_file)
                        
                        # 提取securityId
                        page_security_ids = {}
                        for i, job in enumerate(jobs[:max_jobs_per_page], 1):
                            job_name = job.get('jobName', f'职位{i}')[:30]
                            security_id = job.get('securityId', '')
                            
                            if security_id:
                                page_security_ids[job_name] = security_id
                                print(f"  [{i}] {job_name}: {security_id[:20]}...")
                        
                        if page_security_ids:
                            all_security_ids[f"第{page}页"] = page_security_ids
                            print(f"✅ 第{page}页提取到 {len(page_security_ids)} 个securityId")
                    else:
                        print(f"⚠️  第{page}页搜索成功但没有找到职位")
                else:
                    error_msg = data.get('error', {}).get('message', '未知错误')
                    print(f"❌ 第{page}页搜索数据异常: {error_msg}")
                    
            except json.JSONDecodeError as e:
                print(f"❌ 第{page}页JSON解析失败: {e}")
                continue
        
        if not all_security_ids:
            print("❌ 没有提取到任何securityId")
            return False, None
        
        # 保存所有securityId
        total_ids = sum(len(ids) for ids in all_security_ids.values())
        print(f"\n📊 步骤1完成")
        print(f"✅ 总计提取: {total_ids} 个securityId")
        print(f"📁 搜索数据文件: {len(search_data_files)} 个")
        
        # 保存securityId到文件
        security_file = self.output_base / "security_ids.json"
        with open(security_file, 'w', encoding='utf-8') as f:
            json.dump(all_security_ids, f, ensure_ascii=False, indent=2)
        
        print(f"📁 securityId文件: {security_file}")
        
        return True, all_security_ids
    
    def step2_details_only(self, security_ids_dict, max_details=None, delay=1):
        """
        步骤2：只获取详情，不搜索
        """
        if not security_ids_dict:
            print("❌ 没有securityId数据")
            return []
        
        # 提取所有securityId
        all_security_ids = []
        for page_name, jobs in security_ids_dict.items():
            for job_name, security_id in jobs.items():
                all_security_ids.append((job_name, security_id, page_name))
        
        print(f"\n📋 步骤2：获取职位详情")
        print(f"📊 准备获取 {len(all_security_ids)} 个职位详情")
        
        # 限制数量
        if max_details and len(all_security_ids) > max_details:
            all_security_ids = all_security_ids[:max_details]
            print(f"📊 限制为前 {len(all_security_ids)} 个职位")
        
        print(f"⏳ 预计时间: {len(all_security_ids) * (delay + 2)} 秒")
        
        details = []
        failed_jobs = []
        
        for i, (job_name, security_id, page_name) in enumerate(all_security_ids, 1):
            print(f"\n  [{i}/{len(all_security_ids)}] {job_name}")
            print(f"     来源: {page_name}")
            print(f"     securityId: {security_id[:30]}...")
            
            # 获取详情
            detail_cmd = ["detail", security_id, "--json"]
            success, result = self.run_boss_command(detail_cmd, timeout=30, retries=1)
            
            if success:
                try:
                    data = json.loads(result)
                    
                    if data.get('ok'):
                        details.append(data)
                        print(f"      ✅ 获取成功")
                        
                        # 保存单个详情文件
                        detail_file = self.output_base / f"职位详情_{i}.json"
                        with open(detail_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        error_msg = data.get('error', {}).get('message', '数据异常')
                        print(f"      ❌ {error_msg}")
                        failed_jobs.append((job_name, error_msg))
                        
                except json.JSONDecodeError:
                    print(f"      ❌ JSON解析失败")
                    failed_jobs.append((job_name, "JSON解析失败"))
            else:
                print(f"      ❌ 获取失败: {result[:50]}")
                failed_jobs.append((job_name, result[:50]))
            
            # 延迟
            if i < len(all_security_ids) and delay > 0:
                time.sleep(delay)
        
        # 统计结果
        print(f"\n📊 步骤2完成:")
        print(f"  ✅ 成功: {len(details)} 个")
        print(f"  ❌ 失败: {len(failed_jobs)} 个")
        
        if failed_jobs:
            print(f"  📝 失败详情（前5个）:")
            for job_name, error in failed_jobs[:5]:
                print(f"     {job_name}: {error}")
            if len(failed_jobs) > 5:
                print(f"    ... 还有 {len(failed_jobs)-5} 个失败")
        
        return details
    
    def export_details(self, details, keyword, city, pages):
        """导出详情数据"""
        if not details:
            print("❌ 没有详情数据可导出")
            return None
        
        if not self.Exporter:
            print("❌ 导出器不可用")
            return None
        
        print(f"\n💾 导出 {len(details)} 个职位数据到Excel...")
        
        # 创建导出器
        export_dir = self.output_base / "Excel导出"
        exporter = self.Exporter(str(export_dir))
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{city}_{keyword}_岗位_分步采集_{timestamp}.csv"
        
        try:
            output_files = exporter.export_detail_data(
                details,
                search_keyword=keyword,
                search_page=pages,
                filename=filename,
                include_stats=True
            )
            
            if output_files:
                # 保存原始数据
                raw_file = export_dir / f"原始数据_{timestamp}.json"
                with open(raw_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'keyword': keyword,
                        'city': city,
                        'pages': pages,
                        'total_jobs': len(details),
                        'export_time': timestamp,
                        'details': details
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"\n🎉 导出成功!")
                print(f"📊 职位数量: {len(details)} 个")
                print(f"📁 主文件: {output_files[0]}")
                print(f"📁 原始数据: {raw_file}")
                print(f"📁 输出目录: {export_dir}")
                
                return {
                    'export_dir': str(export_dir),
                    'main_file': output_files[0],
                    'raw_file': str(raw_file),
                    'total_jobs': len(details)
                }
            else:
                print("❌ 导出失败（无输出文件）")
                return None
                
        except Exception as e:
            print(f"❌ 导出异常: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_split_workflow(self, keyword="AI", city="深圳", pages=1, 
                          max_jobs_per_page=10, max_details=None, delay=1):
        """
        运行完整的分步工作流
        
        Args:
            keyword: 搜索关键词
            city: 城市
            pages: 搜索页数
            max_jobs_per_page: 每页最多提取职位数
            max_details: 最多获取详情数
            delay: 详情获取延迟（秒）
        """
        print("🚀 分步工作流启动")
        print("=" * 60)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 搜索配置: {keyword} - {city} (共{pages}页)")
        print(f"📊 每页限制: {max_jobs_per_page} 个职位")
        print("=" * 60)
        
        # ===== 步骤1：搜索并提取securityId =====
        print("\n" + "=" * 30)
        print("📋 步骤1：登录 → 搜索 → 提取securityId")
        print("=" * 30)
        
        # 登录
        if not self.login_and_check():
            print("❌ 步骤1登录失败，停止工作流")
            return False
        
        # 搜索并提取securityId
        step1_success, security_ids = self.step1_search_only(
            keyword, city, pages, max_jobs_per_page
        )
        
        if not step1_success:
            print("❌ 步骤1失败，停止工作流")
            return False
        
        # 计算总securityId数量
        total_ids = sum(len(ids) for ids in security_ids.values())
        print(f"\n✅ 步骤1完成")
        print(f"📊 提取到 {total_ids} 个securityId")
        print(f"📁 数据保存在: {self.output_base}")
        
        # 提示用户
        print(f"\n💡 请等待片刻，然后准备步骤2...")
        print(f"   1. 确保仍在浏览器中登录BOSS直聘")
        print(f"   2. 保持浏览器打开")
        print(f"   3. 准备好后按Enter继续")
        
        try:
            input("\n⏳ 按Enter键开始步骤2...")
        except KeyboardInterrupt:
            print("\n⏹️  用户中断，停止工作流")
            return False
        
        # ===== 步骤2：重新登录并获取详情 =====
        print("\n" + "=" * 30)
        print("📋 步骤2：重新登录 → 批量获取详情")
        print("=" * 30)
        
        # 重新登录
        print("🔄 重新登录...")
        if not self.login_and_check():
            print("❌ 步骤2登录失败")
            # 可以尝试继续，但成功率可能降低
        
        # 获取详情
        details = self.step2_details_only(security_ids, max_details, delay)
        
        if not details:
            print("❌ 步骤2没有获取到任何详情")
            return False
        
        print(f"\n✅ 步骤2完成")
        print(f"📊 获取到 {len(details)} 个职位详情")
        
        # ===== 步骤3：导出数据 =====
        print("\n" + "=" * 30)
        print("📋 步骤3：导出Excel数据")
        print("=" * 30)
        
        export_result = self.export_details(details, keyword, city, pages)
        
        if not export_result:
            print("❌ 步骤3导出失败")
            return False
        
        # ===== 生成工作报告 =====
        report_file = self.generate_workflow_report(
            keyword, city, pages, max_jobs_per_page, 
            total_ids, len(details), export_result
        )
        
        print(f"\n{'=' * 60}")
        print("🎉 分步工作流执行成功！")
        print(f"📊 采集统计:")
        print(f"  - 搜索关键词: {keyword}")
        print(f"  - 目标城市: {city}")
        print(f"  - 处理页数: {pages}")
        print(f"  - 提取securityId: {total_ids} 个")
        print(f"  - 获取详情: {len(details)} 个职位")
        print(f"  - 成功率: {len(details)/total_ids*100:.1f}%")
        print(f"  - 输出文件: {export_result['main_file']}")
        print(f"  - 输出目录: {export_result['export_dir']}")
        print(f"📄 工作报告: {report_file}")
        
        return True
    
    def generate_workflow_report(self, keyword, city, pages, max_jobs, 
                                total_ids, total_details, export_result):
        """生成工作报告"""
        report_file = self.output_base / "分步工作流报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 分步工作流采集报告\n\n")
            f.write(f"**采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**工作流类型**: 方案B（分步工作流）\n\n")
            
            f.write(f"## 📊 采集统计\n\n")
            f.write(f"| 项目 | 数据 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 搜索关键词 | {keyword} |\n")
            f.write(f"| 目标城市 | {city} |\n")
            f.write(f"| 处理页数 | {pages} 页 |\n")
            f.write(f"| 每页限制 | {max_jobs} 个职位 |\n")
            f.write(f"| 提取securityId | {total_ids} 个 |\n")
            f.write(f"| 获取详情 | {total_details} 个职位 |\n")
            f.write(f"| 成功率 | {total_details/total_ids*100:.1f}% |\n")
            f.write(f"| 输出文件 | {Path(export_result['main_file']).name} |\n")
            f.write(f"| 输出目录 | {export_result['export_dir']} |\n\n")
            
            f.write(f"## 🚀 分步工作流优势\n\n")
            f.write(f"1. **避免token过期**：搜索和详情获取分离，互不影响\n")
            f.write(f"2. **提高成功率**：每个步骤专注单一任务，减少干扰\n")
            f.write(f"3. **灵活性强**：可以分多次完成大批量数据采集\n")
            f.write(f"4. **便于调试**：每个步骤的输出都独立保存\n\n")
            
            f.write(f"## 📁 文件结构\n\n")
            f.write(f"```\n")
            f.write(f"{self.output_base}/\n")
            
            # 列出文件
            for item in sorted(self.output_base.rglob("*")):
                if item.is_file():
                    rel_path = item.relative_to(self.output_base)
                    size = item.stat().st_size
                    f.write(f"├── {rel_path} ({size:,} bytes)\n")
            
            f.write(f"```\n\n")
            
            f.write(f"## 🔄 再次运行\n")
            f.write(f"```bash\n")
            f.write(f"# 使用相同的参数\n")
            f.write(f"python3 {Path(__file__).name} \\\n")
            f.write(f"    --keyword {keyword} \\\n")
            f.write(f"    --city {city} \\\n")
            f.write(f"    --pages {pages} \\\n")
            f.write(f"    --max-jobs {max_jobs}\n")
            f.write(f"```\n\n")
            
            f.write(f"## 💡 使用建议\n")
            f.write(f"1. **分步执行**：大数据集时，可以分多次完成\n")
            f.write(f"2. **合理设置数量**：每页10-15个职位，每次处理20-30个详情\n")
            f.write(f"3. **注意时间**：步骤2需要在重新登录后立即执行\n")
            f.write(f"4. **数据备份**：securityId文件可以长期保存，随时重新获取详情\n")
        
        return str(report_file)


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='分步工作流工具 - 方案B实现')
    parser.add_argument('--keyword', default='AI', help='搜索关键词')
    parser.add_argument('--city', default='深圳', help='城市')
    parser.add_argument('--pages', type=int, default=1, help='搜索页数')
    parser.add_argument('--max-jobs', type=int, default=10, help='每页最多提取职位数')
    parser.add_argument('--max-details', type=int, help='最多获取详情数（默认不限）')
    parser.add_argument('--delay', type=int, default=1, help='详情获取延迟（秒）')
    parser.add_argument('--output-dir', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = SplitWorkflow(args.output_dir)
    
    # 运行分步工作流
    success = tool.run_split_workflow(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages,
        max_jobs_per_page=args.max_jobs,
        max_details=args.max_details,
        delay=args.delay
    )
    
    if success:
        print(f"\n✅ 分步工作流执行成功!")
        print(f"📅 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0)
    else:
        print(f"\n❌ 分步工作流执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()