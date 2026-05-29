# 夸克校园招聘爬虫 - 项目结构

## 📁 目录结构

```
quark-campus-recruitment-scraper/
├── scripts/                    # 核心脚本目录（重点优化）
│   ├── main.py                # 主脚本 - 入口点
│   ├── actual_crawler.py      # 实际爬虫脚本（基于验证的代码）
│   ├── core/                  # 核心模块
│   │   └── crawler.py         # 爬虫核心类
│   ├── utils/                 # 工具函数
│   │   ├── browser_utils.py   # 浏览器工具
│   │   ├── excel_writer.py    # Excel写入器
│   │   ├── scraper.py         # 数据提取器
│   │   └── validator.py       # 数据验证器
│   ├── tests/                 # 测试脚本
│   │   └── test_page1.py      # 第1页测试
│   └── docs/                  # 文档
│       └── PROJECT_STRUCTURE.md
├── archive/                   # 归档目录（旧脚本）
│   ├── test_*.py             # 各种测试脚本
│   ├── run_*.py              # 运行脚本
│   └── full_*.py             # 完整流程脚本
├── utils/                     # 原始工具目录（保留）
│   ├── browser_utils.py
│   ├── excel_writer.py
│   ├── scraper.py
│   └── validator.py
├── output/                    # 输出目录
│   ├── correct_page1_test/   # 第1页测试结果
│   ├── full_workflow_test/   # 完整流程测试
│   ├── immediate_results/    # 立即结果
│   ├── crawl_plans/          # 爬取计划
│   ├── guides/               # 指南文档
│   └── scripts/              # 生成的脚本
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖文件
├── main.py                   # 原始主脚本（备份）
├── SKILL.md                  # 技能说明
├── USAGE.md                  # 使用说明
├── progress.md               # 进度记录
└── README.md                 # 项目说明
```

## 🎯 核心脚本说明

### **主脚本 (scripts/main.py)**
- **功能**: 项目入口点，整合所有功能
- **特点**: 命令行参数支持，模块化设计
- **用法**: 
  ```bash
  python scripts/main.py --help
  python scripts/main.py --test-page1
  python scripts/main.py --all-pages
  ```

### **实际爬虫脚本 (scripts/actual_crawler.py)**
- **来源**: 基于验证的成功代码
- **状态**: ✅ 已测试通过
- **功能**: 真实数据提取、Excel生成、日志系统

### **核心模块 (scripts/core/)**
- **crawler.py**: 爬虫核心类，可扩展功能

### **工具函数 (scripts/utils/)**
- **browser_utils.py**: 浏览器交互工具
- **excel_writer.py**: Excel文件生成
- **scraper.py**: 数据提取和解析
- **validator.py**: 数据验证和质量检查

## 🔧 开发原则

### **1. 不创建冗余脚本**
- 在现有脚本上迭代修改
- 使用git管理版本
- 模块化设计，易于扩展

### **2. 保持代码整洁**
- scripts/目录只包含核心脚本
- archive/目录存放旧版本
- utils/目录保留原始工具

### **3. 验证驱动开发**
- 先测试单页功能
- 再扩展多页支持
- 最后添加详情获取

## 🚀 当前状态

### **已完成**
- ✅ 筛选条件应用（7个类别，92个岗位）
- ✅ 第1页数据提取（10个真实岗位）
- ✅ Excel文件生成（12个字段）
- ✅ 完整工作流测试验证

### **待完成**
- ⏳ 获取第2-10页数据（82个岗位）
- ⏳ 点击岗位获取详情信息
- ⏳ 生成最终92个岗位的Excel

## 📋 下一步计划

### **立即执行**
1. **优化scripts/actual_crawler.py**
   - 添加翻页支持
   - 添加详情获取
   - 优化错误处理

2. **完善scripts/main.py**
   - 添加命令行参数
   - 集成所有功能
   - 添加进度显示

### **后续优化**
1. **模块化重构**
   - 将功能拆分为独立模块
   - 提高代码复用性
   - 添加单元测试

2. **性能优化**
   - 添加并发处理
   - 优化内存使用
   - 添加缓存机制

## 📝 最佳实践

### **代码管理**
```bash
# 在scripts目录工作
cd scripts/

# 修改现有脚本
vim actual_crawler.py

# 测试修改
python actual_crawler.py

# 运行主脚本
python main.py --test-page1
```

### **版本控制**
```bash
# 提交核心脚本
git add scripts/
git commit -m "优化爬虫核心功能"

# 归档旧脚本
git add archive/
git commit -m "归档旧版本脚本"
```

### **测试验证**
```bash
# 单页测试
python tests/test_page1.py

# 完整流程测试
python main.py --test-page1

# 数据验证
python utils/validator.py
```

## 🔍 注意事项

1. **真实数据原则**: 不编造任何字段值
2. **防反爬机制**: 添加随机延迟和用户代理轮换
3. **错误处理**: 完善的异常捕获和重试机制
4. **数据验证**: 每个阶段验证数据质量
5. **进度记录**: 详细记录爬取进度和问题

## 📞 问题反馈

如有问题或建议：
1. 检查scripts/目录的代码
2. 查看archive/目录的旧版本参考
3. 查看output/目录的测试结果
4. 记录到progress.md文件中

---

**最后更新**: 2026-05-18
**状态**: ✅ 项目结构已优化，可开始重点开发