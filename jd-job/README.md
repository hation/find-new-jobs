# 🚀 京东招聘数据爬取项目

## 📋 项目概述

这是一个基于**夸克项目完整架构**创建的**京东招聘数据爬取项目**，专门用于爬取京东（JD.com）招聘网站的岗位信息。

### **1. 📚 知识层**（文档模板 + 记忆系统）
- ✅ 10个核心文档模板，已根据京东项目定制
- ✅ 完整的记忆系统，包含京东业务信息
- ✅ 检查清单和教训记录，防止重复犯错

### **2. 🔧 框架层**（业务实现框架）
- ✅ 智能爬取器选择器 (`JDJobCrawler`)
- ✅ 统一爬取器入口 (`jd_crawler.py`)
- ✅ 数据导出框架 (`DataExporter`)

### **3. ⚙️ 配置层**（京东专用配置）
- ✅ 京东API认证配置 (`api_auth.json`)
- ✅ 京东环境配置 (`.env`)
- ✅ 京东浏览器配置 (`browser_config.json`)

## 🎯 立即开始爬取京东招聘数据

### 1. 环境准备
```bash
# 安装Python依赖（已包含京东爬取所需的所有包）
pip install -r requirements.txt

# 安装浏览器驱动（备用方案需要）
python3 -m playwright install
```

### 2. 启动京东爬虫
```bash
# 使用专用启动脚本（推荐）
./start_jd_crawler.sh

# 或直接运行爬虫
python3 src/jd_crawler.py --test --format excel
```

### 3. 测试项目
```bash
# 运行完整测试
python3 test_jd_crawler.py

# 验证架构
python3 scripts/validate_complete_architecture.py
```

### 4. 开始爬取
```bash
# 测试模式（只爬取1页）
python3 src/jd_crawler.py --test --format excel

# 完整模式（爬取10页）
python3 src/jd_crawler.py --pages 10 --format excel

# 自定义模式
python3 src/jd_crawler.py --pages 20 --format csv
```

## 📁 完整架构结构

```
jd-job/
├── 📚 知识层
│   ├── docs/                    # 10个核心文档模板
│   │   ├── ARCHITECTURE.md      # 架构设计
│   │   ├── CHECKLIST.md         # 检查清单（53项）
│   │   ├── LESSONS_LEARNED.md   # 教训记录
│   │   ├── QUICK_START.md       # 快速开始
│   │   └── ... (共10个文档)
│   └── memory-system/           # 记忆系统
│       ├── CORE_BUSINESS_INFO.md # 核心业务信息
│       ├── DAILY_MEMORY_TEMPLATE.md # 每日记忆模板
│       └── MEMORY_SYSTEM_GUIDE.md # 记忆系统指南
│
├── 🔧 框架层
│   └── src/framework/           # 业务实现框架
│       ├── smart_crawler_selector.py  # 智能爬取器选择器
│       ├── unified_crawler_entry.py   # 统一爬取器入口
│       ├── data_exporter.py           # 数据导出框架
│       └── main.py                    # 主程序入口
│
├── ⚙️ 配置层
│   └── config/                  # 配置模板
│       ├── project_config.json  # 项目配置
│       ├── api_auth.json        # API认证配置
│       ├── browser_config.json  # 浏览器配置
│       └── .env.example         # 环境配置示例
│
├── 🛠️ 工具层
│   ├── scripts/                 # 工具脚本
│   ├── tests/                   # 测试代码
│   ├── start_complete_project.sh # 完整启动脚本
│   └── requirements.txt         # Python依赖
│
├── 📊 数据层
│   ├── data/                    # 数据目录
│   ├── output/                  # 输出目录
│   └── logs/                    # 日志目录
│
└── 📄 项目文件
    ├── README.md                # 本文件
    ├── .gitignore               # Git忽略文件
    └── ... (其他项目文件)
```

## 🔧 京东爬取器使用指南

### 京东专用爬取器
```python
from src.jd_crawler import JDJobCrawler

# 创建京东爬取器
crawler = JDJobCrawler()

# 爬取数据
jobs = crawler.crawl_all_jobs(max_pages=10)

# 保存数据
file_path = crawler.save_jobs_to_file(jobs, format="excel")
print(f"数据已保存到: {file_path}")
```

### 命令行使用
```bash
# 查看帮助
python3 src/jd_crawler.py --help

# 爬取5页数据，输出为Excel
python3 src/jd_crawler.py --pages 5 --format excel

# 爬取10页数据，输出为CSV
python3 src/jd_crawler.py --pages 10 --format csv

# 测试模式（只爬取1页）
python3 src/jd_crawler.py --test --format json
```

### 统一爬取器入口
```python
from src.framework.unified_crawler_entry import UnifiedCrawlerEntry

entry = UnifiedCrawlerEntry(company_name="新公司")
# 支持多种运行模式：api, browser, smart, optimized, status, export, check
```

### 数据导出框架
```python
from src.framework.data_exporter import DataExporter

exporter = DataExporter()
# 支持Excel、CSV、JSON格式导出
```

## 📚 京东项目核心文档

### 已配置的文档
1. **京东业务信息** (`memory-system/CORE_BUSINESS_INFO.md`) - 京东项目目标、数据需求
2. **API认证配置** (`config/api_auth.json`) - 京东API端点、认证信息、请求参数
3. **环境配置** (`config/.env`) - 京东专用环境变量
4. **检查清单** (`docs/CHECKLIST.md`) - 53项标准检查，防止犯错

### 京东专用文件
1. **京东爬取器** (`src/jd_crawler.py`) - 基于夸克框架的京东爬取器
2. **启动脚本** (`start_jd_crawler.sh`) - 京东项目专用启动脚本
3. **测试脚本** (`test_jd_crawler.py`) - 京东爬取器测试脚本

### 数据字段说明
京东爬取器提取以下字段：
- `position_id`: 岗位ID
- `position_name`: 岗位名称
- `work_location`: 工作地点
- `department`: 部门名称
- `education_requirement`: 学历要求
- `work_experience`: 工作经验
- `position_description`: 岗位描述
- `position_requirements`: 任职要求
- `publish_date`: 发布日期
- `company_info`: 公司/部门信息
- `recruitment_number`: 招聘编号
- `job_type`: 岗位类型

## 🔄 工作流程

### 开发流程
1. **明确业务目标**：填写 `memory-system/CORE_BUSINESS_INFO.md`
2. **执行环境检查**：按照 `docs/CHECKLIST.md` 逐项检查
3. **配置项目**：设置 `config/` 目录中的配置文件
4. **开发实现**：基于 `src/framework/` 中的框架进行开发
5. **测试验证**：运行 `tests/` 中的测试
6. **记录经验**：在 `docs/LESSONS_LEARNED.md` 中记录

### 执行流程
1. **环境验证**：运行检查清单
2. **数据爬取**：使用智能爬取器
3. **数据处理**：使用数据导出框架
4. **质量检查**：验证数据完整性
5. **生成报告**：记录执行结果和问题

## 🎯 基于夸克的核心经验

### 防错机制（必须遵守）
1. **永远相信页面显示**，不是URL参数
2. **每次操作前验证筛选状态**
3. **每个岗位提取后立即保存**
4. **使用检查清单防止重复犯错**

### 学习机制
1. **遇到问题立即记录**在教训文档
2. **分析根本原因**和制定解决方案
3. **更新检查清单**防止重复犯错
4. **定期回顾**和优化工作流程

### 质量保障
1. **12字段数据完整性**检查
2. **实时验证**和错误恢复
3. **多格式导出**支持不同需求
4. **完整日志**记录便于排查

## 📞 快速帮助

### 常见问题
1. **API认证失败**：检查 `config/api_auth.json`
2. **浏览器驱动问题**：运行 `python -m playwright install`
3. **数据不完整**：检查日志，查看缺失字段
4. **框架导入失败**：检查Python路径和依赖

### 脚本说明
- `./start_complete_project.sh` - 完整的启动脚本
- `python src/main.py` - 查看可用框架组件
- `python scripts/validate_complete_architecture.py` - 验证完整架构

### 文档参考
- 快速问题解决：`docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md`
- 完整知识体系：`docs/BUSINESS_KNOWLEDGE_SYSTEM.md`
- 业务流转图：`docs/BUSINESS_TEMPLATE_FLOW.md`

---

**项目基于夸克项目完整架构创建，包含知识层 + 框架层 + 配置层**
**创建时间**: 2026-05-22 15:40:09
**模板版本**: v1.0.0
**迁移模式**: 完整架构迁移
**祝你项目顺利！** 🚀
