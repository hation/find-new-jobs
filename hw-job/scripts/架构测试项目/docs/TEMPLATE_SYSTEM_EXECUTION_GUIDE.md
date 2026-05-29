# 🚀 模板系统快速执行指南

## 📋 一分钟了解模板系统

**核心价值**: 将夸克项目的经验转化为可复用的业务知识体系  
**包含内容**: 11个模板 + 1个迁移脚本  
**使用场景**: 任何新的数据爬取或类似业务项目

## 🎯 四个关键阶段

### **阶段1：业务确认** (1-2天)
```
使用: CORE_BUSINESS_INFO_TEMPLATE.md
目的: 明确业务目标和需求
产出: 清晰业务需求文档
```

### **阶段2：技术设计** (2-3天)
```
使用: ARCHITECTURE_TEMPLATE.md + PROJECT_STRUCTURE.md
目的: 制定技术方案和项目结构
产出: 完整技术设计文档
```

### **阶段3：执行保障** (1天)
```
使用: CHECKLIST_TEMPLATE.md + QUICK_START_TEMPLATE.md
目的: 确保执行质量和效率
产出: 可执行行动计划和检查清单
```

### **阶段4：经验沉淀** (持续)
```
使用: LESSONS_LEARNED_TEMPLATE.md + memory-system/
目的: 积累经验和持续改进
产出: 组织知识资产和最佳实践
```

## 🚀 快速启动新项目

### **方法1：一键迁移** (推荐)
```bash
# 复制夸克项目经验到新项目
./template/one-click-migration.sh --new-project "你的项目名称"

# 生成的文件结构
your_project/
├── docs/                    # 所有模板文档
├── memory-system/          # 记忆系统
└── scripts/                # 工具脚本
```

### **方法2：手动应用** (定制需求)
```markdown
## 步骤1：复制模板
cp template/docs/CORE_BUSINESS_INFO_TEMPLATE.md docs/CORE_BUSINESS_INFO.md
cp template/docs/ARCHITECTURE_TEMPLATE.md docs/ARCHITECTURE.md
cp template/docs/CHECKLIST_TEMPLATE.md docs/CHECKLIST.md

## 步骤2：根据项目修改
# 修改CORE_BUSINESS_INFO.md中的业务信息
# 修改ARCHITECTURE.md中的技术设计
# 修改CHECKLIST.md中的检查项

## 步骤3：开始使用
# 按照CHECKLIST.md执行项目
# 遇到问题记录在LESSONS_LEARNED.md
# 每日记录在DAILY_MEMORY.md
```

## 🔑 三个必用模板

### **1. CHECKLIST模板** (防错核心)
**什么时候用**: 执行任何重要操作前
**怎么用**:
1. 复制模板: `cp CHECKLIST_TEMPLATE.md CHECKLIST.md`
2. 根据项目定制检查项
3. 执行前逐项检查
4. 执行后记录结果

**核心价值**: 防止重复犯错

### **2. LESSONS_LEARNED模板** (学习核心)
**什么时候用**: 遇到任何问题或失败时
**怎么用**:
1. 立即记录问题现象
2. 分析根本原因
3. 制定解决方案和预防措施
4. 更新CHECKLIST中的检查项

**核心价值**: 将错误转化为组织资产

### **3. CORE_BUSINESS_INFO模板** (对齐核心)
**什么时候用**: 项目启动时，团队讨论前
**怎么用**:
1. 团队一起填写业务信息
2. 明确数据需求和成功标准
3. 达成一致理解
4. 作为后续所有工作的基准

**核心价值**: 确保团队对业务目标理解一致

## 📊 模板关联速查表

| 使用场景 | 主要模板 | 辅助模板 | 产出物 |
|---------|---------|---------|--------|
| 新项目启动 | CORE_BUSINESS_INFO | PROJECT_STRUCTURE | 业务需求文档 |
| 技术方案设计 | ARCHITECTURE | API_DOCUMENTATION | 技术设计文档 |
| 执行前准备 | CHECKLIST | QUICK_START | 执行计划 |
| 执行中监控 | DAILY_MEMORY | (无) | 进度记录 |
| 遇到问题 | LESSONS_LEARNED | CHECKLIST | 解决方案 |
| 项目结束 | 所有模板 | MIGRATION_TEMPLATE | 经验总结 |

## ⚡ 快速问题解决

### **问题：不知道从哪个模板开始？**
**答案**: 从`CORE_BUSINESS_INFO_TEMPLATE.md`开始，明确业务目标。

### **问题：模板太多太复杂？**
**答案**: 只使用三个核心模板：业务信息、检查清单、教训记录。

### **问题：如何定制模板？**
**答案**: 复制模板文件，删除不需要的部分，保留核心结构。

### **问题：模板会过时吗？**
**答案**: 会。定期回顾`LESSONS_LEARNED.md`中的教训，更新相关模板。

## 🔄 持续改进循环

```
简单记住这个循环：
执行 → 发现问题 → 记录教训 → 更新检查清单 → 更好执行
```

**关键**: 每次执行都要比上次更好，避免重复犯错。

## 📈 成功度量

### **短期成功** (1个月)
- ✅ 项目启动时间减少50%
- ✅ 重复错误减少80%
- ✅ 团队对业务理解一致

### **中期成功** (3个月)
- ✅ 项目成功率提升到90%
- ✅ 新成员培训时间减少60%
- ✅ 形成团队知识库

### **长期成功** (1年)
- ✅ 成为团队标准工作方法
- ✅ 推动行业最佳实践
- ✅ 建立可持续的成功模式

## 🎯 立即行动清单

### **今天可以做的**
1. [ ] 浏览`template/docs/`目录，了解有哪些模板
2. [ ] 复制`CHECKLIST_TEMPLATE.md`到你的项目
3. [ ] 为下一个任务创建一个简单的检查清单

### **本周可以做的**
1. [ ] 使用`CORE_BUSINESS_INFO_TEMPLATE.md`明确一个项目目标
2. [ ] 在`LESSONS_LEARNED_TEMPLATE.md`中记录一个最近的问题
3. [ ] 和团队分享一个模板的使用经验

### **本月可以做的**
1. [ ] 在一个完整项目中应用所有模板
2. [ ] 收集团队对模板的反馈
3. [ ] 基于反馈优化一个模板

## 📞 快速支持

### **遇到问题？**
1. **查看完整文档**: `BUSINESS_KNOWLEDGE_SYSTEM.md`
2. **查看流程图**: `BUSINESS_TEMPLATE_FLOW.md`
3. **使用迁移脚本**: `one-click-migration.sh`

### **需要帮助？**
1. **先尝试**: 使用`QUICK_START_TEMPLATE.md`
2. **再提问**: 在`LESSONS_LEARNED_TEMPLATE.md`中记录问题
3. **最后求助**: 联系有经验的团队成员

---

## 🔚 一句话总结

**使用这些模板，让每个新项目都能站在前人的肩膀上，避免重复踩坑，快速实现业务目标。**

---

**文档信息**:
- **版本**: v1.0.0
- **创建时间**: 2026-05-21
- **预计阅读时间**: 5分钟
- **预计应用时间**: 1小时
- **关联文档**: 见`template/docs/`目录