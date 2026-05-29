# 🚀 夸克校园招聘API爬取系统 - 使用指南
# 创建时间: 2026-05-20T10:15:00 GMT+8
# 版本: 1.0 (API优先系统)

## 🎯 系统概述

### 核心特点
- **API优先**: 默认使用已验证的高效API接口
- **智能切换**: API不可用时自动切换到浏览器模式
- **数据一致**: 两种模式输出相同格式的数据
- **高效稳定**: 比浏览器自动化快10-100倍

### 已验证的API信息
```
API URL: https://talent.quark.cn/position/search
请求方法: POST
认证方式: CSRF Token + Cookie
7个类别ID: 97,103,143,152,124,146,492
分页参数: pageIndex (从1开始), pageSize=10
```

## 📋 快速开始

### 方法1：一键启动（推荐）
```bash
# Linux/Mac
cd ~/.openclaw/workspace/skills/quark-campus-recruitment-scraper
./run_api.sh

# Windows
cd %USERPROFILE%\.openclaw\workspace\skills\quark-campus-recruitment-scraper
run_api.bat
```

### 方法2：使用主脚本
```bash
cd ~/.openclaw/workspace/skills/quark-campus-recruitment-scraper
python scripts/main.py --mode auto
```

### 方法3：交互式使用
```bash
cd ~/.openclaw/workspace/skills/quark-campus-recruitment-scraper

# 智能模式（默认API优先）
python scripts/main.py --mode auto

# 强制API模式
python scripts/main.py --mode api

# 强制浏览器模式
python scripts/main.py --mode browser

# 混合模式
python scripts/main.py --mode mixed

# 测试模式
python scripts/main.py --test
```

## 🔧 详细使用说明

### 1. 智能选择器模式 (`--mode auto`)
这是**默认模式**，系统会自动：
1. 检查API接口可用性
2. 如果API可用，使用API模式爬取
3. 如果API不可用，自动切换到浏览器模式
4. 记录切换日志和性能统计

```bash
# 使用智能模式
python scripts/main.py --mode auto --log-level INFO

# 输出示例
🚀 夸克校园招聘智能爬取系统启动
📊 智能选择器：API可用 → 选择API模式
✅ API模式成功：获取92个岗位，耗时15.2秒
```

### 2. API模式 (`--mode api`)
强制使用API模式，如果API不可用则失败。

```bash
# 强制API模式
python scripts/main.py --mode api --force-api

# 输出示例
🔧 强制API模式爬取
📊 API认证成功，CSRF令牌有效
✅ API获取完成：92个岗位，耗时12.8秒
```

### 3. 浏览器模式 (`--mode browser`)
强制使用浏览器模式，完全模拟手动操作。

```bash
# 强制浏览器模式
python scripts/main.py --mode browser --force-browser

# 输出示例
🔧 强制浏览器模式爬取
📊 浏览器启动成功，应用7个筛选类别
✅ 浏览器模式完成：92个岗位，耗时25分钟
```

### 4. 混合模式 (`--mode mixed`)
高级模式，结合两种方式的优势：
- API获取岗位列表和基本信息
- 浏览器获取详情页的详细数据

```bash
# 使用混合模式
python scripts/main.py --mode mixed

# 输出示例
🔄 混合模式爬取
📊 API获取列表：92个岗位，耗时5.2秒
📊 浏览器获取详情：耗时15分钟
✅ 混合模式完成：92个完整岗位数据
```

## ⚙️ 配置说明

### 配置文件 (`config.yaml`)
```yaml
project:
  name: "夸克校园招聘爬取器"
  version: "2.0"
  target_positions: 92
  categories:
    - "产品类"
    - "运营类"
    - "数据类"
    - "市场拓展"
    - "销售类"
    - "游戏类"
    - "金融类"

crawler:
  mode: "auto"          # auto, api, browser, mixed
  max_pages: 10
  page_size: 10
  output_dir: "output/positions"
  retry_times: 3
  retry_delay: 2.0

api:
  enabled: true
  url: "https://talent.quark.cn/position/search"
  categories: "97,103,143,152,124,146,492"
  timeout: 30

browser:
  enabled: true
  profile: "openclaw"
  headless: false
  timeout: 60

quality:
  validate_fields: true
  required_fields:
    - "position_id"
    - "position_name"
    - "position_category"
    - "work_location"
    - "update_time"
  min_fields_required: 10
```

### 命令行参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 爬取模式: auto/api/browser/mixed | auto |
| `--log-level` | 日志级别: DEBUG/INFO/WARNING/ERROR | INFO |
| `--config` | 配置文件路径 | config.yaml |
| `--output` | 输出目录 | output/positions |
| `--test` | 测试模式 | false |
| `--force-api` | 强制使用API模式 | false |
| `--force-browser` | 强制使用浏览器模式 | false |

## 📊 输出文件说明

### 1. 数据文件
```
output/positions/
├── quark_api_positions_20260520_101500.json  # API模式数据
├── quark_browser_positions_20260520_103000.json  # 浏览器模式数据
└── quark_crawler_result_20260520_104500.json  # 完整爬取结果
```

### 2. 日志文件
```
logs/
├── api_crawler.log          # API爬取器日志
├── crawler_selector.log     # 智能选择器日志
├── main.log                # 主程序日志
└── quark_crawler_20260520_101500.log  # 完整执行日志
```

### 3. 报告文件
```
output/reports/
├── performance_report_20260520_101500.txt  # 性能报告
├── data_quality_report_20260520_101500.txt # 数据质量报告
└── error_summary_20260520_101500.txt      # 错误汇总
```

## 🔍 数据字段说明

### 标准字段 (12个)
基于我们已验证的API方案，系统会提取以下字段：

| 字段 | 说明 | 来源 |
|------|------|------|
| **position_id** | 岗位唯一标识 | API字段: positionId |
| **position_name** | 岗位名称 | API字段: title |
| **position_category** | 岗位类别 | API字段: category |
| **work_location** | 工作地点 | API字段: location |
| **update_time** | 更新时间 | API字段: updateTime |
| **department** | 部门信息 | API字段: department |
| **education_requirement** | 学历要求 | API字段: education |
| **work_experience** | 工作经验 | API字段: experience |
| **position_description** | 岗位描述 | API字段: description |
| **position_requirements** | 岗位要求 | API字段: requirements |
| **other_info** | 其他信息 | API字段: other |
| **source** | 数据来源 | api 或 browser |

### 元数据字段
| 字段 | 说明 |
|------|------|
| **extract_time** | 提取时间 |
| **page_url** | 详情页URL |
| **crawler_mode** | 爬取模式 |
| **completion_percentage** | 完成比例 |

## ⚠️ 常见问题与解决方案

### 问题1: API认证失败
**现象**: API返回403或认证错误
**解决方案**:
```bash
# 方法1：切换到浏览器模式
python scripts/main.py --force-browser

# 方法2：重新获取认证信息
# 脚本会自动从浏览器获取新的CSRF令牌和Cookie
```

### 问题2: 网络连接超时
**现象**: API请求超时
**解决方案**:
```bash
# 方法1：增加超时时间
python scripts/main.py --mode api --config custom_config.yaml
# 在custom_config.yaml中设置: api.timeout: 60

# 方法2：使用浏览器模式
python scripts/main.py --force-browser
```

### 问题3: 数据不完整
**现象**: 获取的岗位数量少于92个
**解决方案**:
```bash
# 方法1：检查筛选状态
# 确保7个筛选类别已正确应用

# 方法2：使用混合模式获取完整数据
python scripts/main.py --mode mixed

# 方法3：手动验证API响应
# 查看logs/api_crawler.log中的详细响应
```

### 问题4: 性能问题
**现象**: 爬取速度慢
**解决方案**:
```bash
# 方法1：使用API模式（最快）
python scripts/main.py --force-api

# 方法2：调整配置参数
# 减少retry_delay，增加page_size（如果支持）

# 方法3：检查网络连接
```

## 🔄 智能切换机制

### 切换触发条件
1. **API认证失败** → 切换到浏览器
2. **网络连接超时** → 重试3次后切换
3. **API响应错误** → 切换到浏览器
4. **数据不完整** → 混合模式补充

### 切换日志示例
```
📊 智能选择器状态:
✅ API可用性测试通过
🚀 选择API模式（优先）
⚠️  API认证失败，获取新CSRF令牌
🔄 切换到浏览器模式（备选）
✅ 浏览器模式启动成功
```

### 性能对比
| 模式 | 单页耗时 | 92个岗位总耗时 | 资源使用 | 稳定性 |
|------|----------|---------------|----------|--------|
| **API模式** | 0.5-1秒 | 10-15秒 | 低 | 高 |
| **浏览器模式** | 5-10秒 | 20-30分钟 | 高 | 中 |
| **混合模式** | 2-3秒 | 10-20分钟 | 中 | 高 |

## 🧪 测试与验证

### 单元测试
```bash
# 测试API爬取器
python scripts/api_crawler.py

# 测试智能选择器
python scripts/crawler_selector.py

# 完整系统测试
python scripts/main.py --test
```

### 集成测试
```bash
# 测试API模式
python scripts/main.py --mode api --test

# 测试浏览器模式
python scripts/main.py --mode browser --test

# 测试智能切换
python scripts/main.py --mode auto --test
```

### 性能测试
```bash
# 性能对比测试
./scripts/performance_test.sh

# 输出示例
API模式: 92个岗位，12.5秒，成功率98%
浏览器模式: 92个岗位，25分钟，成功率95%
混合模式: 92个岗位，15分钟，成功率99%
```

## 📈 最佳实践

### 1. 日常使用
```bash
# 最简单的使用方式
./run_api.sh

# 或
python scripts/main.py
```

### 2. 批量处理
```bash
# 批量爬取并保存结果
for i in {1..5}; do
  echo "第 $i 次执行"
  python scripts/main.py --output "output/batch_$i"
  sleep 60  # 间隔1分钟
done
```

### 3. 监控与报告
```bash
# 生成详细报告
python scripts/main.py --log-level DEBUG

# 查看实时日志
tail -f logs/quark_crawler_*.log

# 检查数据质量
python scripts/quality_check.py
```

## 🔗 相关文件

### 核心文件
- `scripts/api_crawler.py` - API爬取器核心
- `scripts/crawler_selector.py` - 智能选择器
- `scripts/main.py` - 主程序入口
- `API_CHECKLIST.md` - API专用检查清单

### 配置与文档
- `config.yaml` - 配置文件
- `ARCHITECTURE.md` - 架构文档
- `LESSONS_LEARNED.md` - 教训记录
- `memory_checkpoints.json` - 状态检查点

### 启动脚本
- `run_api.sh` - Linux/Mac启动脚本
- `run_api.bat` - Windows启动脚本
- `start_smart.sh` - 智能启动器

## 📞 技术支持

### 查看日志
```bash
# 查看最新日志
ls -la logs/quark_crawler_*.log
tail -100 logs/quark_crawler_20260520_101500.log

# 查看错误日志
grep -i "error\|fail\|exception" logs/*.log
```

### 报告问题
1. **收集信息**:
   ```bash
   # 系统信息
   python scripts/main.py --test
   cat memory_checkpoints.json | jq '.current_state'
   ```

2. **提供日志**:
   ```bash
   # 压缩日志文件
   tar -czf debug_logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/
   ```

3. **描述问题**:
   - 问题现象
   - 复现步骤
   - 期望结果
   - 实际结果

---
**版本历史:**
- v1.0 (2026-05-20): 创建API使用指南
- 基于: 夸克校园招聘已验证的API方案
- 目标: 提供完整的使用文档和支持信息

**最后更新**: 2026-05-20 10:15:00
**维护者**: 夸克项目系统