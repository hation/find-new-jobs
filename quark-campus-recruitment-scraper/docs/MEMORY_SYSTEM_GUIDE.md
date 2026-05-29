# 📚 夸克校园招聘爬取器 - 记忆系统使用指南

## 🚀 快速开始

### 1. 首次使用
```bash
# 切换到项目目录
cd /Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper

# 启动记忆系统
./start_smart.sh
```

### 2. 复制生成的指令
启动器会生成标准化指令，复制并发送给助手：
```
执行夸克校园招聘爬取器任务：步骤1验证记忆完整性，步骤2检查待办事项，步骤3开始执行
```

### 3. 助手执行
助手会基于记忆系统文件正确执行任务。

## 📁 文件说明

### 核心文件
- `ARCHITECTURE.md` - 架构规范，定义项目原则和结构
- `CHECKLIST.md` - 操作检查清单，确保操作正确性
- `LESSONS_LEARNED.md` - 教训记录，避免重复犯错
- `memory_checkpoints.json` - 记忆检查点，记录项目状态

### 工具文件
- `start_smart.sh` - 智能启动器，生成标准化指令
- `scripts/auto_memory_loader.py` - 自动记忆加载器
- `config/memory_config.json` - 系统配置

## 🔧 日常使用

### 开始工作
```bash
./start_smart.sh
# 复制输出指令 → 发送给助手
```

### 记录错误
1. 遇到错误时立即记录到 `LESSONS_LEARNED.md`
2. 分析原因并制定预防措施
3. 更新 `CHECKLIST.md` 添加防错检查项

### 更新架构
1. 重大变更前更新 `ARCHITECTURE.md`
2. 记录变更原因和影响
3. 通知相关人员

## 📊 维护建议

### 每周检查
- 检查记忆文件完整性
- 回顾教训记录
- 更新检查清单
- 备份重要文件

### 每月回顾
- 分析错误模式
- 优化工作流程
- 更新架构原则
- 评估系统效果

## 🆘 故障排除

### 记忆文件丢失
```bash
# 重新初始化记忆系统
python /Users/xingan/.openclaw/memory_framework/scripts/init_memory_system.py \
  --name '夸克校园招聘爬取器' \
  --path '/Users/xingan/.openclaw/workspace/skills/find_new_jobs/quark-campus-recruitment-scraper' \
  --type 'web_scraper'
```

### 启动器失效
```bash
# 手动加载记忆
python scripts/auto_memory_loader.py
```

## 📞 支持

如有问题，请参考：
1. 框架文档: /Users/xingan/.openclaw/memory_framework/README.md
2. 项目文档: docs/ 目录
3. 配置说明: config/memory_config.json

---
*记忆系统版本: 1.0*
*最后更新: 2026-05-19 15:03:08*
