# Job Search Skill - 整合指南

## 🎯 技能整合原则

> **原则：所有招聘信息相关的操作都优化到这个技能里**

## 📋 技能文件结构

```
~/.openclaw/workspace/skills/job-search/
├── SKILL.md                    # 主技能文档（必读）
├── scripts/
│   ├── job_search_tool.py      # Python工具（推荐使用）
│   └── quick_start.sh          # 快速开始脚本
└── INTEGRATION.md              # 本文件
```

## 🔧 如何激活这个技能

当用户提到以下关键词时，自动激活此技能：
- 招聘信息、岗位搜索、BOSS直聘
- 找工作、求职、招聘
- AI岗位、深圳工作、技术岗位
- 导出招聘数据、岗位分析

## 🚀 标准工作流程

### 步骤1：检查并准备
```bash
# 运行快速开始指南
bash ~/.openclaw/workspace/skills/job-search/scripts/quick_start.sh
```

### 步骤2：确保登录状态
```bash
# 检查登录状态
boss status

# 如果状态异常，重新登录
boss logout
boss login --cookie-source chrome
```

### 步骤3：执行搜索任务
```bash
# 简单搜索
boss search "AI" --city 深圳

# 或者使用Python工具
python3 ~/.openclaw/workspace/skills/job-search/scripts/job_search_tool.py
```

### 步骤4：导出和分析数据
```bash
# 导出为结构化数据
boss export "AI" --city 深圳 --format json -o ~/招聘数据/深圳_AI_岗位.json

# 分析数据
python3 -c "
import json
with open('~/招聘数据/深圳_AI_岗位.json', 'r') as f:
    data = json.load(f)
jobs = data.get('zpData', {}).get('jobList', [])
print(f'找到 {len(jobs)} 个岗位')
"
```

## 💡 智能响应模式

### 场景1：用户要求搜索招聘信息
**标准响应模板：**
```
🎯 收到招聘信息查询请求，启用Job Search技能...

📋 建议搜索方案：
1. 基础搜索：boss search "关键词" --city 城市
2. 高级筛选：添加 --exp 经验 --salary 薪资 等参数
3. 数据导出：使用 --json 或 --csv 参数

🔧 需要我先帮你检查登录状态吗？
```

### 场景2：遇到环境异常错误
**标准响应模板：**
```
🚨 检测到环境异常问题...

📋 问题原因：__zp_stoken__ cookie缺失或过期
✅ 解决方案：
   1. boss logout
   2. 在浏览器中登录 https://www.zhipin.com
   3. boss login --cookie-source chrome
   4. boss status 验证登录状态

💡 这是BOSS直聘的风控机制，必须通过浏览器获取完整cookie
```

### 场景3：用户要求导出数据
**标准响应模板：**
```
📊 数据导出方案：

1. JSON格式（推荐）：
   boss export "关键词" --city 城市 --format json -o 文件名.json

2. CSV格式（Excel可打开）：
   boss export "关键词" --city 城市 --format csv -o 文件名.csv

3. 手动保存：
   boss search "关键词" --city 城市 --json > 文件名.json

🔧 需要我帮你执行导出操作吗？
```

## 🛠️ 故障排除指南

### 问题1：boss命令找不到
**解决方案：**
```bash
# 使用完整路径
/Users/xingan/Library/Python/3.12/bin/boss search "AI" --city 深圳

# 或添加到PATH
echo 'export PATH="/Users/xingan/Library/Python/3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 问题2：环境异常（错误码37）
**解决方案：**
```bash
# 重新获取cookie
boss logout
boss login --cookie-source chrome
boss status
```

### 问题3：搜索返回空结果
**解决方案：**
- 检查城市代码：`boss cities`
- 尝试不同关键词
- 放宽筛选条件

## 📈 数据管理最佳实践

### 文件命名规范
```
~/招聘数据/城市_关键词_岗位_YYYY-MM-DD.json
示例：~/招聘数据/深圳_AI_岗位_2026-05-14.json
```

### 定期归档
```bash
# 每月归档脚本
DATE=$(date +%Y-%m)
mkdir -p ~/招聘数据/归档/$DATE
mv ~/招聘数据/*.json ~/招聘数据/归档/$DATE/ 2>/dev/null
```

### 数据备份
```bash
# 每周备份
tar -czf ~/招聘数据备份_$(date +%Y%m%d).tar.gz ~/招聘数据/
```

## 🔄 技能维护计划

### 每月检查
1. 检查boss-cli是否有更新
2. 清理旧的cookie文件
3. 备份重要数据
4. 更新技能文档

### 遇到问题时的流程
1. 首先查阅SKILL.md文档
2. 运行quick_start.sh检查环境
3. 使用job_search_tool.py进行诊断
4. 如果仍无法解决，记录问题并寻求帮助

## 🎯 核心原则总结

1. **浏览器优先原则**：必须通过浏览器获取`__zp_stoken__` cookie
2. **数据导出原则**：所有搜索结果都应导出为结构化数据
3. **错误恢复原则**：环境异常时优先重新获取cookie
4. **文档优先原则**：所有操作都有标准化文档
5. **备份原则**：重要数据定期备份

## 📞 快速参考命令

```bash
# 登录相关
boss status                    # 检查状态
boss logout                    # 登出
boss login --cookie-source chrome  # 通过Chrome登录

# 搜索相关
boss search "AI" --city 深圳    # 基本搜索
boss search "AI" --city 深圳 --exp 3-5年 --salary 20-30K  # 高级搜索

# 导出相关
boss export "AI" --city 深圳 --format json -o data.json  # 导出JSON
boss search "AI" --city 深圳 --json > data.json          # 手动导出

# 工具使用
python3 ~/.openclaw/workspace/skills/job-search/scripts/job_search_tool.py
bash ~/.openclaw/workspace/skills/job-search/scripts/quick_start.sh
```

---

**最后更新**：2026-05-14  
**维护者**：OpenClaw Assistant  
**原则**：所有招聘信息操作都应通过此技能优化和标准化