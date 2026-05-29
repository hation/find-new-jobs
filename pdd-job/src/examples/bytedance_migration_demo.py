#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移演示脚本
展示如何将夸克方案迁移到"字节跳动"招聘系统
"""

import os
import shutil
from pathlib import Path

def demo_manual_migration():
    """手动迁移演示"""
    
    # 1. 创建目标目录
    target_dir = "bytedance_recruitment_scraper_demo"
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    print("🚀 演示迁移夸克方案到字节跳动招聘系统")
    print("=" * 60)
    
    # 2. 创建目录结构
    print("📁 创建目录结构...")
    dirs = [
        target_dir,
        f"{target_dir}/scripts",
        f"{target_dir}/config", 
        f"{target_dir}/output",
        f"{target_dir}/other",
    ]
    
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"   ✅ 创建: {d}")
    
    # 3. 复制核心框架文件
    print("\n📋 复制核心框架文件...")
    
    # 统一入口（需要重命名）
    shutil.copy("quark_crawler.py", f"{target_dir}/bytedance_crawler.py")
    print("   ✅ 复制: quark_crawler.py → bytedance_crawler.py")
    
    # 数据处理工具（直接复用）
    shutil.copy("merge_to_excel.py", f"{target_dir}/merge_to_excel.py")
    shutil.copy("detailed_data_check.py", f"{target_dir}/detailed_data_check.py")
    print("   ✅ 复制: merge_to_excel.py")
    print("   ✅ 复制: detailed_data_check.py")
    
    # 4. 复制智能选择器（需要少量修改）
    shutil.copy("scripts/crawler_selector_optimized.py", 
                f"{target_dir}/scripts/crawler_selector_optimized.py")
    print("   ✅ 复制: crawler_selector_optimized.py")
    
    # 5. 创建字节跳动专用的API爬取器模板
    print("\n🔧 创建字节跳动API爬取器模板...")
    
    api_template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字节跳动招聘API爬取器
基于夸克方案迁移
"""

import time
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ByteDanceApiCrawlerConfigurable:
    """字节跳动招聘API爬取器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化字节跳动API爬取器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置文件
        self.config_path = config_path or "config/api_auth.json"
        self.config = self._load_config()
        
        if not self.config:
            raise ValueError(f"无法加载配置文件: {self.config_path}")
        
        # TODO: 更新为字节跳动的API端点
        self.api_url = self.config.get("api_endpoint", "https://jobs.bytedance.com/api/positions")
        
        # TODO: 更新为字节跳动的认证信息
        self.csrf_token = self.config.get("authentication", {}).get("csrf_token", "")
        self.cookies = self.config.get("authentication", {}).get("cookies", {})
        self.headers = self.config.get("authentication", {}).get("headers", {})
        
        # TODO: 更新为字节跳动的请求参数
        self.base_params = {
            "page": 1,          # 字节跳动的页码参数
            "page_size": 10,    # 字节跳动的页大小参数
            "category": "",     # 字节跳动的筛选类别
            "location": "",     # 字节跳动的工作地点
            "keyword": ""       # 字节跳动的关键词搜索
        }
        
        # 输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"output/bytedance_api_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"🎯 字节跳动API爬取器初始化完成")
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """加载配置文件"""
        # 复用夸克的配置加载逻辑
        # TODO: 可能需要根据字节跳动的需求调整
        pass
    
    def fetch_page(self, page_index: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """
        获取单页数据
        
        Args:
            page_index: 页码（从1开始）
            page_size: 每页数量
            
        Returns:
            解析后的API响应数据
        """
        logger.info(f"📡 获取字节跳动第 {page_index} 页数据")
        
        # TODO: 实现字节跳动的API请求逻辑
        # 1. 构建请求参数
        # 2. 发送请求
        # 3. 解析响应
        # 4. 返回数据
        
        # 示例代码：
        try:
            # 构建字节跳动特定的请求参数
            params = {
                "page": page_index,
                "page_size": page_size,
                # TODO: 添加字节跳动的其他参数
            }
            
            # 发送请求到字节跳动API
            response = requests.post(
                f"{self.api_url}?csrf_token={self.csrf_token}",
                headers=self.headers,
                cookies=self.cookies,
                json=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # TODO: 根据字节跳动的响应结构解析数据
                # 字节跳动的响应可能类似：
                # {
                #   "code": 0,
                #   "message": "success",
                #   "data": {
                #     "total": 100,
                #     "list": [...],
                #     "page": 1,
                #     "page_size": 10
                #   }
                # }
                
                return self._parse_bytedance_response(data)
            else:
                logger.error(f"❌ 字节跳动API请求失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ 字节跳动API请求异常: {e}")
            return None
    
    def _parse_bytedance_response(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析字节跳动的API响应
        
        Args:
            raw_data: 原始响应数据
            
        Returns:
            标准化的岗位数据
        """
        # TODO: 根据字节跳动的实际响应结构实现
        
        positions = []
        if raw_data.get("code") == 0:
            data = raw_data.get("data", {})
            positions_list = data.get("list", [])
            
            for item in positions_list:
                # 映射字节跳动的字段到标准字段
                position = {
                    "position_id": item.get("id", ""),
                    "position_name": item.get("title", ""),      # 字节跳动的岗位标题字段
                    "work_location": item.get("city", ""),       # 字节跳动的城市字段
                    "department": item.get("department", ""),    # 字节跳动的部门字段
                    "education_requirement": item.get("education", ""),
                    "work_experience": item.get("experience", ""),
                    "salary_range": item.get("salary", ""),      # 字节跳动的薪资字段
                    "position_description": item.get("description", ""),
                    "position_requirements": item.get("requirement", ""),
                    "publish_date": item.get("publish_time", ""),
                    "application_deadline": item.get("deadline", ""),
                    "company_info": "字节跳动"
                }
                positions.append(position)
        
        return {
            "success": True,
            "positions": positions,
            "total_count": raw_data.get("data", {}).get("total", 0),
            "current_page": raw_data.get("data", {}).get("page", 1),
            "page_size": raw_data.get("data", {}).get("page_size", 10)
        }
    
    # ... 其他方法可以复用夸克的逻辑，但需要根据字节跳动的API调整

# 测试代码
if __name__ == "__main__":
    print("🧪 字节跳动API爬取器模板创建完成")
    print("下一步需要:")
    print("  1. 获取字节跳动的真实API端点")
    print("  2. 获取CSRF令牌和Cookie")
    print("  3. 分析API响应结构")
    print("  4. 实现字段映射")
'''
    
    with open(f"{target_dir}/scripts/bytedance_api_crawler.py", 'w', encoding='utf-8') as f:
        f.write(api_template)
    
    print("   ✅ 创建: bytedance_api_crawler.py")
    
    # 6. 创建配置文件模板
    print("\n⚙️ 创建字节跳动配置文件模板...")
    
    config_template = {
        "description": "字节跳动招聘API认证配置文件",
        "last_updated": "2026-05-20",
        "status": "pending_configuration",
        "company_name": "字节跳动",
        "notes": [
            "需要从字节跳动招聘网站获取真实的认证信息",
            "使用浏览器开发者工具分析API请求",
            "CSRF令牌和Cookie可能需要定期更新"
        ],
        "authentication": {
            "csrf_token": "TODO: 从字节跳动网站获取CSRF令牌",
            "cookies": {
                "SESSION": "TODO: 填写字节跳动会话Cookie",
                "XSRF-TOKEN": "TODO: 填写字节跳动XSRF令牌"
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Referer": "https://jobs.bytedance.com/experienced"
            }
        },
        "api_endpoint": "TODO: https://jobs.bytedance.com/api/positions",
        "parameters": {
            "page": 1,
            "page_size": 10,
            "categories": "技术类,产品类,运营类",
            "location": "北京,上海,深圳,杭州"
        }
    }
    
    with open(f"{target_dir}/config/api_auth.json", 'w', encoding='utf-8') as f:
        import json
        json.dump(config_template, f, ensure_ascii=False, indent=2)
    
    print("   ✅ 创建: config/api_auth.json")
    
    # 7. 创建迁移指南
    print("\n📝 创建迁移指南...")
    
    guide_content = """# 🚀 字节跳动招聘爬取器迁移指南

## ✅ 已完成的工作

### 框架迁移
1. ✅ 统一入口: `bytedance_crawler.py`
2. ✅ 数据处理: `merge_to_excel.py`, `detailed_data_check.py`
3. ✅ 智能选择器: `crawler_selector_optimized.py`
4. ✅ 目录结构: 完整的项目结构

### 定制模板
1. ✅ API爬取器模板: `bytedance_api_crawler.py`
2. ✅ 配置文件模板: `config/api_auth.json`

## 🛠️ 下一步定制工作

### 1. 获取字节跳动API信息
```bash
# 打开字节跳动招聘网站
# https://jobs.bytedance.com/experienced

# 使用浏览器开发者工具:
# 1. 打开Network标签
# 2. 筛选XHR请求
# 3. 找到岗位列表API请求
# 4. 记录请求URL、方法、参数、头部
```

### 2. 填写配置文件
```json
{
  "api_endpoint": "实际的字节跳动API地址",
  "csrf_token": "从请求参数或Cookie中获取",
  "cookies": {
    "SESSION": "实际的会话Cookie",
    "XSRF-TOKEN": "实际的XSRF令牌"
  }
}
```

### 3. 实现API解析逻辑
修改 `bytedance_api_crawler.py` 中的:
- `fetch_page()`: 实现字节跳动的API请求逻辑
- `_parse_bytedance_response()`: 解析字节跳动的响应结构

### 4. 测试和验证
```bash
# 测试API连接
python3 scripts/bytedance_api_crawler.py

# 测试统一入口
python3 bytedance_crawler.py --mode status
```

## 📋 字节跳动特定信息

### 可能的关键信息
- **API端点**: `https://jobs.bytedance.com/api/xxx`
- **认证方式**: CSRF + Cookie
- **分页参数**: `page`, `page_size`
- **筛选参数**: `category`, `location`, `keyword`

### 数据字段映射参考
| 标准字段 | 字节跳动字段 |
|---------|-------------|
| position_id | id |
| position_name | title |
| work_location | city |
| department | department |
| salary_range | salary |

## 🚀 快速开始

```bash
# 1. 进入项目目录
cd bytedance_recruitment_scraper_demo

# 2. 配置认证信息
vim config/api_auth.json

# 3. 实现API解析
vim scripts/bytedance_api_crawler.py

# 4. 测试运行
python3 bytedance_crawler.py --mode smart
```

## 📞 遇到问题?

### 常见问题
1. **API端点错误**: 检查字节跳动招聘网站的实际API
2. **认证失败**: 检查CSRF令牌和Cookie是否有效
3. **数据解析失败**: 检查字节跳动的响应结构

### 调试建议
```python
# 在bytedance_api_crawler.py中添加调试代码
import pprint
pprint.pprint(response.json())  # 打印完整响应
```

---

**完成标志**: 能够成功爬取字节跳动招聘网站的岗位数据
"""
    
    with open(f"{target_dir}/MIGRATION_GUIDE.md", 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("   ✅ 创建: MIGRATION_GUIDE.md")
    
    print("\n" + "=" * 60)
    print("🎉 字节跳动迁移演示完成!")
    print("=" * 60)
    print()
    print(f"📂 项目位置: {target_dir}")
    print("📋 包含文件:")
    print("  • bytedance_crawler.py          # 统一入口")
    print("  • scripts/bytedance_api_crawler.py # API爬取器模板")
    print("  • config/api_auth.json          # 配置文件模板")
    print("  • MIGRATION_GUIDE.md            # 迁移指南")
    print()
    print("🚀 下一步:")
    print("  1. 分析字节跳动招聘网站的API")
    print("  2. 填写配置文件中的TODO标记")
    print("  3. 实现API解析逻辑")
    print("  4. 测试和优化")
    print()
    print("💡 提示: 这个演示展示了完整的迁移流程")
    print("       实际迁移时，可以使用完整的迁移工具")

if __name__ == "__main__":
    demo_manual_migration()