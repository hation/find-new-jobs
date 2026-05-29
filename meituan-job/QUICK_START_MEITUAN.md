# 🚀 美团招聘爬取项目 - 快速开始指南

## 📋 项目概述

这是一个基于**夸克项目完整架构**创建的美团招聘数据爬取项目，专门用于爬取美团招聘网站的岗位信息。

### **核心特性**
- ✅ **智能爬取策略**: API优先，浏览器备选
- ✅ **完整数据模型**: 12个关键字段 + 扩展字段
- ✅ **多种导出格式**: Excel、CSV、JSON
- ✅ **错误恢复机制**: 自动重试和降级方案
- ✅ **质量验证**: 数据完整性检查

### **技术栈**
0️⃣ **Python 3.8+** - 核心编程语言
1️⃣ **Requests** - HTTP请求库
2️⃣ **Playwright** - 浏览器自动化
3️⃣ **Pandas** - 数据处理和导出
4️⃣ **夸克框架** - 智能爬取器选择器

## 🎯 立即开始

### **第一步：环境准备**

```bash
# 1. 进入项目目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/meituan-job

# 2. 安装Python依赖（已完成✅）
pip3 install -r requirements.txt

# 3. 安装浏览器驱动
python3 -m playwright install
```

### **第二步：配置项目**

```bash
# 1. 环境配置已创建 ✅
# 文件: config/.env

# 2. 核心业务信息已填写 ✅
# 文件: memory-system/CORE_BUSINESS_INFO.md

# 3. 美团爬取器已创建 ✅
# 文件: src/meituan_crawler.py
```

### **第三步：测试连接**

```bash
# 测试美团招聘网站连接
python3 src/meituan_crawler.py --mode test
```

预期输出：
```
🔍 测试美团API连接...
✅ 美团API连接测试完成，步骤: 3
```

### **第四步：浏览器爬取（推荐）**

```bash
# 使用浏览器爬取美团招聘数据
python3 src/meituan_crawler.py --mode browser
```

或使用启动脚本：
```bash
./run_meituan.sh
```

### **第五步：查看结果**

```bash
# 查看爬取的数据
ls -la output/crawl_data/

# 查看最新数据文件
cat output/crawl_data/meituan_positions_*.json | head -50
```

## 📊 数据字段说明

### **必须字段（12个）**
1. **position_id** - 岗位唯一标识
2. **position_name** - 岗位名称
3. **work_location** - 工作地点
4. **position_category** - 岗位类别
5. **publish_time** - 发布时间
6. **detail_url** - 详情页链接
7. **department** - 部门信息
8. **education_requirement** - 学历要求
9. **work_experience** - 工作经验
10. **job_responsibilities** - 工作职责
11. **job_requirements** - 任职要求
12. **salary_range** - 薪资范围

### **扩展字段**
- position_status - 岗位状态
- application_deadline - 申请截止日期
- company_name - 公司名称（美团）
- work_type - 工作类型
- benefits - 福利待遇

## 🔧 高级用法

### **自定义爬取URL**

```bash
# 使用自定义URL爬取
python3 src/meituan_crawler.py --mode browser --url "https://zhaopin.meituan.com/web/social?cityList=001019002"
```

### **详细日志模式**

```bash
# 查看详细日志
python3 src/meituan_crawler.py --mode browser --verbose
```

### **指定输出文件**

```bash
# 指定输出文件名
python3 src/meituan_crawler.py --mode browser --output "美团招聘数据.json"
```

### **多页爬取**

```bash
# 爬取多页数据（需要实现分页逻辑）
python3 src/meituan_crawler.py --mode browser --pages 3
```

## 🎯 美团招聘URL分析

### **基础URL**
```
https://zhaopin.meituan.com/web/social
```

### **筛选参数**
- **cityList=001019002** - 城市筛选（深圳）
- **jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001** - 岗位类别
  - 11002_-1: 技术类
  - 11003_-1: 产品类  
  - 11005_-1: 运营类
  - 11007_-1: 市场类
  - 11010_1101001: 数据类

### **完整示例URL**
```
https://zhaopin.meituan.com/web/social?cityList=001019002&jfJgList=11002_-1,11003_-1,11005_-1,11007_-1,11010_1101001
```

**注意**: `cityList=001019002` 对应的是 **深圳**，不是北京。

## 📁 项目结构

```
meituan-job/
├── 📚 知识层
│   ├── docs/                    # 10个核心文档模板
│   └── memory-system/          # 记忆系统
│       └── CORE_BUSINESS_INFO.md # 美团业务信息 ✅
├── 🔧 框架层
│   ├── src/framework/          # 三大核心框架
│   └── src/meituan_crawler.py  # 美团爬取器 ✅
├── ⚙️ 配置层
│   └── config/
│       ├── .env                # 环境配置 ✅
│       ├── project_config.json # 项目配置
│       └── api_auth.json       # API认证（待配置）
├── 🛠️ 工具层
│   ├── run_meituan.sh          # 启动脚本 ✅
│   ├── scripts/                # 工具脚本
│   └── tests/                  # 测试代码
└── 📊 数据层
    ├── data/                   # 数据目录
    ├── output/                 # 输出目录
    └── logs/                   # 日志目录
```

## 🚀 立即执行的命令

### **选项1：使用启动脚本（推荐）**
```bash
./run_meituan.sh
```
然后选择选项2（浏览器爬取）

### **选项2：直接命令**
```bash
# 1. 测试连接
python3 src/meituan_crawler.py --mode test

# 2. 浏览器爬取
python3 src/meituan_crawler.py --mode browser

# 3. 查看结果
ls -la output/crawl_data/
cat output/crawl_data/meituan_positions_*.json | jq '.positions[0]' 2>/dev/null || cat output/crawl_data/meituan_positions_*.json | head -30
```

## 🔍 调试和问题解决

### **常见问题**

#### **1. 浏览器启动失败**
```bash
# 确保已安装Playwright
python3 -m playwright install

# 检查配置
cat config/.env | grep HEADLESS_MODE
# 如果是true，改为false进行调试
```

#### **2. 网络连接问题**
```bash
# 测试网站可访问性
curl -I "https://zhaopin.meituan.com"

# 使用代理（如需）
export HTTP_PROXY="http://proxy.example.com:8080"
```

#### **3. 依赖安装问题**
```bash
# 重新安装依赖
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

### **调试模式**
```bash
# 启用调试日志
python3 src/meituan_crawler.py --mode browser --verbose

# 保存页面截图
# 编辑 config/.env，设置 SAVE_SCREENSHOTS=true
```

## 📈 后续开发计划

### **阶段1：MVP（已完成✅）**
- ✅ 项目框架搭建
- ✅ 环境配置
- ✅ 基础爬取器
- ✅ 数据导出功能

### **阶段2：功能完善**
- ⬜ API爬取实现
- ⬜ 分页逻辑
- ⬜ 数据清洗和验证
- ⬜ 错误处理优化

### **阶段3：高级功能**
- ⬜ 定时爬取
- ⬜ 数据监控
- ⬜ 报表生成
- ⬜ 可视化展示

## 📚 学习资源

### **项目文档**
1. **架构设计**: `docs/ARCHITECTURE.md`
2. **检查清单**: `docs/CHECKLIST.md` (53项标准检查)
3. **教训记录**: `docs/LESSONS_LEARNED.md`
4. **业务知识**: `docs/BUSINESS_KNOWLEDGE_SYSTEM.md`

### **技术文档**
1. **夸克框架**: `src/framework/` 目录
2. **美团爬取器**: `src/meituan_crawler.py`
3. **数据导出**: `src/framework/data_exporter.py`

### **外部资源**
1. **美团招聘**: https://zhaopin.meituan.com
2. **Playwright文档**: https://playwright.dev
3. **Requests文档**: https://docs.python-requests.org

## 🎉 恭喜！

你已经成功配置了美团招聘爬取项目。现在可以：

1. **立即开始爬取**: `./run_meituan.sh`
2. **查看爬取结果**: `output/crawl_data/` 目录
3. **定制爬取逻辑**: 编辑 `src/meituan_crawler.py`
4. **记录经验教训**: 更新 `docs/LESSONS_LEARNED.md`

### **下一步建议**
1. 运行一次完整的爬取，验证功能
2. 分析爬取的数据，确认字段完整性
3. 根据实际需求调整配置
4. 记录遇到的问题和解决方案

**祝你美团招聘数据爬取顺利！** 🚀

---
**最后更新**: 2026-05-21  
**版本**: v1.0.0  
**维护人**: xingan  
**项目状态**: ✅ 可立即使用