#!/usr/bin/env python3
"""
批量职位抓取脚本 - 解决__zp_stoken__过期问题
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def setup_environment():
    """设置环境变量"""
    os.environ["PATH"] = f"/Users/xingan/Library/Python/3.12/bin:{os.environ.get('PATH', '')}"

def run_boss_command(cmd_args, description=None):
    """运行boss命令"""
    if description:
        print(f"🔧 {description}...")
    
    cmd = ["boss"] + cmd_args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result
    except Exception as e:
        print(f"❌ 命令执行失败: {e}")
        return None

def check_login_status():
    """检查登录状态"""
    print("📊 检查登录状态...")
    result = run_boss_command(["status"])
    
    if result and result.returncode == 0:
        # 解析状态输出
        for line in result.stdout.split('\n'):
            if "search=ok" in line:
                print("✅ 登录状态正常 (search=ok)")
                return True
            elif "search=fail" in line and "__zp_stoken__" in line:
                print("❌ __zp_stoken__已过期")
                return False
    print("⚠️  登录状态未知")
    return False

def scrape_jobs(keyword, city, pages=3, output_dir=None):
    """批量抓取职位数据"""
    if output_dir is None:
        output_dir = Path.home() / "招聘数据" / f"{city}_{keyword}_{time.strftime('%Y%m%d_%H%M%S')}"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 数据将保存到: {output_dir}")
    
    all_jobs = []
    
    for page in range(1, pages + 1):
        print(f"\n📄 抓取第 {page}/{pages} 页...")
        
        # 构建搜索命令
        cmd = ["search", keyword, "--city", city, "--page", str(page), "--json"]
        result = run_boss_command(cmd, f"搜索第{page}页")
        
        if not result or result.returncode != 0:
            print(f"❌ 第{page}页搜索失败")
            continue
        
        # 尝试解析JSON
        try:
            for line in result.stdout.split('\n'):
                if line.strip().startswith('{'):
                    data = json.loads(line.strip())
                    if data.get("ok"):
                        jobs = data.get("data", {}).get("jobList", [])
                        print(f"✅ 获取到 {len(jobs)} 个职位")
                        
                        # 保存该页数据
                        page_file = output_dir / f"page_{page}.json"
                        with open(page_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        
                        # 添加到总列表
                        all_jobs.extend(jobs)
                        break
        except Exception as e:
            print(f"⚠️  解析失败: {e}")
        
        # 短暂延迟，避免请求过快
        if page < pages:
            time.sleep(1)
    
    # 保存合并后的数据
    if all_jobs:
        merged_file = output_dir / "all_jobs.json"
        with open(merged_file, 'w', encoding='utf-8') as f:
            json.dump({
                "ok": True,
                "data": {
                    "jobList": all_jobs,
                    "total": len(all_jobs)
                },
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword,
                "city": city
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n🎉 抓取完成！")
        print(f"📊 总计: {len(all_jobs)} 个职位")
        print(f"📁 数据目录: {output_dir}")
        
        # 生成统计报告
        generate_report(all_jobs, output_dir)
    
    return all_jobs, output_dir

def generate_report(jobs, output_dir):
    """生成统计报告"""
    report_file = output_dir / "report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 职位数据统计报告\n\n")
        f.write(f"- **抓取时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **职位数量**: {len(jobs)} 个\n")
        f.write(f"- **数据文件**: all_jobs.json\n\n")
        
        f.write("## 薪资分布\n")
        
        # 薪资分析
        salary_stats = {}
        for job in jobs:
            salary = job.get('salaryDesc', '未知')
            salary_stats[salary] = salary_stats.get(salary, 0) + 1
        
        for salary, count in sorted(salary_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {salary}: {count} 个职位\n")
        
        f.write("\n## 公司分布\n")
        
        # 公司分析
        company_stats = {}
        for job in jobs:
            company = job.get('brandName', '未知公司')
            company_stats[company] = company_stats.get(company, 0) + 1
        
        for company, count in sorted(company_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"- {company}: {count} 个职位\n")
        
        f.write("\n## 职位列表（前20个）\n")
        f.write("| 序号 | 职位名称 | 薪资 | 公司 | 地区 |\n")
        f.write("|------|----------|------|------|------|\n")
        
        for i, job in enumerate(jobs[:20], 1):
            name = job.get('jobName', '未知')
            salary = job.get('salaryDesc', '未知')
            company = job.get('brandName', '未知')
            area = job.get('areaDistrict', '未知')
            f.write(f"| {i} | {name} | {salary} | {company} | {area} |\n")
    
    print(f"📋 报告生成: {report_file}")

def create_quick_view_script(output_dir):
    """创建快速查看脚本"""
    script_content = f'''#!/bin/bash
echo "🚀 快速查看职位数据"
echo "========================"
echo "数据目录: {output_dir}"
echo ""

# 显示统计信息
echo "📊 数据统计:"
python3 -c "
import json, os, sys
try:
    with open('{output_dir}/all_jobs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jobs = data.get('data', {{}}).get('jobList', [])
    print(f'  职位总数: {{len(jobs)}}')
    
    # 薪资统计
    salary_stats = {{}}
    for job in jobs:
        salary = job.get('salaryDesc', '未知')
        salary_stats[salary] = salary_stats.get(salary, 0) + 1
    
    print('  薪资分布:')
    for salary, count in sorted(salary_stats.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f'    {salary}: {count}个')
    
    print('')
    print('  前10个职位:')
    for i, job in enumerate(jobs[:10], 1):
        name = job.get('jobName', '未知')[:30]
        salary = job.get('salaryDesc', '未知')
        company = job.get('brandName', '未知')[:20]
        print(f'    {i}. {name}')
        print(f'       薪资: {salary}, 公司: {company}')
        print()
except Exception as e:
    print(f'  数据加载失败: {{e}}')
"

echo ""
echo "🔧 可用命令:"
echo "  # 查看完整数据"
echo "  cat {output_dir}/all_jobs.json | jq '.'"
echo ""
echo "  # 提取职位名称和薪资"
echo "  cat {output_dir}/all_jobs.json | jq -r '.data.jobList[] | \"\\(.jobName) - \\(.salaryDesc) (\\(.brandName))\"'"
echo ""
echo "  # 查看报告"
echo "  cat {output_dir}/report.md"
'''
    
    script_file = output_dir / "quick_view.sh"
    script_file.write_text(script_content, encoding="utf-8")
    script_file.chmod(0o755)
    
    return script_file

def main():
    """主函数"""
    print("🎯 BOSS直聘批量职位抓取工具")
    print("==============================")
    print("注意: 请在登录后立即运行此脚本")
    print("      __zp_stoken__ 有效期很短")
    print()
    
    setup_environment()
    
    # 检查登录状态
    if not check_login_status():
        print("\n❌ 登录状态异常，请先登录:")
        print("   1. boss logout")
        print("   2. 浏览器登录 https://www.zhipin.com")
        print("   3. boss login --cookie-source chrome")
        print("   4. 立即运行此脚本")
        return 1
    
    print("\n🚀 开始批量抓取...")
    
    # 抓取参数
    keyword = "AI"
    city = "深圳"
    pages = 3  # 抓取3页
    
    jobs, output_dir = scrape_jobs(keyword, city, pages)
    
    if jobs:
        # 创建快速查看脚本
        script_file = create_quick_view_script(output_dir)
        
        print(f"\n💡 快速查看命令:")
        print(f"   sh {script_file}")
        
        print(f"\n📝 最佳实践:")
        print("   1. 登录后立即运行此脚本")
        print("   2. 批量抓取，避免多次登录")
        print("   3. 及时保存数据到文件")
        print("   4. 从JSON文件分析数据，而非实时API")
    else:
        print("❌ 未获取到任何职位数据")
        print("   可能原因:")
        print("   - __zp_stoken__ 已过期")
        print("   - 网络问题")
        print("   - 搜索无结果")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())