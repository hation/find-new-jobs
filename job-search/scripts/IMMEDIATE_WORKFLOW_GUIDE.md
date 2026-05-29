# 🚀 即时工作流使用指南（策略A）

## 📋 概述

即时工作流是**策略A**的实现，专门解决`__zp_stoken__`有效期短的问题。核心原则是：**登录后立即执行所有操作**，在3-5分钟的有效期内完成数据采集。

## 🎯 核心优势

### 1. **高效性**
- 登录后立即批量处理
- 减少重复登录次数
- 最大化利用token有效期

### 2. **稳定性**
- 内置超时和重试机制
- 错误处理和恢复
- 详细日志记录

### 3. **完整性**
- 完整35字段数据导出
- 包含搜索数据和详情数据
- 自动生成工作报告

## 🚀 快速开始

### 第一步：登录BOSS直聘
```bash
# 使用浏览器cookie登录（推荐）
boss login --cookie-source chrome

# 验证登录状态
boss status
# 应该显示: search=ok · recommend=ok
```

### 第二步：立即运行工作流
```bash
# 进入脚本目录
cd ~/.openclaw/workspace/skills/job-search/scripts

# 基本用法（深圳AI岗位，第1页）
python3 immediate_workflow.py --keyword AI --city 深圳

# 扩展用法（多页，多职位）
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 3 --max-details 15
```

### 第三步：查看结果
```bash
# 工具会自动显示输出目录
# 通常位于: ~/招聘数据/即时采集_时间戳/

# 查看工作报告
cat ~/招聘数据/即时采集_*/工作报告.md

# 打开Excel文件（CSV格式）
open ~/招聘数据/即时采集_*/Excel导出/*.csv
```

## 📊 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--keyword` | AI | 搜索关键词 |
| `--city` | 深圳 | 目标城市 |
| `--pages` | 1 | 搜索页数（每页15个职位） |
| `--max-details` | 10 | 每页最多获取详情数 |
| `--output-dir` | 自动生成 | 输出目录 |
| `--delay` | 2 | 页间延迟秒数 |

## 🔧 最佳实践配置

### 配置1：快速测试
```bash
# 测试连接和基本功能
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 1 --max-details 3
```

### 配置2：标准采集
```bash
# 采集完整数据（建议）
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 2 --max-details 10
```

### 配置3：批量采集
```bash
# 采集更多数据（需要稳定网络）
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 3 --max-details 15 --delay 3
```

### 配置4：多关键词采集
```bash
# 使用脚本批量处理多个关键词
for keyword in "AI" "人工智能" "机器学习" "深度学习"; do
    echo "采集: $keyword"
    python3 immediate_workflow.py --keyword "$keyword" --city 深圳 --pages 1 --max-details 10
    echo "等待5秒..."
    sleep 5
done
```

## 📁 输出文件结构

```
即时采集_20260514_223700/          # 时间戳目录
├── 工作报告.md                    # 完整工作报告
├── 搜索数据_第1页.json            # 原始搜索数据
├── 搜索数据_第2页.json            # （如果有多页）
├── 职位详情_1.json               # 单个职位详情
├── 职位详情_2.json               # （JSON格式）
├── ...
└── Excel导出/                    # Excel输出目录
    ├── 深圳_AI_岗位_即时采集_20260514_223700.csv    # 主数据文件
    ├── 原始数据_20260514_223700.json                # 所有详情数据
    └── （其他统计文件）
```

## 🎯 使用场景

### 场景1：日常市场监测
```bash
# 每天上午9点采集数据
# 添加到crontab
0 9 * * * cd ~/.openclaw/workspace/skills/job-search/scripts && python3 immediate_workflow.py --keyword AI --city 深圳 --pages 2 --max-details 10 >> ~/招聘数据/采集日志.txt 2>&1
```

### 场景2：竞品分析
```bash
# 分析竞争对手的招聘需求
python3 immediate_workflow.py --keyword "腾讯" --city 深圳 --pages 3
python3 immediate_workflow.py --keyword "阿里巴巴" --city 杭州 --pages 3
python3 immediate_workflow.py --keyword "字节跳动" --city 北京 --pages 3
```

### 场景3：技能需求分析
```bash
# 分析市场技能需求
python3 immediate_workflow.py --keyword "Python" --city 深圳 --pages 2
python3 immediate_workflow.py --keyword "Java" --city 北京 --pages 2
python3 immediate_workflow.py --keyword "前端" --city 上海 --pages 2
```

### 场景4：薪资调研
```bash
# 调研各城市薪资水平
python3 immediate_workflow.py --keyword "AI工程师" --city 深圳 --pages 2
python3 immediate_flowflow.py --keyword "AI工程师" --city 北京 --pages 2
python3 immediate_workflow.py --keyword "AI工程师" --city 上海 --pages 2
python3 immediate_workflow.py --keyword "AI工程师" --city 广州 --pages 2
```

## 🔧 故障排除

### 问题1：登录状态异常
```
❌ boss命令不可用
💡 请确保: boss-cli已安装且PATH设置正确
```
**解决方案**:
```bash
# 检查boss命令
which boss
# 如果找不到，手动设置PATH
export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"

# 重新登录
boss login --cookie-source chrome
```

### 问题2：Token过期
```
❌ 环境异常 (__zp_stoken__ 已过期)
```
**解决方案**:
```bash
# 重新登录后立即运行
boss logout
boss login --cookie-source chrome
# 在3分钟内运行工作流
python3 immediate_workflow.py --keyword AI --city 深圳
```

### 问题3：网络超时
```
⏱️  命令超时
```
**解决方案**:
```bash
# 增加超时时间（修改工具源代码）
# 或减少采集数量
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 1 --max-details 5
```

### 问题4：数据不完整
```
❌ 没有获取到任何职位详情
```
**解决方案**:
```bash
# 检查搜索关键词
python3 immediate_workflow.py --keyword "人工智能" --city 深圳

# 尝试其他城市
python3 immediate_workflow.py --keyword AI --city 北京
```

## 📈 性能优化建议

### 1. **网络优化**
```bash
# 使用更快的网络连接
# 减少延迟参数
python3 immediate_workflow.py --delay 1
```

### 2. **批量优化**
```bash
# 合理设置页面和详情数量
# 每页10-15个详情，2 secondary 页面是最佳平衡
python3 immediate_workflow.py --pages 2 --max-details 12
```

### 3. **定时优化**
```bash
# 在网络较好的时段运行
# 如：上午10点，下午3点
```

### 4. **存储优化**
```bash
# 定期清理旧数据
find ~/招聘数据 -name "即时采集_*" -type d -mtime +30 -exec rm -rf {} \;
```

## 🎯 成功指标

### 指标1：成功率
- ✅ 搜索成功率 > 90%
- ✅ 详情获取率 > 70%
- ✅ 数据导出成功率 100%

### 指标2：性能指标
- ⏱️  单页处理时间 < 60秒
- 📊 每分钟处理 5-8个职位
- 💾 数据完整率 > 80%

### 指标3：数据质量
- 📝 岗位描述完整率 > 90%
- 🎯 技能要求完整率 > 95%
- 💰 薪资信息完整率 > 98%

## 🔄 更新和维护

### 定期检查
```bash
# 检查工具更新
cd ~/.openclaw/workspace/skills/job-search/scripts
git status  # 如果有git仓库

# 检查依赖
pip3 list | grep boss-cli
```

### 日志监控
```bash
# 查看运行日志
tail -f ~/招聘数据/采集日志.txt

# 分析错误日志
grep -i "error\|失败\|异常" ~/招聘数据/*.log
```

### 数据备份
```bash
# 每月备份一次
tar -czf 招聘数据_$(date +%Y%m).tar.gz ~/招聘数据/
# 上传到云存储或外部硬盘
```

## 📞 技术支持

### 常见问题解答
**Q: 工具运行很慢怎么办？**
A: 减少`--pages`和`--max-details`参数，增加`--delay`

**Q: 总是获取不到详情怎么办？**
A: 检查登录状态，确保`boss status`显示`search=ok`

**Q: 导出的Excel文件乱码怎么办？**
A: 使用支持UTF-8的Excel版本，或使用文本编辑器打开CSV文件

**Q: 可以同时运行多个工作流吗？**
A: 不建议，可能会触发BOSS直聘的风控机制

### 获取帮助
```bash
# 查看帮助
python3 immediate_workflow.py --help

# 调试模式（查看详细日志）
python3 immediate_workflow.py --keyword AI --city 深圳 --pages 1 2>&1 | tee debug.log

# 检查具体错误
grep -A5 -B5 "ERROR\|异常\|失败" debug.log
```

## 🎉 开始使用

现在你已经准备好使用即时工作流了！记住关键步骤：

1. **登录**: `boss login --cookie-source chrome`
2. **验证**: `boss status` (确保`search=ok`)
3. **执行**: `python3 immediate_workflow.py --keyword AI --city 深圳`
4. **查看**: 检查输出目录中的工作报告和Excel文件

祝你使用愉快！如果有任何问题，请参考本指南或运行`--help`查看详细参数说明。

---
**最后更新**: 2026-05-14  
**版本**: v1.0  
**作者**: OpenClaw Assistant  
**适用场景**: BOSS直聘数据即时采集、市场监测、竞品分析