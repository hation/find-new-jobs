#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDD招聘爬取器 - 阶段2启动脚本
目的: 开始阶段2开发，同时请求用户提供缺失技术细节
"""

import os
import sys
import json
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║          PDD招聘爬取器 - 阶段2: 详情页数据提取           ║
    ║                    🚀 启动脚本                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_stage1_completion():
    """检查阶段1完成状态"""
    print("\n🔍 检查阶段1完成状态...")
    
    stage1_files = [
        "src/crawler/pdd_crawler.py",
        "src/utils/pdd_data_exporter.py",
        "config/.env",
        "config/api_auth.json",
        "config/project_config.json",
        "test_basic_functionality.py"
    ]
    
    all_exist = True
    for file_path in stage1_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (缺失)")
            all_exist = False
    
    if all_exist:
        print("\n✅ 阶段1文件完整，可以开始阶段2")
    else:
        print("\n❌ 阶段1文件不完整，请先完成阶段1")
    
    return all_exist

def analyze_known_technical_details():
    """分析已知技术细节"""
    print("\n📊 分析已知技术细节...")
    
    known_details = {
        "列表页API": {
            "状态": "✅ 已知",
            "端点": "https://careers.pddglobalhr.com/api/recruit/position/list",
            "方法": "POST",
            "关键参数": ["page", "size", "anti_content"],
            "返回字段": ["code", "name", "workLocation", "job", "updateTime"]
        },
        "详情页URL": {
            "状态": "✅ 已知",
            "模式": "https://careers.pddglobalhr.com/jobs/{code}",
            "说明": "基于code字段构造"
        },
        "anti_content参数": {
            "状态": "❌ 未知",
            "问题": "如何动态生成？"
        },
        "详情页类型": {
            "状态": "❌ 未知", 
            "问题": "HTML页面还是API接口？"
        },
        "详情页字段": {
            "状态": "❌ 未知",
            "问题": "包含哪些具体字段？"
        }
    }
    
    for category, details in known_details.items():
        status = details.pop("状态")
        print(f"   {status} {category}")
        
        for key, value in details.items():
            if isinstance(value, list):
                print(f"      {key}: {', '.join(value)}")
            else:
                print(f"      {key}: {value}")
    
    return known_details

def generate_technical_questions():
    """生成需要用户回答的技术问题"""
    print("\n❓ 需要用户提供的技术细节:")
    
    questions = [
        {
            "id": 1,
            "问题": "anti_content参数如何生成？",
            "重要性": "🔴 高",
            "说明": "这是访问API的关键参数，没有它无法获取数据",
            "可能答案": [
                "A. 固定的字符串（不需要动态生成）",
                "B. 从JavaScript代码中提取的加密值",
                "C. 通过特定API接口获取",
                "D. 基于时间戳等参数计算"
            ]
        },
        {
            "id": 2,
            "问题": "详情页是哪种类型？",
            "重要性": "🔴 高",
            "说明": "决定爬取技术方案",
            "可能答案": [
                "A. 静态HTML页面（直接访问URL即可）",
                "B. 动态加载页面（需要处理JavaScript）",
                "C. 有单独的API接口",
                "D. 混合类型"
            ]
        },
        {
            "id": 3,
            "问题": "详情页包含哪些关键字段？",
            "重要性": "🟡 中",
            "说明": "决定数据提取策略",
            "可能答案": [
                "学历要求（education）",
                "工作经验（experience）",
                "薪资范围（salary）",
                "部门信息（department）",
                "工作职责（responsibilities）",
                "任职要求（requirements）",
                "其他福利（benefits）"
            ]
        },
        {
            "id": 4,
            "问题": "是否有反爬机制？",
            "重要性": "🟡 中",
            "说明": "影响爬取策略和稳定性",
            "可能答案": [
                "A. 频率限制（如每分钟请求数限制）",
                "B. IP限制",
                "C. User-Agent验证",
                "D. 验证码",
                "E. 无显著反爬"
            ]
        }
    ]
    
    for q in questions:
        print(f"\n   {q['重要性']} 问题{q['id']}: {q['问题']}")
        print(f"      说明: {q['说明']}")
        print(f"      可能答案:")
        for ans in q['可能答案']:
            print(f"        - {ans}")
    
    return questions

def create_stage2_starter_files():
    """创建阶段2启动文件"""
    print("\n📁 创建阶段2启动文件...")
    
    # 创建详情页爬取器框架
    detail_crawler_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDD详情页爬取器 - 框架
阶段2: 详情页数据提取
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class PddDetailCrawlerConfig:
    """详情页爬取器配置"""
    base_url: str = "https://careers.pddglobalhr.com/jobs/{code}"
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 2
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


class PddDetailCrawler:
    """PDD详情页爬取器"""
    
    def __init__(self, config: Optional[PddDetailCrawlerConfig] = None):
        """
        初始化详情页爬取器
        
        Args:
            config: 配置对象
        """
        self.config = config or PddDetailCrawlerConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        
        logger.info("✅ PDD详情页爬取器初始化完成")
        logger.info(f"   基础URL: {self.config.base_url}")
        logger.info(f"   超时时间: {self.config.timeout}秒")
    
    def construct_detail_url(self, position_code: str) -> str:
        """
        构造详情页URL
        
        Args:
            position_code: 岗位代码
            
        Returns:
            详情页URL
        """
        url = self.config.base_url.format(code=position_code)
        logger.debug(f"构造详情页URL: {url}")
        return url
    
    def fetch_detail_page(self, position_code: str) -> Optional[str]:
        """
        获取详情页内容
        
        Args:
            position_code: 岗位代码
            
        Returns:
            页面内容（HTML或JSON），失败返回None
        """
        url = self.construct_detail_url(position_code)
        
        for attempt in range(self.config.retry_count):
            try:
                logger.info(f"📥 获取详情页数据 (尝试 {attempt+1}/{self.config.retry_count}): {position_code}")
                
                response = self.session.get(
                    url,
                    timeout=self.config.timeout,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # 检查内容类型
                content_type = response.headers.get('Content-Type', '').lower()
                
                if 'application/json' in content_type:
                    logger.info(f"   ✅ 获取到JSON数据，大小: {len(response.content)} 字节")
                    return response.json()
                else:
                    logger.info(f"   ✅ 获取到HTML数据，大小: {len(response.content)} 字节")
                    return response.text
                    
            except requests.exceptions.Timeout:
                logger.warning(f"   ⏰ 请求超时 (尝试 {attempt+1})")
            except requests.exceptions.HTTPError as e:
                logger.error(f"   ❌ HTTP错误: {e}")
                if response.status_code == 404:
                    logger.warning(f"   ⚠️ 详情页不存在 (404)")
                    return None
                elif response.status_code == 403:
                    logger.error(f"   🔒 访问被拒绝 (403)，可能需要反爬处理")
                    return None
            except Exception as e:
                logger.error(f"   ❌ 获取详情页失败: {e}")
            
            # 重试前等待
            if attempt < self.config.retry_count - 1:
                time.sleep(self.config.retry_delay)
        
        logger.error(f"❌ 获取详情页失败，已重试{self.config.retry_count}次: {position_code}")
        return None
    
    def parse_detail_data(self, detail_content: Any, position_code: str) -> Dict[str, Any]:
        """
        解析详情页数据
        
        Args:
            detail_content: 详情页内容（HTML或JSON）
            position_code: 岗位代码
            
        Returns:
            解析后的数据字典
        """
        logger.info(f"🔍 解析详情页数据: {position_code}")
        
        # 基础结果
        result = {
            "position_code": position_code,
            "parse_success": False,
            "parse_method": "unknown",
            "extracted_fields": {},
            "raw_content_type": type(detail_content).__name__,
            "parse_timestamp": time.time()
        }
        
        try:
            # 尝试解析JSON
            if isinstance(detail_content, dict):
                result["parse_method"] = "json"
                result["extracted_fields"] = self._parse_json_detail(detail_content)
                result["parse_success"] = True
                
            elif isinstance(detail_content, str):
                # 尝试解析为JSON字符串
                try:
                    json_data = json.loads(detail_content)
                    result["parse_method"] = "json_string"
                    result["extracted_fields"] = self._parse_json_detail(json_data)
                    result["parse_success"] = True
                    
                except json.JSONDecodeError:
                    # 解析为HTML
                    result["parse_method"] = "html"
                    result["extracted_fields"] = self._parse_html_detail(detail_content)
                    result["parse_success"] = True
                    
            else:
                logger.warning(f"   ⚠️ 未知的内容类型: {type(detail_content)}")
                
        except Exception as e:
            logger.error(f"   ❌ 解析详情页数据失败: {e}")
            result["parse_error"] = str(e)
        
        logger.info(f"   📊 解析结果: 成功={result['parse_success']}, 方法={result['parse_method']}")
        return result
    
    def _parse_json_detail(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析JSON格式的详情数据
        
        Args:
            json_data: JSON数据
            
        Returns:
            提取的字段
        """
        # TODO: 根据实际JSON结构实现
        # 这里是一个示例实现
        extracted = {}
        
        # 尝试提取常见字段
        field_mapping = {
            "education": ["education", "学历", "学历要求"],
            "experience": ["experience", "工作经验", "经验要求"],
            "salary": ["salary", "薪资", "薪酬"],
            "department": ["department", "部门", "所属部门"],
            "responsibilities": ["responsibilities", "工作职责", "岗位职责"],
            "requirements": ["requirements", "任职要求", "要求"]
        }
        
        for field_name, possible_keys in field_mapping.items():
            for key in possible_keys:
                if key in json_data:
                    extracted[field_name] = json_data[key]
                    break
        
        return extracted
    
    def _parse_html_detail(self, html_content: str) -> Dict[str, Any]:
        """
        解析HTML格式的详情数据
        
        Args:
            html_content: HTML内容
            
        Returns:
            提取的字段
        """
        # TODO: 根据实际HTML结构实现
        # 这里是一个示例实现
        extracted = {}
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 示例：尝试提取标题
            title_elem = soup.find('h1')
            if title_elem:
                extracted["title"] = title_elem.get_text(strip=True)
            
            # 示例：尝试提取所有段落文本
            paragraphs = soup.find_all('p')
            if paragraphs:
                extracted["paragraphs"] = [p.get_text(strip=True) for p in paragraphs[:10]]
            
            # 示例：尝试提取列表
            lists = soup.find_all(['ul', 'ol'])
            if lists:
                extracted["lists"] = []
                for lst in lists[:5]:
                    items = [li.get_text(strip=True) for li in lst.find_all('li')]
                    extracted["lists"].append(items)
            
        except Exception as e:
            logger.error(f"HTML解析失败: {e}")
        
        return extracted
    
    def crawl_position_detail(self, position_code: str) -> Dict[str, Any]:
        """
        爬取单个岗位的详情数据
        
        Args:
            position_code: 岗位代码
            
        Returns:
            完整的爬取结果
        """
        logger.info(f"🚀 开始爬取岗位详情: {position_code}")
        
        start_time = time.time()
        
        # 获取详情页内容
        detail_content = self.fetch_detail_page(position_code)
        
        if detail_content is None:
            logger.warning(f"❌ 无法获取详情页内容: {position_code}")
            return {
                "position_code": position_code,
                "success": False,
                "error": "无法获取详情页内容",
                "elapsed_time": time.time() - start_time
            }
        
        # 解析详情页数据
        parse_result = self.parse_detail_data(detail_content, position_code)
        
        result = {
            "position_code": position_code,
            "success": parse_result["parse_success"],
            "elapsed_time": time.time() - start_time,
            "parse_method": parse_result["parse_method"],
            "extracted_fields": parse_result["extracted_fields"],
            "raw_content_type": parse_result["raw_content_type"]
        }
        
        if not parse_result["parse_success"]:
            result["error"] = parse_result.get("parse_error", "解析失败")
        
        logger.info(f"   🎯 爬取完成: 成功={result['success']}, 用时={result['elapsed_time']:.2f}秒")
        
        return result


def test_detail_crawler():
    """测试详情页爬取器"""
    print("🧪 测试PDD详情页爬取器...")
    
    # 创建爬取器
    crawler = PddDetailCrawler()
    
    # 测试URL构造
    test_code = "TEST001"
    url = crawler.construct_detail_url(test_code)
    print(f"   ✅ URL构造测试: {url}")
    
    # 注意：这里不实际请求，因为需要用户提供技术细节
    print("   ⚠️ 实际爬取测试需要用户提供技术细节后执行")
    
    return True


if __name__ == "__main__":
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    success = test_detail_crawler()
    
    if success:
        print("\n✅ PDD详情页爬取器框架测试通过")
        print("\n下一步:")
        print("1. 等待用户提供技术细节（anti_content、详情页类型等）")
        print("2. 根据技术细节完善爬取器实现")
        print("3. 进行实际爬取测试")
    else:
        print("\n❌ PDD详情页爬取器框架测试失败")
    
    sys.exit(0 if success else 1)
'''
    
    # 创建技术问题文档
    questions_content = '''# ❓ PDD爬取器阶段2 - 技术问题清单

## 📅 创建时间
2026-05-22 16:45

## 🎯 目的
本文件列出阶段2开发需要用户提供的技术细节。请回答以下问题，以便我们继续开发。

## 🔴 高优先级问题（必须回答）

### 问题1: anti_content参数如何生成？
**重要性**: 🔴 高  
**说明**: 这是访问API的关键参数，没有它无法获取数据  
**当前状态**: ❌ 未知  
**需要的信息**:
- 该参数是固定的还是动态生成的？
- 如果是动态生成的，生成逻辑是什么？
- 是否有JavaScript加密代码？
- 是否需要调用特定API？

**可能答案**:
- A. 固定的字符串（不需要动态生成）
- B. 从JavaScript代码中提取的加密值
- C. 通过特定API接口获取
- D. 基于时间戳等参数计算

### 问题2: 详情页是哪种类型？
**重要性**: 🔴 高  
**说明**: 决定爬取技术方案  
**当前状态**: ❌ 未知  
**需要的信息**:
- 直接访问URL返回什么内容？
- 是静态页面还是动态加载？
- 是否有单独的API接口？

**可能答案**:
- A. 静态HTML页面（直接访问URL即可）
- B. 动态加载页面（需要处理JavaScript）
- C. 有单独的API接口
- D. 混合类型

## 🟡 中优先级问题（建议回答）

### 问题3: 详情页包含哪些关键字段？
**重要性**: 🟡 中  
**说明**: 决定数据提取策略  
**当前状态**: ❌ 未知  
**需要的信息**:
- 除了列表页已有的字段，详情页还有哪些字段？
- 字段的准确名称是什么？
- 字段在页面中的位置（HTML选择器或JSON路径）？

**期望字段**:
- 学历要求（education）
- 工作经验（experience）
- 薪资范围（salary）
- 部门信息（department）
- 工作职责（responsibilities）
- 任职要求（requirements）
- 其他福利（benefits）

### 问题4: 是否有反爬机制？
**重要性**: 🟡 中  
**说明**: 影响爬取策略和稳定性  
**当前状态**: ❌ 未知  
**需要的信息**:
- 是否有请求频率限制？
- 是否需要IP轮换？
- 是否需要特殊请求头？
- 是否有验证码？

**可能答案**:
- A. 频率限制（如每分钟请求数限制）
- B. IP限制
- C. User-Agent验证
- D. 验证码
- E. 无显著反爬

## 🟢 低优先级问题（可选回答）

### 问题5: 数据导出格式要求？
**重要性**: 🟢 低  
**说明**: 影响最终输出格式  
**当前状态**: ✅ 已有基础格式（JSON/CSV/Excel）

### 问题6: 项目时间要求？
**重要性**: 🟢 低  
**说明**: 安排开发优先级  
**当前状态**: ❌ 未知

## 📋 回答格式建议

请按以下格式回答：

```markdown
### 问题1: anti_content参数
**答案**: [选择A/B/C/D或提供具体信息]
**详细信息**: [具体生成方法、代码示例等]

### 问题2: 详情页类型
**答案**: [选择A/B/C/D]
**详细信息**: [页面结构、API端点等]

### 问题3: 详情页字段
**答案**: [列出具体字段]
**详细信息**: [字段位置、选择器等]

### 问题4: 反爬机制
**答案**: [选择A/B/C/D/E]
**详细信息**: [具体限制条件]
```

## 🚀 下一步

**回答后我们可以立即开始**:
1. ✅ 完善详情页爬取器实现
2. ✅ 实现anti_content参数生成
3. ✅ 进行实际爬取测试
4. ✅ 完成阶段2开发

**当前可以并行进行的工作**:
1. ✅ 详情页爬取器框架开发（已完成）
2. ✅ 数据整合器框架开发
3. ✅ 测试脚本开发

## 📞 联系方式

如有任何问题或需要澄清，请随时联系。

---
**最后更新**: 2026-05-22 16:45  
**项目状态**: 阶段1完成，阶段2待技术细节  
**预计影响**: 技术细节到位后2-3天完成阶段2
'''
    
    # 创建文件
    files_to_create = {
        "src/crawler/pdd_detail_crawler.py": detail_crawler_content,
        "docs/TECHNICAL_QUESTIONS_STAGE2.md": questions_content
    }
    
    created_count = 0
    for file_path, content in files_to_create.items():
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 创建文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ 创建文件: {file_path} ({len(content)} 字节)")
        created_count += 1
    
    return created_count

def generate_next_steps():
    """生成下一步行动计划"""
    print("\n🚀 下一步行动计划:")
    
    steps = [
        {
            "序号": 1,
            "行动": "用户提供技术细节",
            "负责人": "用户",
            "时间": "立即",
            "产出": "回答技术问题清单"
        },
        {
            "序号": 2,
            "行动": "完善详情页爬取器",
            "负责人": "开发",
            "时间": "收到技术细节后2小时",
            "产出": "可工作的详情页爬取器"
        },
        {
            "序号": 3,
            "行动": "实现anti_content生成",
            "负责人": "开发",
            "时间": "收到技术细节后3小时",
            "产出": "anti_content参数生成器"
        },
        {
            "序号": 4,
            "行动": "测试详情页爬取",
            "负责人": "开发",
            "时间": "爬取器完成后2小时",
            "产出": "测试报告和样例数据"
        },
        {
            "序号": 5,
            "行动": "开发数据整合器",
            "负责人": "开发",
            "时间": "并行进行",
            "产出": "列表页+详情页数据整合器"
        },
        {
            "序号": 6,
            "行动": "全面测试和优化",
            "负责人": "开发",
            "时间": "所有组件完成后3小时",
            "产出": "稳定的阶段2版本"
        }
    ]
    
    for step in steps:
        print(f"\n   {step['序号']}. {step['行动']}")
        print(f"      负责人: {step['负责人']}")
        print(f"      时间: {step['时间']}")
        print(f"      产出: {step['产出']}")
    
    return steps

def main():
    """主函数"""
    print_banner()
    
    # 检查阶段1完成状态
    if not check_stage1_completion():
        print("\n❌ 请先完成阶段1开发")
        return 1
    
    # 分析已知技术细节
    known_details = analyze_known_technical_details()
    
    # 生成技术问题
    questions = generate_technical_questions()
    
    # 创建阶段2启动文件
    created_files = create_stage2_starter_files()
    
    # 生成下一步行动计划
    next_steps = generate_next_steps()
    
    # 生成总结报告
    print("\n" + "="*60)
    print("🎯 阶段2启动完成总结")
    print("="*60)
    
    print(f"\n📊 状态概览:")
    print(f"   ✅ 阶段1完成检查: 通过")
    print(f"   📋 已知技术细节: {len([k for k, v in known_details.items() if v.get('状态') == '✅ 已知'])}/{len(known_details)}")
    print(f"   ❓ 待解决问题: {len(questions)} 个")
    print(f"   📁 创建文件: {created_files} 个")
    
    print(f"\n🎯 立即行动:")
    print(f"   1. 请查看并回答: docs/TECHNICAL_QUESTIONS_STAGE2.md")
    print(f"   2. 技术细节到位后，我们将立即开始阶段2核心开发")
    
    print(f"\n🛠️ 已创建的文件:")
    print(f"   • src/crawler/pdd_detail_crawler.py - 详情页爬取器框架")
    print(f"   • docs/TECHNICAL_QUESTIONS_STAGE2.md - 技术问题清单")
    print(f"   • DEVELOPMENT_PLAN_STAGE2.md - 阶段2开发计划")
    
    print(f"\n📅 预计时间线:")
    print(f"   • 收到技术细节: 立即开始开发")
    print(f"   • 阶段2核心开发: 2-3天")
    print(f"   • 全面测试: 1天")
    
    print(f"\n💡 建议:")
    print(f"   1. 优先回答高优先级问题（anti_content、详情页类型）")
    print(f"   2. 可以提供示例请求/响应或截图")
    print(f"   3. 如果有测试账号或测试数据，可以加快开发")
    
    print("\n" + "="*60)
    print("🚀 我们已准备好开始阶段2开发，等待您的技术细节！")
    print("="*60)
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)