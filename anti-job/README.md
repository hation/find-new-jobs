# 🚀 anti-job

## 📋 项目概述

这是一个基于**夸克项目完整架构**创建的数据爬取项目，包含三个完整层次：

### **1. 📚 知识层**（文档模板 + 记忆系统）
- ✅ 10个核心文档模板
- ✅ 完整的记忆系统
- ✅ 检查清单和教训记录

### **2. 🔧 框架层**（业务实现框架）
- ✅ 智能爬取器选择器 ()
- ✅ 统一爬取器入口 ()
- ✅ 数据导出框架 ()

### **3. ⚙️ 配置层**（配置模板 + 环境配置）
- ✅ 项目配置模板
- ✅ API认证配置
- ✅ 浏览器配置
- ✅ 环境配置示例

## 🎯 立即开始

### 1. 环境准备
```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装浏览器驱动（如果需要）
python -m playwright install
```

### 2. 配置项目
```bash
# 复制环境配置
cp config/.env.example config/.env

# 编辑配置文件
vim config/.env
# 设置你的API密钥、浏览器配置等

# 配置API认证
vim config/api_auth.json
# 设置API认证信息
```

### 3. 填写业务信息
```bash
# 编辑核心业务信息
vim memory-system/CORE_BUSINESS_INFO.md
# 填写业务目标、数据需求、成功标准
```

### 4. 验证架构
```bash
# 运行完整架构验证
python scripts/validate_complete_architecture.py

# 或使用启动脚本
./start_complete_project.sh
```

## 📁 完整架构结构

```
anti-job/
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

## 🔧 业务框架使用指南

### 智能爬取器选择器
```python
from src.framework.smart_crawler_selector import SmartCrawlerSelector

class YourCompanyCrawler(SmartCrawlerSelector):
    """你的公司爬取器"""
    
    def _initialize_primary_crawler(self):
        # 实现你的API爬取器
        pass
    
    def _initialize_fallback_crawler(self):
        # 实现你的浏览器爬取器
        pass
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

## 📚 核心文档说明

### 必须阅读的文档
1. **架构设计** (`docs/ARCHITECTURE.md`) - 理解系统设计原则
2. **检查清单** (`docs/CHECKLIST.md`) - 53项标准检查，防止犯错
3. **快速开始** (`docs/QUICK_START.md`) - 一步步开始项目
4. **业务知识** (`docs/BUSINESS_KNOWLEDGE_SYSTEM.md`) - 业务知识体系
5. **模板使用** (`docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md`) - 如何使用这些模板

### 必须填写的文档
1. **核心业务信息** (`memory-system/CORE_BUSINESS_INFO.md`) - 明确业务目标
2. **每日记忆** (`memory-system/DAILY_MEMORY_TEMPLATE.md`) - 记录每日工作
3. **教训记录** (`docs/LESSONS_LEARNED.md`) - 记录问题和解决方案

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
**创建时间**: 2026-05-22 11:16:57
**模板版本**: v1.0.0
**迁移模式**: 完整架构迁移
**祝你项目顺利！** 🚀
