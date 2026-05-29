# 拼多多招聘爬取器 - 阶段1

## 🎯 **阶段1目标：基础API爬取**

### **已完成的工作**
1. ✅ **项目配置**：基于夸克项目完整架构
2. ✅ **API信息整合**：请求参数、响应结构、数据字段映射
3. ✅ **爬取器开发**：PDD专用API爬取器
4. ✅ **测试工具**：交互式测试脚本

### **技术架构**
```
pdd-job/
├── config/                    # 配置文件
│   ├── .env                  # 环境配置
│   ├── api_auth.json         # API认证配置
│   └── project_config.json   # 项目配置
├── src/crawler/              # 爬取器代码
│   └── pdd_crawler.py       # 主爬取器类
├── run_stage1.py            # 测试脚本
├── requirements.txt         # 完整依赖
├── requirements_minimal.txt # 最小依赖
└── install_dependencies.sh  # 安装脚本
```

### **核心功能**
- **API连接测试**：验证认证信息和API可访问性
- **分页爬取**：支持多页数据爬取
- **数据解析**：解析API响应，提取6个基础字段
- **数据保存**：JSON格式输出
- **错误处理**：重试机制和错误日志

### **基础字段（阶段1）**
1. **position_id**：岗位代码 (code)
2. **position_name**：岗位名称 (name)
3. **work_location**：工作地点 (workLocation)
4. **position_category**：岗位类别 (job)
5. **update_time_str**：更新时间 (updateTime)
6. **update_timestamp**：更新时间戳 (updateDate)

### **使用方法**

#### **1. 安装依赖**
```bash
# 方法1：使用安装脚本
chmod +x install_dependencies.sh
./install_dependencies.sh

# 方法2：手动安装
pip install -r requirements_minimal.txt
```

#### **2. 配置检查**
确保以下文件存在并正确配置：
- `config/.env` - 环境配置
- `config/api_auth.json` - API认证配置
- `config/project_config.json` - 项目配置

#### **3. 运行测试**
```bash
# 交互式测试
python3 run_stage1.py

# 直接运行主爬取器
python3 -c "from src.crawler.pdd_crawler import main; main()"
```

#### **4. 测试选项**
1. **检查环境配置** - 验证文件和目录
2. **测试API连接** - 验证认证和API可访问性
3. **运行小规模测试** - 爬取1页数据
4. **运行完整爬取** - 爬取多页数据
5. **运行所有测试** - 完整测试流程

### **配置文件说明**

#### **`.env` 环境配置**
```bash
# API配置
PDD_API_FULL_URL=https://careers.pddglobalhr.com/api/recruit/position/list
PDD_API_METHOD=POST
PDD_COOKIE_NANO_FP=你的Cookie

# 请求参数
PAGE_PARAM=page
SIZE_PARAM=pageSize
DEFAULT_PAGE_SIZE=10

# 响应结构
SUCCESS_FIELD=success
ERROR_CODE_FIELD=errorCode
LIST_FIELD=list
TOTAL_FIELD=total
SUCCESS_CODE=1000000
```

#### **`api_auth.json` API认证配置**
包含完整的API端点、请求头、参数映射等信息。

### **错误处理**

#### **常见错误及解决方案**
1. **认证失败**：检查Cookie是否有效
2. **API连接失败**：检查网络和API端点
3. **数据解析失败**：检查响应结构是否变化
4. **分页错误**：检查分页参数

#### **重试机制**
- 最大重试次数：3次
- 重试延迟：5秒
- 错误日志：保存到`logs/pdd_stage1.log`

### **数据输出**

#### **JSON格式**
```json
[
  {
    "position_id": "T015294",
    "position_name": "web前端高级开发工程师（广告投放&媒体运营方向）",
    "work_location": "上海",
    "position_category": "技术类",
    "update_time_str": "2026-05-21",
    "update_timestamp": 1779352494000,
    "detail_url": "https://careers.pddglobalhr.com/jobs/T015294",
    "crawl_time": "2026-05-22T15:30:00.123456",
    "raw_data": { ... }
  }
]
```

#### **输出位置**
- 数据文件：`output/pdd_stage1/pdd_positions_YYYYMMDD_HHMMSS.json`
- 日志文件：`logs/pdd_stage1.log`
- 测试报告：`output/stage1_report_YYYYMMDD_HHMMSS.json`

### **性能指标**

#### **测试环境**
- Python 3.8+
- 网络连接正常
- Cookie有效

#### **预期性能**
- 单页请求时间：2-5秒
- 数据解析时间：<1秒
- 并发支持：阶段1为单线程

### **阶段1限制**

#### **已知限制**
1. **详情页信息**：无法获取完整12个字段
2. **反爬虫参数**：`anti_content`使用固定值
3. **浏览器方案**：阶段1只实现API爬取
4. **数据导出**：只支持JSON格式

#### **待解决问题**
1. **详情页URL模式**：需要调查
2. **完整字段获取**：需要详情页信息
3. **反爬虫策略**：需要动态生成`anti_content`

### **下一步计划**

#### **阶段2（等你提供详情页信息后）**
1. **详情页爬取**：获取完整岗位信息
2. **完整字段提取**：12个核心字段
3. **数据导出增强**：支持Excel/CSV格式
4. **浏览器方案**：备用爬取方案

#### **经验沉淀**
1. **更新检查清单**：记录拼多多特定检查项
2. **完善教训记录**：记录遇到的问题和解决方案
3. **优化模板系统**：将解决方案反馈到夸克项目模板

### **开发日志**

#### **2026-05-22 15:30**
- ✅ 完成项目配置和API信息整合
- ✅ 开发PDD专用API爬取器
- ✅ 创建测试工具和安装脚本
- ✅ 编写阶段1文档

#### **下一步**
1. 运行测试验证功能
2. 记录测试结果和经验
3. 准备阶段2开发

### **联系信息**
- **项目状态**：阶段1开发完成
- **下一步依赖**：需要详情页信息
- **经验沉淀**：已建立模板系统

---

**阶段1开发完成，准备测试！** 🚀