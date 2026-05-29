# 📁 夸克校园招聘爬取器 - 项目结构

## 🎯 **最终方案核心文件**

### **根目录**
```
quark_crawler.py          # 🚀 统一入口（推荐使用）
merge_to_excel.py         # 📊 数据导出到Excel
detailed_data_check.py    # 🔍 数据完整性检查
```

### **scripts/ 核心脚本**
```
api_crawler_configurable.py      # 🔧 可配置的API爬取器
crawler_selector_optimized.py    # 🧠 优化的智能选择器（失败后询问）
browser_crawler.py               # 🌐 浏览器爬取器（备选方案）
```

### **config/ 配置文件**
```
api_auth.json                    # 🔐 API认证配置（CSRF令牌、Cookie等）
```

### **output/ 输出目录**
```
quark_page_1_raw.json           # 📄 原始数据
quark_page_2_raw.json
...
all_positions_processed.json    # 📊 处理后的完整数据
quark_positions_20260520.xlsx   # 📈 Excel文件
```

### **other/ 历史文件和测试文件**
```
scripts/                        # 📜 历史版本脚本
  api_crawler.py                # 初始版本
  api_crawler_complete.py       # 完整版
  api_crawler_final.py          # 最终版
  api_crawler_perfect.py        # 完美版
  crawler_selector.py           # 原始选择器
  fix_api_auth.py               # 认证修复工具
  actual_crawler.py             # 实际爬取器（旧版）
  main.py                       # 主脚本（旧版）
  AUTO_LOADER.py                # 自动加载器（功能已集成）
  
tests/                          # 🧪 测试文件
  test_*.py                     # 各种测试脚本
  
docs/                           # 📚 文档和分析
  analysis_summary.md           # 文件分析总结
```

## 🚀 **使用说明**

### **推荐使用方式**
```bash
# 1. 使用优化模式（失败后询问）
python3 quark_crawler.py --mode optimized

# 2. 查看帮助信息
python3 quark_crawler.py --help

# 3. 查看项目状态
python3 quark_crawler.py --mode status

# 4. 导出数据到Excel
python3 quark_crawler.py --mode export --format excel
```

### **工作流程**
1. **API优先**：首先尝试使用高效的API方案
2. **失败告知**：如果API失败，显示具体原因
3. **用户询问**：询问是否切换到浏览器模式
4. **智能处理**：根据用户选择执行相应操作

## 📋 **核心功能**
- ✅ API优先，高效稳定
- ✅ 失败后告知具体原因
- ✅ 询问用户是否切换到浏览器
- ✅ 支持用户决策和重试
- ✅ 集成到统一入口
- ✅ 符合插件规范

## 🛠️ **开发说明**
- **新方案**：使用`optimized`模式
- **历史参考**：`other/`目录保存历史版本
- **配置文件**：`config/api_auth.json`管理认证信息
- **数据导出**：支持Excel、CSV、JSON格式

## 📅 **更新记录**
- **2026-05-20**：整理项目结构，移动无关脚本到`other/`目录
- **2026-05-20**：创建优化方案，支持失败后询问用户
- **2026-05-20**：实现统一入口`quark_crawler.py`
- **2026-05-19**：验证并完善API方案

---

**项目状态**：✅ 优化完成，结构清晰，随时可用