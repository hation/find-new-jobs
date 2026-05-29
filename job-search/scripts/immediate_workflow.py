#!/usr/bin/env python3
"""
即时工作流工具 - 策略A实现
登录后立即执行完整的数据采集工作流
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class ImmediateWorkflow:
    """即时工作流工具"""
    
    def __init__(self, output_base=None):
        """初始化工具"""
        self.setup_environment()
        
        if output_base:
            self.output_base = Path(output_base)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_base = Path.home() / "招聘数据" / f"即时采集_{timestamp}"
        
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
    
    def run_with_timeout(self, cmd_args, timeout=25, retries=1):
        """
        运行命令，带超时和重试机制
        
        Args:
            cmd_args: 命令参数列表
            timeout: 超时时间（秒）
            retries: 重试次数
        
        Returns:
            (success, result_or_error)
        """
        cmd = ["boss"] + cmd_args
        
        for attempt in range(retries + 1):
            try:
                print(f"  ⚡ 执行命令: boss {' '.join(cmd_args)}")
                
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
                        print(f"    ❌ Token过期 (尝试 {attempt+1}/{retries+1})")
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
    
    def check_and_prepare(self):
        """检查并准备工作环境"""
        print("🔍 检查工作环境...")
        
        # 检查boss命令是否存在
        boss_cmd = ["status"]
        success, result = self.run_with_timeout(boss_cmd, timeout=10)
        
        if not success:
            print("❌ boss命令不可用")
            print("💡 请确保: boss-cli已安装且PATH设置正确")
            return False
        
        print("✅ boss命令可用")
        return True
    
    def execute_search(self, keyword, city, page=1, max_results=15):
        """执行搜索并获取职位列表"""
        print(f"\n🔍 搜索职位: {keyword} - {city} (第{page}页)")
        
        search_cmd = [
            "search", keyword,
            "--city", city,
            "--page", str(page),
            "--json"
        ]
        
        success, result = self.run_with_timeout(search_cmd, timeout=30, retries=0)
        
        if not success:
            print(f"❌ 搜索失败: {result}")
            return None
        
        try:
            data = json.loads(result)
            
            if data.get('ok'):
                jobs = data.get('data', {}).get('jobList', [])
                
                if jobs:
                    print(f"✅ 搜索成功: 找到 {len(jobs)} 个职位")
                    
                    # 保存搜索数据
                    search_file = self.output_base / f"搜索数据_第{page}页.json"
                    with open(search_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    print(f"📁 搜索数据已保存: {search_file}")
                    
                    # 限制返回数量
                    if max_results and len(jobs) > max_results:
                        jobs = jobs[:max_results]
                        print(f"📊 限制为前 {len(jobs)} 个职位")
                    
                    return jobs
                else:
                    print("❌ 搜索成功但没有找到职位")
                    return []
            else:
                error_msg = data.get('error', {}).get('message', '未知错误')
                print(f"❌ 搜索数据异常: {error_msg}")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
    
    def fetch_job_details(self, jobs, max_details=None, delay=1):
        """获取职位详情"""
        if not jobs:
            print("❌ 没有职位数据")
            return []
        
        total = len(jobs)
        if max_details and total > max_details:
            jobs = jobs[:max_details]
            print(f"📊 限制为前 {len(jobs)} 个职位详情")
        
        print(f"\n🚀 开始获取 {len(jobs)} 个职位详情")
        print("⏳ 预计时间: {}秒".format(len(jobs) * (delay + 2)))
        
        details = []
        failed_jobs = []
        
        for i, job in enumerate(jobs, 1):
            job_name = job.get('jobName', f'职位{i}')[:40]
            security_id = job.get('securityId', '')
            
            print(f"  [{i:2d}/{len(jobs)}] {job_name}")
            
            if not security_id:
                print(f"      ❌ 缺少securityId")
                failed_jobs.append((i, "缺少securityId"))
                continue
            
            # 获取详情
            detail_cmd = ["detail", security_id, "--json"]
            success, result = self.run_with_timeout(detail_cmd, timeout=30, retries=1)
            
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
                        failed_jobs.append((i, error_msg))
                        
                except json.JSONDecodeError:
                    print(f"      ❌ JSON解析失败")
                    failed_jobs.append((i, "JSON解析失败"))
            else:
                print(f"      ❌ 获取失败: {result[:50]}")
                failed_jobs.append((i, result[:50]))
            
            # 延迟，避免请求过快
            if i < len(jobs) and delay > 0:
                time.sleep(delay)
        
        # 统计结果
        print(f"\n📊 详情获取完成:")
        print(f"  ✅ 成功: {len(details)} 个")
        print(f"  ❌ 失败: {len(failed_jobs)} 个")
        
        if failed_jobs:
            print(f"  📝 失败详情:")
            for job_index, error in failed_jobs[:5]:  # 只显示前5个
                print(f"    职位 {job_index}: {error}")
            if len(failed_jobs) > 5:
                print(f"    ... 还有 {len(failed_jobs)-5} 个失败")
        
        return details
    
    def export_to_excel(self, details, keyword, city, page):
        """导出到Excel"""
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
        filename = f"{city}_{keyword}_岗位_即时采集_{timestamp}.csv"
        
        try:
            output_files = exporter.export_detail_data(
                details,
                search_keyword=keyword,
                search_page=page,
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
                        'page': page,
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
    
    def run_immediate_workflow(self, keyword="AI", city="深圳", pages=1, 
                              max_details_per_page=10, delay_between_pages=2):
        """
        运行即时工作流
        
        Args:
            keyword: 搜索关键词
            city: 城市
            pages: 搜索页数
            max_details_per_page: 每页最多获取详情数
            delay_between_pages: 页间延迟（秒）
        """
        print("🚀 即时工作流启动")
        print("=" * 60)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 搜索配置: {keyword} - {city} (共{pages}页)")
        print(f"📊 详情限制: 每页最多 {max_details_per_page} 个")
        print("=" * 60)
        
        # 1. 检查环境
        if not self.check_and_prepare():
            print("❌ 环境检查失败，停止工作流")
            return False
        
        all_details = []
        
        # 2. 处理每个页面
        for page in range(1, pages + 1):
            print(f"\n📄 处理第 {page}/{pages} 页")
            
            # 搜索职位
            jobs = self.execute_search(keyword, city, page, max_details_per_page)
            
            if not jobs:
                print(f"⚠️  第{page}页没有找到职位，跳过")
                continue
            
            # 获取职位详情
            page_details = self.fetch_job_details(jobs, max_details_per_page, delay=1)
            
            if page_details:
                all_details.extend(page_details)
                print(f"✅ 第{page}页完成: 获取 {len(page_details)} 个职位详情")
            else:
                print(f"⚠️  第{page}页没有获取到任何详情")
            
            # 页间延迟
            if page < pages and len(page_details) > 0:
                print(f"⏳ 等待{delay_between_pages}秒后处理下一页...")
                time.sleep(delay_between_pages)
        
        if not all_details:
            print("\n❌ 没有获取到任何职位详情")
            return False
        
        print(f"\n✅ 所有页面处理完成")
        print(f"📊 总计获取: {len(all_details)} 个职位详情")
        
        # 3. 导出到Excel
        export_result = self.export_to_excel(all_details, keyword, city, pages)
        
        if export_result:
            # 4. 生成工作报告
            report = self.generate_workflow_report(
                keyword, city, pages, max_details_per_page, 
                len(all_details), export_result
            )
            
            print(f"\n{'=' * 60}")
            print("🎉 即时工作流执行成功！")
            print(f"📊 采集统计:")
            print(f"  - 搜索关键词: {keyword}")
            print(f"  - 目标城市: {city}")
            print(f"  - 处理页数: {pages}")
            print(f"  - 获取详情: {len(all_details)} 个职位")
            print(f"  - 输出文件: {export_result['main_file']}")
            print(f"  - 输出目录: {export_result['export_dir']}")
            print(f"📄 工作报告: {report}")
            
            return True
        else:
            print("\n❌ 导出失败")
            return False
    
    def generate_workflow_report(self, keyword, city, pages, max_details, 
                                total_details, export_result):
        """生成工作报告"""
        report_file = self.output_base / "工作报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 即时工作流采集报告\n\n")
            f.write(f"**采集时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**工作流类型**: 策略A（即时工作流）\n\n")
            
            f.write(f"## 📊 采集统计\n\n")
            f.write(f"| 项目 | 数据 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 搜索关键词 | {keyword} |\n")
            f.write(f"| 目标城市 | {city} |\n")
            f.write(f"| 处理页数 | {pages} 页 |\n")
            f.write(f"| 每页限制 | {max_details} 个 |\n")
            f.write(f"| 获取详情 | {total_details} 个职位 |\n")
            f.write(f"| 输出文件 | {Path(export_result['main_file']).name} |\n")
            f.write(f"| 输出目录 | {export_result['export_dir']} |\n\n")
            
            f.write(f"## 📁 文件结构\n\n")
            f.write(f"```\n")
            f.write(f"{self.output_base}/\n")
            
            # 列出文件
            for item in self.output_base.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(self.output_base)
                    size = item.stat().st_size
                    f.write(f"├── {rel_path} ({size:,} bytes)\n")
            
            f.write(f"```\n\n")
            
            f.write(f"## 🚀 使用说明\n\n")
            f.write(f"### 1. 查看数据\n")
            f.write(f"```bash\n")
            f.write(f"# 查看Excel文件\n")
            f.write(f"open {export_result['main_file']}\n")
            f.write(f"\n# 查看原始数据\n")
            f.write(f"cat {export_result['raw_file']} | python3 -m json.tool | head -100\n")
            f.write(f"```\n\n")
            
            f.write(f"### 2. 再次运行\n")
            f.write(f"```bash\n")
            f.write(f"# 确保已登录\n")
            f.write(f"boss login --cookie-source chrome\n")
            f.write(f"\n# 运行即时工作流\n")
            f.write(f"python3 {Path(__file__).name} --keyword {keyword} --city {city} --pages {pages}\n")
            f.write(f"```\n\n")
            
            f.write(f"### 3. 数据分析建议\n")
            f.write(f"- **薪资分析**: 统计各薪资范围的职位数量\n")
            f.write(f"- **技能分析**: 分析最常要求的技能\n")
            f.write(f"- **地区分析**: 查看工作地点分布\n")
            f.write(f"- **公司分析**: 比较不同规模公司的招聘需求\n\n")
            
            f.write(f"## 💡 最佳实践\n\n")
            f.write(f"1. **登录后立即执行**: 在`__zp_stoken__`有效期内（3-5分钟）完成所有操作\n")
            f.write(f"2. **合理设置参数**: 根据网络情况调整延迟和重试次数\n")
            f.write(f"3. **定期采集**: 建议每周采集一次，跟踪市场变化\n")
            f.write(f"4. **数据备份**: 定期备份采集的数据文件\n")
        
        return str(report_file)


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='即时工作流工具 - 策略A实现')
    parser.add_argument('--keyword', default='AI', help='搜索关键词')
    parser.add_argument('--city', default='深圳', help='城市')
    parser.add_argument('--pages', type=int, default=1, help='搜索页数')
    parser.add_argument('--max-details', type=int, default=10, help='每页最多获取详情数')
    parser.add_argument('--output-dir', help='输出目录')
    parser.add_argument('--delay', type=int, default=2, help='页间延迟（秒）')
    
    args = parser.parse_args()
    
    # 显示使用提示
    print("💡 使用提示: 请确保已登录BOSS直聘")
    print("   运行: boss login --cookie-source chrome")
    print("   然后立即运行本工具\n")
    
    # 创建工具实例
    tool = ImmediateWorkflow(args.output_dir)
    
    # 运行即时工作流
    success = tool.run_immediate_workflow(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages,
        max_details_per_page=args.max_details,
        delay_between_pages=args.delay
    )
    
    if success:
        print(f"\n✅ 即时工作流执行成功!")
        print(f"📅 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(0)
    else:
        print(f"\n❌ 即时工作流执行失败")
        print(f"💡 建议: 检查登录状态，稍后重试")
        sys.exit(1)


if __name__ == "__main__":
    main()