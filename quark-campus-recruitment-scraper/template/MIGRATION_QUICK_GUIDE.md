# 🚀 一键迁移指南：如何将模板应用到新项目

## 📋 最简单的迁移方法

### **方法一：一键迁移脚本（推荐）**
```bash
# 1. 进入模板目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper/template

# 2. 运行迁移脚本
./scripts/new-project-migration.sh "你的新项目名称"

# 示例：创建字节跳动招聘爬取器
./scripts/new-project-migration.sh "字节跳动招聘爬取器"

# 3. 进入新项目
cd ../字节跳动招聘爬取器

# 4. 启动项目
./start_project.sh
```

### **方法二：带选项的迁移**
```bash
# 指定目标目录
./scripts/new-project-migration.sh -d ~/projects "美团招聘爬取器"

# 指定项目类型
./scripts/new-project-migration.sh -t api "API数据采集项目"

# 模拟运行（不实际创建文件）
./scripts/new-project-migration.sh --dry-run "测试项目"

# 强制覆盖已存在的目录
./scripts/new-project-migration.sh -f "已有项目名称"
```

## 🎯 迁移后得到什么？

### **完整的项目结构**
```
新项目名称/
├── 📁 docs/                    # 完整文档体系（11个模板）
├── 📁 config/                  # 配置文件
├── 📁 scripts/                 # 工具脚本
├── 📁 src/                     # 源代码目录
├── 📁 tests/                   # 测试目录
├── 📁 logs/                    # 日志目录
├── 📁 data/                    # 数据目录
├── 📁 memory-system/           # 记忆系统
├── 📄 README.md                # 项目启动指南
├── 📄 start_project.sh         # 交互式启动脚本
└── 📄 scripts/new-project-migration.sh # 可继续迁移
```

### **核心文档已就绪**
- ✅ `docs/CORE_BUSINESS_INFO.md` - 业务目标模板（已替换项目名）
- ✅ `docs/CHECKLIST.md` - 检查清单模板
- ✅ `docs/LESSONS_LEARNED.md` - 教训记录模板
- ✅ `docs/QUICK_START.md` - 快速开始指南
- ✅ `docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md` - 模板使用指南

## 🔄 迁移后立即开始的步骤

### **第一步：理解业务目标（30分钟）**
```bash
# 1. 查看业务目标文档
cat docs/CORE_BUSINESS_INFO.md

# 2. 与团队一起填写
# 编辑 docs/CORE_BUSINESS_INFO.md，明确：
#   - 项目目标
#   - 数据需求
#   - 成功标准
#   - 业务规则
```

### **第二步：执行检查清单（15分钟）**
```bash
# 使用交互式启动脚本
./start_project.sh

# 选择 "3. 执行检查清单"
# 按照提示逐项检查
```

### **第三步：快速验证（1小时）**
```bash
# 按照快速开始指南操作
# 查看 docs/QUICK_START.md
# 完成环境搭建和配置测试
```

## 📊 模板如何自动生效？

### **1. 检查清单防错系统**
迁移后的项目**自动包含**：
- 53项标准检查项（基于夸克项目教训）
- 执行前/中/后的验证步骤
- 质量指标和验收标准

**生效方式**：每次执行重要操作前，强制检查`docs/CHECKLIST.md`

### **2. 教训记录学习系统**
**自动包含**：
- 标准化错误记录格式
- 根本原因分析模板
- 预防措施制定指南

**生效方式**：遇到问题时，立即在`docs/LESSONS_LEARNED.md`中记录

### **3. 记忆系统知识积累**
**自动包含**：
- 每日记忆模板
- 核心业务信息模板
- 记忆系统使用指南

**生效方式**：每日工作记录在`memory-system/`中

## ⚡ 快速验证迁移是否成功

### **验证命令**
```bash
# 运行验证脚本（如果迁移脚本创建了的话）
./scripts/validate_migration.py

# 或手动检查
ls -la docs/  # 应该看到11个模板文件
ls -la config/ # 应该看到配置文件
ls -la scripts/ # 应该看到工具脚本
```

### **成功标志**
```
✅ docs/CORE_BUSINESS_INFO.md 存在且已替换项目名
✅ docs/CHECKLIST.md 存在且包含标准检查项
✅ docs/LESSONS_LEARNED.md 存在且格式正确
✅ README.md 存在且包含项目启动指南
✅ start_project.sh 存在且可执行
```

## 🔧 自定义和调整

### **如果不需要所有模板**
```bash
# 迁移时跳过部分模板
./scripts/new-project-migration.sh --skip-docs "轻量项目"
./scripts/new-project-migration.sh --skip-memory "简单项目"
./scripts/new-project-migration.sh --skip-scripts "手动管理项目"
```

### **如果项目类型不同**
```bash
# 指定项目类型，模板会相应调整
./scripts/new-project-migration.sh -t api "API数据项目"
./scripts/new-project-migration.sh -t data-processing "数据处理项目"
./scripts/new-project-migration.sh -t crawler "网页爬虫项目"  # 默认
```

### **如果需要调整模板**
```markdown
# 迁移后可以自由调整
1. 编辑 docs/CORE_BUSINESS_INFO.md - 修改业务信息
2. 编辑 docs/CHECKLIST.md - 增减检查项
3. 编辑 docs/ARCHITECTURE.md - 调整技术架构
4. 编辑 config/project_config.json - 修改项目配置
```

## 📈 迁移的最佳实践

### **团队项目迁移**
```bash
# 1. 项目经理先迁移
./scripts/new-project-migration.sh "团队项目名称"

# 2. 填写核心业务信息
# 与团队一起完成 docs/CORE_BUSINESS_INFO.md

# 3. 分享给团队成员
git init
git add .
git commit -m "初始提交：基于夸克模板创建的项目"
git push

# 4. 团队成员克隆
git clone <仓库地址>
cd 项目名称
./start_project.sh
```

### **个人项目迁移**
```bash
# 1. 快速创建
./scripts/new-project-migration.sh "我的实验项目"

# 2. 只使用核心模板
# 重点关注：业务信息、检查清单、教训记录

# 3. 轻量使用
# 不需要填写所有模板，按需使用
```

### **企业级项目迁移**
```bash
# 1. 创建基础项目
./scripts/new-project-migration.sh -d /opt/projects "企业数据采集项目"

# 2. 定制化调整
# 根据企业规范修改模板
# 添加企业特定的检查项
# 集成企业工具链

# 3. 建立模板仓库
# 将定制后的模板保存为企业标准模板
```

## 🆘 常见问题解决

### **问题1：迁移脚本没有执行权限**
```bash
chmod +x scripts/new-project-migration.sh
```

### **问题2：目录已存在**
```bash
# 使用 -f 选项强制覆盖
./scripts/new-project-migration.sh -f "项目名称"

# 或指定其他目录
./scripts/new-project-migration.sh -d ~/other_projects "项目名称"
```

### **问题3：模板内容不符合需求**
```markdown
# 迁移后自由修改
1. 删除不需要的部分
2. 添加项目特定的内容
3. 保持核心结构不变

# 核心结构不要变：
- CHECKLIST.md 的检查项格式
- LESSONS_LEARNED.md 的分析框架
- CORE_BUSINESS_INFO.md 的业务信息结构
```

### **问题4：想恢复到原始模板**
```bash
# 重新迁移（覆盖）
./scripts/new-project-migration.sh -f "项目名称"

# 或从模板目录手动复制
cp template/docs/*.md docs/
```

## 🎯 迁移后的关键行动

### **24小时内完成**
1. [ ] 填写 `docs/CORE_BUSINESS_INFO.md` 中的业务信息
2. [ ] 运行 `./start_project.sh` 完成环境检查
3. [ ] 查看 `docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md` 了解如何使用

### **第一周内完成**
1. [ ] 在 `docs/LESSONS_LEARNED.md` 中记录遇到的第一个问题
2. [ ] 根据项目需要调整 `docs/CHECKLIST.md`
3. [ ] 使用 `memory-system/DAILY_MEMORY_TEMPLATE.md` 记录每日工作

### **第一个月内完成**
1. [ ] 回顾 `docs/LESSONS_LEARNED.md` 中的教训
2. [ ] 更新 `docs/CHECKLIST.md` 中的预防措施
3. [ ] 总结项目经验，优化模板系统

## 🔄 持续改进循环

```
迁移模板 → 使用模板 → 发现问题 → 改进模板 → 更好使用
      ↓                                    ↓
  新项目 ← 应用改进 ← 总结经验 ← 记录教训
```

**关键**：每次使用模板都要比上次更好，形成持续改进的正向循环。

---

## 📞 快速帮助

### **需要立即帮助？**
```bash
# 查看迁移脚本帮助
./scripts/new-project-migration.sh -h

# 查看项目启动帮助
./start_project.sh

# 查看模板使用指南
cat docs/TEMPLATE_SYSTEM_EXECUTION_GUIDE.md
```

### **需要更多信息？**
- 查看完整文档：`docs/BUSINESS_KNOWLEDGE_SYSTEM.md`
- 查看流程图：`docs/BUSINESS_TEMPLATE_FLOW.md`
- 查看原始模板：`template/docs/` 目录

---

## 🎉 开始你的第一个迁移！

```bash
# 最简单的开始方式
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper/template
./scripts/new-project-migration.sh "我的第一个模板项目"
cd ../我的第一个模板项目
./start_project.sh
```

**记住**：迁移不仅是复制文件，更是**复制成功的工作方法和持续改进的能力**。

---

**文档信息**:
- **创建时间**: 2026-05-21
- **版本**: v1.0.0
- **预计阅读时间**: 10分钟
- **预计执行时间**: 5分钟
- **关联文件**: `scripts/new-project-migration.sh`