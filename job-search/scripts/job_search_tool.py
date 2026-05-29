#!/usr/bin/env python3
"""
BOSS直聘招聘信息查询工具 - 智能版
集成自动登录、搜索、导出、错误恢复等功能
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

class JobSearchTool:
    def __init__(self):
        self.boss_path = self._find_boss_command()
        self.config_dir = Path.home() / ".config" / "boss-cli"
        self.credential_file = self.config_dir / "credential.json"
        self.output_dir = Path.home() / "招聘数据"
        self.output_dir.mkdir(exist_ok=True)
    
    def _find_boss_command(self):
        """查找boss命令路径"""
        # 尝试常见路径
        possible_paths = [
            "/Users/xingan/Library/Python/3.12/bin/boss",
            os.path.expanduser("~/.local/bin/boss"),
            "/usr/local/bin/boss",
            "/opt/homebrew/bin/boss"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # 尝试在PATH中查找
        try:
            result = subprocess.run(["which", "boss"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "boss"  # 最后尝试直接使用boss
    
    def run_command(self, cmd, capture_output=True):
        """运行命令并处理输出"""
        print(f"🔧 执行: {cmd}")
        
        try:
            if capture_output:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(cmd, shell=True, timeout=30)
                result.stdout = ""
                result.stderr = ""
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "命令执行超时",
                "returncode": 1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": 1
            }
    
    def check_login_status(self):
        """检查登录状态"""
        print("🔍 检查登录状态...")
        result = self.run_command(f"{self.boss_path} status")
        
        if not result["success"]:
            print("❌ 无法执行status命令")
            return False
        
        output = result["stdout"]
        
        if "已登录" in output and "search=ok" in output:
            print("✅ 登录状态正常")
            return True
        elif "缺少关键Cookie: __zp_stoken__" in output:
            print("❌ 缺少关键cookie: __zp_stoken__")
            print("💡 必须通过浏览器登录获取此cookie")
            return False
        elif "环境异常" in output:
            print("❌ 环境异常，cookie可能已过期")
            return False
        else:
            print("⚠️ 未知登录状态")
            print(output)
            return False
    
    def login_with_browser(self, browser="chrome"):
        """通过浏览器登录"""
        print(f"🌐 通过{browser}浏览器登录...")
        
        # 先登出
        self.run_command(f"{self.boss_path} logout", capture_output=False)
        time.sleep(1)
        
        # 通过浏览器登录
        result = self.run_command(f"{self.boss_path} login --cookie-source {browser}")
        
        if result["success"]:
            print("✅ 登录成功")
            return True
        else:
            print("❌ 登录失败")
            if "No such option" in result["stderr"]:
                print("💡 你的boss-cli版本可能不支持--cookie-source参数")
                print("💡 请先手动在浏览器中登录BOSS直聘，然后运行: boss login")
            return False
    
    def search_jobs(self, keyword, city="深圳", **filters):
        """搜索岗位"""
        print(f"🔍 搜索 {city} 的 {keyword} 岗位...")
        
        # 构建命令
        cmd = f"{self.boss_path} search \"{keyword}\" --city {city}"
        
        # 添加筛选条件
        if "salary" in filters:
            cmd += f" --salary {filters['salary']}"
        if "exp" in filters:
            cmd += f" --exp {filters['exp']}"
        if "degree" in filters:
            cmd += f" --degree {filters['degree']}"
        if "industry" in filters:
            cmd += f" --industry {filters['industry']}"
        if "scale" in filters:
            cmd += f" --scale {filters['scale']}"
        if "page" in filters:
            cmd += f" --page {filters['page']}"
        
        # 添加输出格式
        if filters.get("format") == "json":
            cmd += " --json"
        elif filters.get("format") == "yaml":
            cmd += " --yaml"
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(f"✅ 搜索成功")
            return result["stdout"]
        else:
            print(f"❌ 搜索失败")
            if "环境异常" in result["stderr"]:
                print("💡 cookie可能已过期，需要重新登录")
            return None
    
    def export_jobs(self, keyword, city="深圳", format="json", output_file=None):
        """导出岗位数据"""
        print(f"📊 导出 {city} 的 {keyword} 岗位数据 ({format})...")
        
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{city}_{keyword}_岗位_{timestamp}.{format}"
            output_file = self.output_dir / filename
        
        cmd = f"{self.boss_path} export \"{keyword}\" --city {city} --format {format} -o {output_file}"
        
        result = self.run_command(cmd)
        
        if result["success"]:
            print(f"✅ 数据已导出到: {output_file}")
            return str(output_file)
        else:
            print(f"❌ 导出失败")
            if "环境异常" in result["stderr"]:
                print("💡 尝试使用搜索功能手动保存")
                data = self.search_jobs(keyword, city=city, format=format)
                if data:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(data)
                    print(f"✅ 已手动保存到: {output_file}")
                    return str(output_file)
            return None
    
    def search_multiple_keywords(self, keywords, city="深圳", format="json"):
        """批量搜索多个关键词"""
        results = {}
        
        for keyword in keywords:
            print(f"\n{'='*60}")
            print(f"搜索: {keyword}")
            
            # 检查登录状态
            if not self.check_login_status():
                print("尝试重新登录...")
                if not self.login_with_browser("chrome"):
                    print("登录失败，跳过此关键词")
                    continue
            
            # 搜索
            data = self.search_jobs(keyword, city=city, format=format)
            if data:
                # 保存文件
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{city}_{keyword}_岗位_{timestamp}.{format}"
                output_file = self.output_dir / filename
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(data)
                
                results[keyword] = str(output_file)
                print(f"✅ 已保存: {filename}")
            
            # 避免请求过快
            time.sleep(2)
        
        return results
    
    def analyze_jobs_data(self, json_file):
        """分析岗位数据"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取岗位列表
            if "zpData" in data and "jobList" in data["zpData"]:
                jobs = data["zpData"]["jobList"]
            elif "jobList" in data:
                jobs = data["jobList"]
            else:
                jobs = []
            
            print(f"\n📈 数据分析结果 ({len(jobs)} 个岗位)")
            print("=" * 60)
            
            # 按公司规模统计
            company_sizes = {}
            for job in jobs:
                size = job.get("brandScaleName", "未知")
                company_sizes[size] = company_sizes.get(size, 0) + 1
            
            if company_sizes:
                print("公司规模分布:")
                for size, count in sorted(company_sizes.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs) * 100
                    print(f"  {size}: {count}个 ({percentage:.1f}%)")
            
            # 按薪资统计
            salaries = {}
            for job in jobs:
                salary = job.get("salaryDesc", "面议")
                salaries[salary] = salaries.get(salary, 0) + 1
            
            if salaries:
                print("\n薪资分布:")
                for salary, count in sorted(salaries.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs) * 100
                    print(f"  {salary}: {count}个 ({percentage:.1f}%)")
            
            # 按经验要求统计
            experiences = {}
            for job in jobs:
                exp = job.get("jobExperience", "经验不限")
                experiences[exp] = experiences.get(exp, 0) + 1
            
            if experiences:
                print("\n经验要求分布:")
                for exp, count in sorted(experiences.items(), key=lambda x: x[1], reverse=True):
                    percentage = count / len(jobs) * 100
                    print(f"  {exp}: {count}个 ({percentage:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"❌ 分析数据失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 BOSS直聘招聘信息查询工具")
    print("=" * 60)
    
    tool = JobSearchTool()
    
    # 检查并确保登录状态
    if not tool.check_login_status():
        print("\n尝试自动登录...")
        if not tool.login_with_browser("chrome"):
            print("❌ 自动登录失败")
            print("\n💡 手动解决方案:")
            print("1. 在Chrome浏览器中登录 https://www.zhipin.com")
            print("2. 运行: boss login --cookie-source chrome")
            print("3. 运行: boss status 验证登录状态")
            return
    
    # 示例：搜索深圳AI岗位
    print("\n🎯 示例：搜索深圳AI相关岗位")
    
    keywords = ["AI", "人工智能", "机器学习", "深度学习"]
    
    results = tool.search_multiple_keywords(
        keywords=keywords,
        city="深圳",
        format="json"
    )
    
    print(f"\n{'='*60}")
    print("📊 搜索完成!")
    
    if results:
        print(f"成功搜索 {len(results)} 个关键词:")
        for keyword, filepath in results.items():
            print(f"  {keyword}: {filepath}")
            
            # 分析数据
            tool.analyze_jobs_data(filepath)
    
    print(f"\n💡 后续操作建议:")
    print("1. 查看具体数据文件")
    print("2. 使用Excel打开CSV文件")
    print("3. 定期检查登录状态: boss status")
    print("4. cookie过期时重新登录: boss login --cookie-source chrome")

if __name__ == "__main__":
    main()