#!/usr/bin/env python3
"""
可靠获取岗位描述的工具
使用search + show的方式，避免securityId问题
"""

import os
import sys
import json
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class RobustDescriptionFetcher:
    """可靠的岗位描述获取器"""
    
    def __init__(self, boss_path=None):
        self.boss_path = boss_path or self._find_boss_command()
        self.search_cache = {}  # 缓存搜索结果
    
    def _find_boss_command(self):
        """查找boss命令"""
        # 已知路径
        known_paths = [
            "/Users/xingan/Library/Python/3.12/bin/boss",
            f"{Path.home()}/Library/Python/3.12/bin/boss",
            f"{Path.home()}/.local/bin/boss",
            "/usr/local/bin/boss",
        ]
        
        for path in known_paths:
            if os.path.exists(path):
                return path
        
        # 使用which查找
        try:
            result = subprocess.run(
                ["which", "boss"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        
        return None
    
    def check_login(self):
        """检查登录状态"""
        if not self.boss_path:
            return False, "boss命令未找到"
        
        try:
            result = subprocess.run(
                [self.boss_path, "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = result.stdout
            if "已登录" in output and "search=ok" in output:
                return True, "登录成功"
            else:
                return False, output
                
        except Exception as e:
            return False, f"检查登录状态失败: {e}"
    
    def search_jobs(self, keyword: str, city: str = "深圳", page: int = 1) -> Dict:
        """搜索岗位"""
        cache_key = f"{keyword}_{city}_{page}"
        
        # 检查缓存
        if cache_key in self.search_cache:
            return self.search_cache[cache_key]
        
        print(f"🔍 搜索: {keyword} ({city}), 第{page}页")
        
        cmd = [
            self.boss_path,
            "search",
            keyword,
            "--city", city,
            "--page", str(page),
            "--json"  # 获取JSON格式
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    self.search_cache[cache_key] = data
                    return data
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"输出: {result.stdout[:500]}")
                    return {}
            else:
                print(f"❌ 搜索失败: {result.stderr[:200]}")
                return {}
                
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
            return {}
    
    def get_job_description_by_search(self, job_name: str, company_name: str = None) -> str:
        """通过搜索获取岗位描述"""
        # 提取关键词进行搜索
        keywords = self._extract_keywords(job_name)
        
        for keyword in keywords:
            print(f"🔍 使用关键词搜索: {keyword}")
            search_result = self.search_jobs(keyword, city="深圳", page=1)
            
            if search_result and 'data' in search_result and 'jobList' in search_result['data']:
                jobs = search_result['data']['jobList']
                
                # 查找匹配的岗位
                for idx, job in enumerate(jobs, 1):
                    found_job_name = job.get('jobName', '')
                    found_company = job.get('brandName', '')
                    
                    # 检查是否匹配
                    if (job_name in found_job_name or found_job_name in job_name or
                        (company_name and company_name in found_company)):
                        
                        print(f"✅ 找到匹配岗位: {found_job_name} ({found_company})")
                        
                        # 使用show命令获取详情
                        description = self._get_description_by_show(idx)
                        if description:
                            return description
                        else:
                            print(f"⚠️  无法获取描述，尝试下一个匹配")
            
            time.sleep(2)  # 避免请求过快
        
        return "未能通过搜索找到匹配的岗位"
    
    def _extract_keywords(self, job_name: str) -> List[str]:
        """从岗位名称中提取关键词"""
        # 移除特殊字符和数字
        cleaned = re.sub(r'[0-9【】（）()\[\]{}【】、，,\.。！!？?]', ' ', job_name)
        words = cleaned.split()
        
        # 提取有意义的关键词
        keywords = []
        for word in words:
            if len(word) >= 2:  # 至少2个字符
                # 过滤掉常见无意义词
                stop_words = ['试用期', '面试', '给结果', '资源', '接受', '经验']
                if word not in stop_words:
                    keywords.append(word)
        
        # 如果没有提取到关键词，使用原岗位名称
        if not keywords:
            keywords = [job_name[:20]]  # 使用前20个字符
        
        return keywords[:3]  # 最多3个关键词
    
    def _get_description_by_show(self, index: int) -> str:
        """使用show命令获取岗位详情"""
        print(f"  👁️  使用show命令查看第{index}个结果")
        
        cmd = [self.boss_path, "show", str(index)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                # 从输出中提取描述
                description = self._extract_description_from_show_output(result.stdout)
                return description if description else "已获取详情但未找到描述文本"
            else:
                print(f"  ❌ show命令失败: {result.stderr[:100]}")
                return f"获取失败: {result.stderr[:100]}"
                
        except Exception as e:
            print(f"  ❌ show命令异常: {e}")
            return f"获取异常: {e}"
    
    def _extract_description_from_show_output(self, output: str) -> str:
        """从show命令输出中提取描述"""
        if not output:
            return ""
        
        lines = output.split('\n')
        description_lines = []
        in_description = False
        
        # 查找描述开始
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 描述开始标记
            if any(marker in line for marker in ['岗位描述', '职位描述', '工作职责', '岗位职责', '工作内容', '职责描述']):
                in_description = True
                continue
            
            # 描述结束标记
            if in_description and any(marker in line for marker in ['任职要求', '职位要求', '薪资福利', '公司介绍', '联系方式', '---']):
                break
            
            # 收集描述内容
            if in_description and line:
                # 过滤掉太短或无意义的行
                if len(line) > 3 and not line.startswith('·') and not line.startswith('•'):
                    description_lines.append(line)
        
        if description_lines:
            return '\n'.join(description_lines)
        
        # 如果没有找到标准格式，查找大段文本
        paragraphs = [p.strip() for p in output.split('\n\n') if len(p.strip()) > 100]
        if paragraphs:
            # 优先选择包含中文的段落
            chinese_paragraphs = [p for p in paragraphs if re.search(r'[\u4e00-\u9fff]', p)]
            if chinese_paragraphs:
                return chinese_paragraphs[0][:1000]
            return paragraphs[0][:1000]
        
        return ""
    
    def get_descriptions_for_jobs(self, jobs_data: List[Dict], max_jobs: int = 10) -> List[Dict]:
        """为多个岗位获取描述"""
        print(f"🚀 开始为 {min(len(jobs_data), max_jobs)} 个岗位获取描述")
        print("=" * 50)
        
        # 检查登录状态
        logged_in, message = self.check_login()
        if not logged_in:
            print(f"❌ {message}")
            return jobs_data
        
        print(f"✅ {message}")
        
        results = []
        processed = 0
        
        for job in jobs_data[:max_jobs]:
            processed += 1
            job_name = job.get('jobName', f'岗位{processed}')
            company_name = job.get('brandName', '')
            
            print(f"\n📋 [{processed}/{max_jobs}] 处理: {job_name}")
            
            # 获取描述
            description = self.get_job_description_by_search(job_name, company_name)
            
            # 更新岗位数据
            job_with_desc = job.copy()
            job_with_desc['jobDescription'] = description
            
            results.append(job_with_desc)
            
            # 进度报告
            desc_len = len(description)
            if desc_len > 50 and "未能" not in description and "失败" not in description:
                print(f"  ✅ 获取成功 ({desc_len} 字符)")
                print(f"  📝 预览: {description[:100]}...")
            else:
                print(f"  ⚠️  获取结果: {description[:80]}")
            
            # 延迟避免请求过快
            if processed < max_jobs:
                time.sleep(3)
        
        print(f"\n🎉 完成！共处理 {processed} 个岗位")
        
        return results

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='可靠获取岗位描述')
    parser.add_argument('--input', '-i', required=True, help='输入JSON文件')
    parser.add_argument('--output', '-o', help='输出JSON文件')
    parser.add_argument('--max', type=int, default=10, help='最多处理多少个岗位')
    parser.add_argument('--keyword', '-k', help='搜索关键词（可选）')
    
    args = parser.parse_args()
    
    print("🚀 可靠岗位描述获取器")
    print("=" * 50)
    
    # 创建获取器
    fetcher = RobustDescriptionFetcher()
    
    # 加载数据
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取岗位列表
        if isinstance(data, list):
            jobs = data
        elif 'data' in data and 'jobList' in data['data']:
            jobs = data['data']['jobList']
        elif 'jobList' in data:
            jobs = data['jobList']
        else:
            jobs = []
        
        print(f"📁 加载 {len(jobs)} 个岗位数据")
        
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        return
    
    # 获取描述
    jobs_with_desc = fetcher.get_descriptions_for_jobs(jobs, max_jobs=args.max)
    
    # 保存结果
    output_file = args.output or f"岗位数据_带描述_{int(time.time())}.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(jobs_with_desc, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_file}")
        
        # 统计
        success_count = sum(1 for job in jobs_with_desc 
                          if job.get('jobDescription') and 
                          len(job['jobDescription']) > 50 and
                          "未能" not in job['jobDescription'] and
                          "失败" not in job['jobDescription'])
        
        print(f"📊 统计: {success_count}/{len(jobs_with_desc)} 个岗位成功获取描述")
        
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")

if __name__ == "__main__":
    main()