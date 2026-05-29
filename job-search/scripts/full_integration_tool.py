#!/usr/bin/env python3
"""
完整的BOSS直聘数据整合工具
将搜索、获取详情和Excel导出功能完整整合
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class BossFullIntegration:
    """完整的BOSS直聘数据整合工具"""
    
    def __init__(self, output_base_dir=None):
        """初始化工具"""
        self.setup_environment()
        
        if output_base_dir:
            self.output_base = Path(output_base_dir)
        else:
            self.output_base = Path.home() / "招聘数据" / "完整导出"
        
        self.output_base.mkdir(parents=True, exist_ok=True)
        
        # 导入扩展导出器
        sys.path.insert(0, str(Path(__file__).parent))
        try:
            from extended_excel_exporter import ExtendedExcelExporter
            self.exporter_class = ExtendedExcelExporter
        except ImportError:
            print("⚠️  无法导入扩展导出器，使用基础导出器")
            # 这里可以回退到基础导出器
            self.exporter_class = None
    
    def setup_environment(self):
        """设置环境变量"""
        boss_path = "/Users/xingan/Library/Python/3.12/bin"
        if boss_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{boss_path}:{os.environ.get('PATH', '')}"
    
    def run_boss_command(self, cmd_args, timeout=30):
        """运行boss命令"""
        cmd = ["boss"] + cmd_args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result
        except subprocess.TimeoutExpired:
            print(f"❌ 命令超时: {' '.join(cmd)}")
            return None
        except Exception as e:
            print(f"❌ 命令执行失败: {e}")
            return None
    
    def check_login_status(self):
        """检查登录状态"""
        print("🔍 检查登录状态...")
        result = self.run_boss_command(["status"])
        
        if result and result.returncode == 0:
            if "search=ok" in result.stdout:
                print("✅ 登录状态正常 (search=ok)")
                return True
            else:
                print("⚠️  登录状态异常")
                print(result.stdout[:200])
                return False
        else:
            print("❌ 无法检查登录状态")
            return False
    
    def search_jobs(self, keyword="AI", city="深圳", page=1, max_results=15):
        """
        搜索职位
        
        Returns:
            (success, data_or_error)
        """
        print(f"🔍 搜索职位: {keyword} - {city} (第{page}页)")
        
        result = self.run_boss_command([
            "search", keyword,
            "--city", city,
            "--page", str(page),
            "--json"
        ])
        
        if not result or result.returncode != 0:
            print(f"❌ 搜索失败: {result.stderr if result else '无输出'}")
            return False, "搜索命令执行失败"
        
        try:
            data = json.loads(result.stdout)
            
            if data.get('ok'):
                jobs = data.get('data', {}).get('jobList', [])
                total = len(jobs)
                
                if total > 0:
                    print(f"✅ 搜索成功: 找到 {total} 个职位")
                    
                    # 限制返回数量
                    if max_results and total > max_results:
                        jobs = jobs[:max_results]
                        print(f"📊 限制为前 {len(jobs)} 个职位")
                    
                    return True, {
                        'jobs': jobs,
                        'hasMore': data.get('data', {}).get('hasMore', False),
                        'total': total,
                        'page': page
                    }
                else:
                    print("❌ 搜索成功但没有找到职位")
                    return False, "没有找到职位"
            else:
                error_msg = data.get('error', {}).get('message', '未知错误')
                print(f"❌ 搜索数据异常: {error_msg}")
                return False, error_msg
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"原始输出: {result.stdout[:200]}")
            return False, "JSON解析失败"
        except Exception as e:
            print(f"❌ 搜索处理异常: {e}")
            return False, str(e)
    
    def get_job_detail(self, security_id, job_index=None):
        """获取职位详情"""
        if job_index:
            print(f"🔍 获取职位 {job_index} 详情...")
        else:
            print(f"🔍 获取职位详情...")
        
        result = self.run_boss_command([
            "detail", security_id,
            "--json"
        ])
        
        if not result or result.returncode != 0:
            if job_index:
                print(f"❌ 职位 {job_index} 详情获取失败")
            else:
                print("❌ 职位详情获取失败")
            return None
        
        try:
            data = json.loads(result.stdout)
            
            if data.get('ok'):
                if job_index:
                    print(f"✅ 职位 {job_index} 详情获取成功")
                else:
                    print("✅ 职位详情获取成功")
                return data
            else:
                error_msg = data.get('error', {}).get('message', '未知错误')
                if job_index:
                    print(f"❌ 职位 {job_index} 数据异常: {error_msg}")
                else:
                    print(f"❌ 职位数据异常: {error_msg}")
                return None
                
        except json.JSONDecodeError as e:
            if job_index:
                print(f"❌ 职位 {job_index} JSON解析失败: {e}")
            else:
                print(f"❌ JSON解析失败: {e}")
            return None
    
    def batch_get_details(self, jobs_data, max_details=None, delay=1):
        """批量获取职位详情"""
        if not jobs_data:
            print("❌ 没有职位数据")
            return []
        
        total = len(jobs_data)
        if max_details and total > max_details:
            jobs_data = jobs_data[:max_details]
            print(f"📊 限制为前 {len(jobs_data)} 个职位详情")
        
        print(f"🚀 开始批量获取 {len(jobs_data)} 个职位详情")
        
        details = []
        success_count = 0
        failed_count = 0
        
        for i, job in enumerate(jobs_data, 1):
            job_name = job.get('jobName', f'职位{i}')[:30]
            security_id = job.get('securityId', '')
            
            if not security_id:
                print(f"❌ 职位 {i}: {job_name} 缺少securityId，跳过")
                failed_count += 1
                continue
            
            print(f"  [{i}/{len(jobs_data)}] 获取: {job_name}")
            
            detail = self.get_job_detail(security_id, i)
            
            if detail:
                details.append(detail)
                success_count += 1
                
                # 保存到文件
                detail_file = self.output_base / f"temp_detail_{i}.json"
                with open(detail_file, 'w', encoding='utf-8') as f:
                    json.dump(detail, f, ensure_ascii=False, indent=2)
            else:
                failed_count += 1
            
            # 延迟，避免请求过快
            if i < len(jobs_data) and delay > 0:
                time.sleep(delay)
        
        print(f"\n📊 批量获取完成:")
        print(f"  ✅ 成功: {success_count} 个")
        print(f"  ❌ 失败: {failed_count} 个")
        print(f"  📁 临时文件: {self.output_base}")
        
        return details
    
    def export_to_excel(self, detail_data_list, search_keyword, search_page, output_name=None):
        """导出到Excel"""
        if not detail_data_list:
            print("❌ 没有详情数据可导出")
            return None
        
        if not self.exporter_class:
            print("❌ 导出器不可用")
            return None
        
        # 创建时间戳目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = self.output_base / f"完整导出_{timestamp}"
        export_dir.mkdir(exist_ok=True)
        
        print(f"📁 导出目录: {export_dir}")
        
        # 创建导出器
        exporter = self.exporter_class(str(export_dir))
        
        # 导出数据
        if not output_name:
            output_name = f"深圳_{search_keyword}_岗位_完整数据_{timestamp}.csv"
        
        output_files = exporter.export_detail_data(
            detail_data_list,
            search_keyword=search_keyword,
            search_page=search_page,
            filename=output_name,
            include_stats=True
        )
        
        if output_files:
            # 保存原始数据
            raw_data_file = export_dir / f"原始数据_{timestamp}.json"
            with open(raw_data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'search_keyword': search_keyword,
                    'search_page': search_page,
                    'total_jobs': len(detail_data_list),
                    'export_time': timestamp,
                    'details': detail_data_list
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n🎉 导出成功！")
            print(f"📊 职位数量: {len(detail_data_list)}")
            print(f"📁 主文件: {output_files[0]}")
            print(f"📁 原始数据: {raw_data_file}")
            print(f"📁 输出目录: {export_dir}")
            
            return {
                'export_dir': str(export_dir),
                'main_file': output_files[0] if output_files else None,
                'raw_data_file': str(raw_data_file),
                'total_jobs': len(detail_data_list)
            }
        else:
            print("❌ 导出失败")
            return None
    
    def full_workflow(self, keyword="AI", city="深圳", pages=1, max_details_per_page=5):
        """完整工作流程"""
        print("🚀 BOSS直聘完整数据整合工作流")
        print("=" * 60)
        
        # 1. 检查登录状态
        if not self.check_login_status():
            print("❌ 请先登录: boss login --cookie-source chrome")
            return False
        
        all_details = []
        
        for page in range(1, pages + 1):
            print(f"\n📄 处理第 {page}/{pages} 页")
            
            # 2. 搜索职位
            success, result = self.search_jobs(keyword, city, page)
            if not success:
                print(f"❌ 第{page}页搜索失败: {result}")
                continue
            
            jobs_data = result['jobs']
            print(f"📊 找到 {len(jobs_data)} 个职位")
            
            # 3. 批量获取详情
            page_details = self.batch_get_details(
                jobs_data, 
                max_details=max_details_per_page,
                delay=1  # 1秒延迟
            )
            
            all_details.extend(page_details)
            
            # 页间延迟
            if page < pages and len(page_details) > 0:
                print(f"⏳ 等待2秒后处理下一页...")
                time.sleep(2)
        
        if not all_details:
            print("\n❌ 没有获取到任何职位详情")
            return False
        
        print(f"\n✅ 所有页面处理完成")
        print(f"📊 总计获取: {len(all_details)} 个职位详情")
        
        # 4. 导出到Excel
        export_result = self.export_to_excel(all_details, keyword, pages)
        
        if export_result:
            print(f"\n🎉 完整工作流执行成功！")
            print(f"📁 导出目录: {export_result['export_dir']}")
            print(f"📊 职位数量: {export_result['total_jobs']}")
            return True
        else:
            print("\n❌ 导出失败")
            return False


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='BOSS直聘完整数据整合工具')
    parser.add_argument('--keyword', default='AI', help='搜索关键词')
    parser.add_argument('--city', default='深圳', help='城市')
    parser.add_argument('--pages', type=int, default=1, help='搜索页数')
    parser.add_argument('--max-details', type=int, default=5, help='每页最多获取详情数')
    parser.add_argument('--output-dir', help='输出目录')
    
    args = parser.parse_args()
    
    # 创建工具实例
    tool = BossFullIntegration(args.output_dir)
    
    # 执行完整工作流
    success = tool.full_workflow(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages,
        max_details_per_page=args.max_details
    )
    
    if success:
        print("\n✅ 任务完成！")
        sys.exit(0)
    else:
        print("\n❌ 任务失败")
        sys.exit(1)


if __name__ == "__main__":
    main()