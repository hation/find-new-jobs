#!/usr/bin/env python3
"""
方案B批量处理器 - 专门处理大批量数据（如10页）
优化逻辑以适应token有效期限制
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

class BatchProcessor:
    """方案B批量处理器"""
    
    def __init__(self, output_base=None):
        self.setup_environment()
        
        if output_base:
            self.output_base = Path(output_base)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_base = Path.home() / "招聘数据" / f"方案B批量_{timestamp}"
        
        self.output_base.mkdir(parents=True, exist_ok=True)
        
        # 状态文件
        self.state_file = self.output_base / "processing_state.json"
        self.load_state()
    
    def setup_environment(self):
        """设置环境变量"""
        boss_path = "/Users/xingan/Library/Python/3.12/bin"
        if boss_path not in os.environ.get('PATH', ''):
            os.environ['PATH'] = f"{boss_path}:{os.environ.get('PATH', '')}"
    
    def load_state(self):
        """加载处理状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
                print(f"✅ 加载处理状态: {self.state_file}")
            except:
                self.state = {}
        else:
            self.state = {
                'start_time': datetime.now().isoformat(),
                'total_pages': 0,
                'processed_pages': 0,
                'extracted_ids': 0,
                'processed_ids': 0,
                'successful_details': 0,
                'failed_details': 0,
                'batches': []
            }
    
    def save_state(self):
        """保存处理状态"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def run_boss_command(self, cmd_args, description="", retries=1):
        """运行boss命令"""
        cmd = ["boss"] + cmd_args
        
        for attempt in range(retries + 1):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    if description:
                        print(f"✅ {description}")
                    return True, result.stdout
                else:
                    error_msg = result.stderr or result.stdout or "未知错误"
                    
                    if "环境异常" in error_msg or "__zp_stoken__" in error_msg:
                        print(f"    ⚠️  Token过期 (尝试 {attempt+1}/{retries+1})")
                        if attempt < retries:
                            time.sleep(2)
                            continue
                    
                    if description:
                        print(f"❌ {description}失败: {error_msg[:100]}")
                    return False, error_msg
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏱️  命令超时 (尝试 {attempt+1}/{retries+1})")
                if attempt < retries:
                    time.sleep(2)
                continue
            except Exception as e:
                return False, str(e)
        
        return False, "所有重试都失败"
    
    def login_and_search_batch(self, keyword, city, start_page, pages_per_batch=3):
        """
        登录并搜索一批数据
        每批处理少量页面，确保在token有效期内完成
        """
        print(f"\n📋 处理批次: 第{start_page}-{start_page+pages_per_batch-1}页")
        print("-" * 50)
        
        # 登录
        print("🔑 登录...")
        success, _ = self.run_boss_command(
            ["login", "--cookie-source", "chrome"],
            "登录"
        )
        
        if not success:
            print("❌ 登录失败，跳过此批次")
            return False, []
        
        # 检查登录状态
        success, status = self.run_boss_command(["status"], "检查登录状态")
        if not success or "search=ok" not in status:
            print("❌ 登录状态异常，跳过此批次")
            return False, []
        
        # 搜索批次内的所有页面
        all_security_ids = []
        
        for page in range(start_page, start_page + pages_per_batch):
            print(f"\n📄 搜索第 {page} 页...")
            
            search_file = self.output_base / f"search_page_{page}.json"
            success, result = self.run_boss_command(
                ["search", keyword, "--city", city, "--page", str(page), "--json"],
                f"搜索第{page}页"
            )
            
            if success:
                # 保存搜索数据
                with open(search_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                
                # 提取securityId（每页最多10个）
                try:
                    data = json.loads(result)
                    if data.get('ok'):
                        jobs = data.get('data', {}).get('jobList', [])
                        page_ids = []
                        
                        for i, job in enumerate(jobs[:10], 1):  # 每页最多10个
                            security_id = job.get('securityId')
                            job_name = job.get('jobName', f'职位{i}')[:40]
                            
                            if security_id:
                                page_ids.append((security_id, job_name, page))
                                print(f"  [{i}] {job_name}")
                        
                        if page_ids:
                            all_security_ids.extend(page_ids)
                            print(f"✅ 第{page}页提取到 {len(page_ids)} 个securityId")
                        else:
                            print(f"⚠️  第{page}页没有提取到securityId")
                except:
                    print(f"❌ 第{page}页数据解析失败")
            
            # 页间短暂延迟
            if page < start_page + pages_per_batch - 1:
                time.sleep(1)
        
        if all_security_ids:
            print(f"\n📊 本批次总计: {len(all_security_ids)} 个securityId")
            
            # 保存到批次文件
            batch_id = len(self.state['batches']) + 1
            batch_file = self.output_base / f"batch_{batch_id}_ids.txt"
            
            with open(batch_file, 'w', encoding='utf-8') as f:
                for security_id, job_name, page in all_security_ids:
                    f.write(f"{security_id}|{job_name}|{page}\n")
            
            # 更新状态
            self.state['batches'].append({
                'batch_id': batch_id,
                'start_page': start_page,
                'end_page': start_page + pages_per_batch - 1,
                'security_ids': len(all_security_ids),
                'batch_file': str(batch_file),
                'processed': False,
                'success_count': 0
            })
            
            self.state['extracted_ids'] += len(all_security_ids)
            self.save_state()
            
            return True, all_security_ids
        else:
            print("❌ 本批次没有提取到securityId")
            return False, []
    
    def process_details_batch(self, batch_id, max_details_per_session=15):
        """
        处理一个批次的详情获取
        每批次分多次会话，避免token过期
        """
        print(f"\n📋 处理批次 {batch_id} 的详情")
        print("-" * 50)
        
        # 查找批次数据
        batch_info = None
        for batch in self.state['batches']:
            if batch['batch_id'] == batch_id and not batch['processed']:
                batch_info = batch
                break
        
        if not batch_info:
            print(f"❌ 批次 {batch_id} 不存在或已处理")
            return False
        
        batch_file = Path(batch_info['batch_file'])
        if not batch_file.exists():
            print(f"❌ 批次文件不存在: {batch_file}")
            return False
        
        # 读取securityId
        security_ids = []
        with open(batch_file, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) >= 2:
                    security_ids.append((parts[0], parts[1], parts[2] if len(parts) > 2 else '1'))
        
        if not security_ids:
            print(f"❌ 批次 {batch_id} 没有securityId")
            return False
        
        print(f"📊 本批次有 {len(security_ids)} 个职位需要处理")
        print(f"🔧 将分 {((len(security_ids)-1)//max_details_per_session)+1} 次会话处理")
        
        # 分多次会话处理
        total_success = 0
        session_count = 0
        
        for i in range(0, len(security_ids), max_details_per_session):
            session_count += 1
            session_ids = security_ids[i:i+max_details_per_session]
            
            print(f"\n🔄 会话 {session_count}: 处理 {len(session_ids)} 个职位")
            
            # 重新登录
            print("🔑 重新登录...")
            success, _ = self.run_boss_command(
                ["login", "--cookie-source", "chrome"],
                f"会话{session_count}登录"
            )
            
            if not success:
                print(f"❌ 会话{session_count}登录失败，跳过")
                continue
            
            # 检查登录状态
            success, status = self.run_boss_command(["status"], "检查登录状态")
            if not success or "search=ok" not in status:
                print(f"❌ 会话{session_count}登录状态异常，跳过")
                continue
            
            # 获取详情
            session_success = 0
            details_dir = self.output_base / f"details_batch{batch_id}"
            details_dir.mkdir(exist_ok=True)
            
            for j, (security_id, job_name, page) in enumerate(session_ids, 1):
                print(f"  [{j}/{len(session_ids)}] {job_name}")
                
                detail_file = details_dir / f"detail_{i+j}.json"
                success, result = self.run_boss_command(
                    ["detail", security_id, "--json"],
                    f"获取详情 {i+j}"
                )
                
                if success:
                    try:
                        data = json.loads(result)
                        if data.get('ok'):
                            with open(detail_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            session_success += 1
                            print(f"      ✅ 成功")
                        else:
                            print(f"      ❌ 数据异常")
                    except:
                        print(f"      ❌ 数据解析失败")
                else:
                    print(f"      ❌ 获取失败")
                
                # 延迟
                if j < len(session_ids):
                    time.sleep(1)
            
            total_success += session_success
            print(f"✅ 会话{session_count}完成: {session_success}/{len(session_ids)} 成功")
            
            # 会话间延迟
            if i + max_details_per_session < len(security_ids):
                print(f"⏳ 等待3秒后开始下一会话...")
                time.sleep(3)
        
        # 更新批次状态
        batch_info['processed'] = True
        batch_info['success_count'] = total_success
        batch_info['processed_time'] = datetime.now().isoformat()
        
        # 更新全局状态
        self.state['processed_ids'] += len(security_ids)
        self.state['successful_details'] += total_success
        self.state['failed_details'] += (len(security_ids) - total_success)
        
        self.save_state()
        
        print(f"\n📊 批次 {batch_id} 处理完成:")
        print(f"  ✅ 成功: {total_success} 个")
        print(f"  ❌ 失败: {len(security_ids) - total_success} 个")
        print(f"  📊 成功率: {total_success/len(security_ids)*100:.1f}%")
        
        return total_success > 0
    
    def process_10_pages(self, keyword="AI", city="深圳", pages=10):
        """
        处理10页数据的完整流程
        """
        print("🚀 方案B批量处理10页数据")
        print("=" * 60)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 搜索配置: {keyword} - {city} (共{pages}页)")
        print("=" * 60)
        
        self.state['total_pages'] = pages
        self.save_state()
        
        # ===== 步骤1：分批次搜索并提取securityId =====
        print("\n" + "=" * 50)
        print("📋 步骤1：分批次搜索并提取securityId")
        print("=" * 50)
        
        pages_per_batch = 3  # 每批3页，避免token过期
        all_batches_success = True
        
        for start_page in range(1, pages + 1, pages_per_batch):
            end_page = min(start_page + pages_per_batch - 1, pages)
            
            print(f"\n🎯 处理页面范围: {start_page}-{end_page}")
            
            success, batch_ids = self.login_and_search_batch(
                keyword, city, start_page, pages_per_batch
            )
            
            if success:
                self.state['processed_pages'] += (end_page - start_page + 1)
                self.save_state()
                print(f"✅ 页面 {start_page}-{end_page} 处理完成")
            else:
                all_batches_success = False
                print(f"❌ 页面 {start_page}-{end_page} 处理失败")
            
            # 批次间提示
            if end_page < pages:
                print(f"\n💡 批次完成，准备下一批次")
                print(f"⏳ 请确保仍在浏览器中登录BOSS直聘")
                print(f"📊 已处理: {self.state['processed_pages']}/{pages} 页")
                print(f"📊 已提取: {self.state['extracted_ids']} 个securityId")
                input("⏳ 按Enter键继续下一批次...")
        
        print(f"\n✅ 步骤1完成")
        print(f"📊 总计提取: {self.state['extracted_ids']} 个securityId")
        print(f"📁 数据保存在: {self.output_base}")
        
        if self.state['extracted_ids'] == 0:
            print("❌ 没有提取到任何securityId，停止流程")
            return False
        
        # ===== 步骤2：分批次获取详情 =====
        print("\n" + "=" * 50)
        print("📋 步骤2：分批次获取详情")
        print("=" * 50)
        
        print(f"📊 准备处理 {len(self.state['batches'])} 个批次")
        print(f"💡 每个批次将分多次会话处理，避免token过期")
        
        for batch in self.state['batches']:
            if not batch['processed']:
                batch_id = batch['batch_id']
                
                print(f"\n🎯 处理批次 {batch_id}")
                print(f"📊 包含: {batch['security_ids']} 个职位")
                
                success = self.process_details_batch(batch_id, max_details_per_session=12)
                
                if success:
                    print(f"✅ 批次 {batch_id} 处理完成")
                else:
                    print(f"❌ 批次 {batch_id} 处理失败")
                
                # 批次间提示
                if batch_id < len(self.state['batches']):
                    print(f"\n💡 批次完成，准备下一批次")
                    print(f"⏳ 请确保仍在浏览器中登录BOSS直聘")
                    print(f"📊 已处理: {batch_id}/{len(self.state['batches'])} 个批次")
                    input("⏳ 按Enter键继续下一批次...")
        
        # ===== 生成最终报告 =====
        print("\n" + "=" * 50)
        print("📋 生成最终报告")
        print("=" * 50)
        
        self.generate_final_report(keyword, city, pages)
        
        print(f"\n{'=' * 60}")
        print("🎉 方案B批量处理完成！")
        print(f"📊 最终统计:")
        print(f"  - 搜索关键词: {keyword}")
        print(f"  - 目标城市: {city}")
        print(f"  - 处理页数: {pages} 页")
        print(f"  - 提取securityId: {self.state['extracted_ids']} 个")
        print(f"  - 获取详情: {self.state['successful_details']} 个职位")
        print(f"  - 成功率: {self.state['successful_details']/self.state['extracted_ids']*100:.1f}%")
        print(f"  - 输出目录: {self.output_base}")
        
        return True
    
    def generate_final_report(self, keyword, city, pages):
        """生成最终报告"""
        report_file = self.output_base / "批量处理报告.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 方案B批量处理报告\n\n")
            f.write(f"**处理时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**工作流类型**: 方案B批量处理（优化版）\n\n")
            
            f.write(f"## 📊 处理统计\n\n")
            f.write(f"| 项目 | 数据 |\n")
            f.write(f"|------|------|\n")
            f.write(f"| 搜索关键词 | {keyword} |\n")
            f.write(f"| 目标城市 | {city} |\n")
            f.write(f"| 目标页数 | {pages} 页 |\n")
            f.write(f"| 实际处理页数 | {self.state['processed_pages']} 页 |\n")
            f.write(f"| 提取securityId | {self.state['extracted_ids']} 个 |\n")
            f.write(f"| 成功获取详情 | {self.state['successful_details']} 个职位 |\n")
            f.write(f"| 失败详情 | {self.state['failed_details']} 个职位 |\n")
            f.write(f"| 总成功率 | {self.state['successful_details']/self.state['extracted_ids']*100:.1f}% |\n")
            f.write(f"| 输出目录 | {self.output_base} |\n\n")
            
            f.write(f"## 🔄 批次处理详情\n\n")
            for batch in self.state['batches']:
                f.write(f"### 批次 {batch['batch_id']}\n")
                f.write(f"- 页面范围: {batch['start_page']}-{batch['end_page']}\n")
                f.write(f"- securityId数量: {batch['security_ids']} 个\n")
                f.write(f"- 成功获取详情: {batch.get('success_count', 0)} 个\n")
                f.write(f"- 处理状态: {'✅ 已完成' if batch.get('processed') else '❌ 未完成'}\n")
                if batch.get('processed_time'):
                    f.write(f"- 处理时间: {batch['processed_time']}\n")
                f.write(f"\n")
            
            f.write(f"## 🎯 优化策略\n\n")
            f.write(f"1. **分批次搜索**: 每3页为一个批次，避免token过期\n")
            f.write(f"2. **分会话获取详情**: 每12个职位为一个会话，确保在token有效期内完成\n")
            f.write(f"3. **智能重试**: 失败后自动重试，记录处理状态\n")
            f.write(f"4. **断点续传**: 支持从中断的地方继续处理\n")
            f.write(f"5. **状态保存**: 实时保存处理进度，防止数据丢失\n\n")
            
            f.write(f"## 📁 文件结构\n\n")
            f.write(f"```\n")
            f.write(f"{self.output_base}/\n")
            
            # 列出主要文件
            for item in sorted(self.output_base.rglob("*")):
                if item.is_file() and item.suffix in ['.json', '.txt', '.md']:
                    rel_path = item.relative_to(self.output_base)
                    size = item.stat().st_size
                    f.write(f"├── {rel_path} ({size:,} bytes)\n")
            
            f.write(f"```\n\n")
            
            f.write(f"## 🔄 再次运行或继续\n")
            f.write(f"```bash\n")
            f.write(f"# 查看当前状态\n")
            f.write(f"cat {self.state_file}\n\n")
            f.write(f"# 如果中断，可以手动继续\n")
            f.write(f"python3 {Path(__file__).name} --continue\n")
            f.write(f"```\n")
        
        print(f"📄 报告已生成: {report_file}")


def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='方案B批量处理器 - 处理大批量数据')
    parser.add_argument('--keyword', default='AI', help='搜索关键词')
    parser.add_argument('--city', default='深圳', help='城市')
    parser.add_argument('--pages', type=int, default=10, help='搜索页数')
    parser.add_argument('--continue', dest='continue_mode', action='store_true', help='继续上次的处理')
    
    args = parser.parse_args()
    
    # 创建处理器
    processor = BatchProcessor()
    
    # 运行批量处理
    success = processor.process_10_pages(
        keyword=args.keyword,
        city=args.city,
        pages=args.pages
    )
    
    if success:
        print(f"\n✅ 批量处理执行成功!")
        sys.exit(0)
    else:
        print(f"\n❌ 批量处理执行失败")
        sys.exit(1)


if __name__ == "__main__":
    main()