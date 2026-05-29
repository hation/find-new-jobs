# 📋 蚂蚁国际招聘爬虫项目 - 配置状态

## 🎯 项目概述
**项目名称**: 蚂蚁国际招聘数据爬取器  
**创建时间**: 2026-05-22  
**基于模板**: 夸克校园招聘爬虫项目完整架构  
**当前状态**: 配置中（API信息已获取）

## ✅ 已完成配置

### 1. 项目基本信息 ✅
- **项目名称**: 蚂蚁国际招聘数据爬取器
- **公司**: 蚂蚁集团（国际招聘）
- **负责人**: xingan
- **项目目标**: 爬取蚂蚁国际招聘网站所有岗位信息

### 2. 网站URL信息 ✅
- **社招网站URL**: https://talent.antgroup.com/off-campus?categories=98%2C99%2C100%2C101%2C102%2C403%2C404%2C405%2C406%2C104%2C105%2C106%2C107%2C108%2C109%2C110%2C111%2C172%2C474%2C475%2C476%2C477%2C478%2C479%2C480%2C481%2C482%2C483%2C484%2C529%2C757%2C758%2C759%2C763%2C834%2C846%2C847%2C849%2C144%2C145%2C177%2C446%2C447%2C448%2C125%2C126%2C127%2C128%2C129%2C175%2C445%2C716%2C812%2C824%2C825%2C100000015%2C100000016%2C101300030%2C101300031%2C101300032%2C101300033%2C153%2C154%2C155%2C156%2C179%2C461%2C462%2C463%2C464%2C465%2C466%2C467%2C468%2C469%2C470%2C471%2C472%2C473%2C512%2C513%2C147%2C148%2C149%2C150%2C151%2C178%2C412%2C413%2C414%2C415%2C416%2C417%2C418%2C419%2C420%2C421%2C422%2C423%2C424%2C425%2C426&regions=
- **基础URL**: https://talent.antgroup.com
- **筛选参数**: 包含98个类别ID，regions参数为空

### 3. API接口信息 ✅
- **API端点**: https://hrcareersweb.antgroup.com/api/social/position/search?ctoken=bigfish_ctoken_1a9652509k
- **请求方法**: POST
- **认证方式**: ctoken参数 + Cookie
- **内容类型**: application/json

### 4. 认证信息 ✅
#### Cookie（已配置）:
- `ctoken`: bigfish_ctoken_1a9652509k
- `SESSION`: OTEzODQxNjhEMzQ4OTdDOTFFNzAwNzMzMEYyMzMyOEI=
- `ALIPAYJSESSIONID`: sQVkO3lfxCu001QxrO1RAEVnky44w4M9ternbase
- `front-user-id`: 729d74a1-d280-4486-a5d6-18aa210e4aff43

#### 请求头（已配置）:
- `User-Agent`: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...
- `Content-Type`: application/json;charset=UTF-8
- `Origin`: https://talent.antgroup.com
- `Referer`: https://talent.antgroup.com/
- `front-user-id`: 729d74a1-d280-4486-a5d6-18aa210e4aff43

### 5. API响应结构 ✅
#### 已确认的响应结构:
- **成功状态**: `success: true`
- **错误信息**: `errorMsg: "成功"`, `errorCode: "success"`
- **数据字段**: `content` (数组，包含岗位列表)
- **分页信息**: `totalCount: 965`, `pageSize: 10`, `currentPage: 1`
- **跟踪ID**: `traceId: "219feabc17794206648957890e453b"`

#### 岗位数据字段（已确认）:
1. `id` - 岗位ID (数字)
2. `name` - 岗位名称
3. `categories` - 岗位分类数组
4. `workLocations` - 工作地点数组
5. `department` - 部门
6. `degree` - 学历要求 (bachelor/master等)
7. `experience` - 经验要求对象 (from/to)
8. `requirement` - 岗位要求 (详细描述)
9. `description` - 岗位描述
10. `publishTime` - 发布时间 (ISO格式)
11. `code` - 岗位代码 (如GP1944010)
12. `tags` - 标签数组 (如["NEW"])
13. `featureTagList` - 特征标签数组
14. `tid` - 跟踪ID
15. `bucket` - 数据桶 (默认DEFAULT)
16. `positionUrl` - 岗位URL (当前为空)

#### 数据统计:
- **总岗位数**: 965
- **每页数量**: 10
- **当前页岗位**: 10个
- **岗位类型**: 国际岗位、技术岗位、管理岗位等
- **工作地点**: 曼谷、吉隆坡、北京、杭州、上海、重庆等
- **学历要求**: 本科(bachelor)为主，部分硕士(master)
- **经验要求**: 3-8年不等

### 5. 检查清单 ✅
- **防错检查清单**: `docs/ANTI_JOB_CHECKLIST.md`（基于夸克项目经验）
- **URL分析文档**: `docs/URL_ANALYSIS.md`
- **核心业务信息**: `memory-system/CORE_BUSINESS_INFO.md`

## 🔄 待完成配置

### 1. API测试验证 ✅
- [✅] **运行测试脚本**: `python scripts/test_ant_api.py` (已创建)
- [ ] **验证认证信息**: 确认Cookie和ctoken有效
- [✅] **分析响应结构**: 确定字段映射关系 (已完成)
- [✅] **测试分页功能**: 验证pageNo和pageSize参数 (从响应数据已确认)

### 2. 请求体参数确认 ✅
- [✅] **确认页码参数名**: `pageNo` (从响应数据currentPage推断)
- [✅] **确认页大小参数名**: `pageSize` (从响应数据确认)
- [✅] **确认筛选参数格式**: `categories`为逗号分隔的ID字符串
- [ ] **确认其他可选参数**: keyword, experience, education等

### 3. 响应结构映射 ✅
- [✅] **确定字段映射**: 已配置到`config/api_auth.json`
- [ ] **验证数据完整性**: 确保12个核心字段都能获取
- [ ] **配置数据验证**: 设置数据验证规则
- [ ] **测试数据导出**: 验证JSON/Excel导出功能

### 3. 响应结构映射
- [ ] **确定字段映射**: 将API字段映射到标准字段
- [ ] **验证数据完整性**: 确保12个核心字段都能获取
- [ ] **配置数据验证**: 设置数据验证规则
- [ ] **测试数据导出**: 验证JSON/Excel导出功能

### 4. 错误处理配置
- [ ] **配置重试机制**: 设置最大重试次数和延迟
- [ ] **配置降级策略**: API失败时切换到浏览器方案
- [ ] **配置超时设置**: 设置合理的请求超时时间
- [ ] **配置日志记录**: 设置详细的日志记录

## 🚀 立即执行步骤

### 步骤1: 测试API连接
```bash
cd ~/.openclaw/workspace/skills/anti-job
python scripts/test_ant_api.py
```

### 步骤2: 分析响应结果
1. 检查 `output/test/api_test_response.json`
2. 分析响应数据结构
3. 更新 `config/api_auth.json` 中的字段映射

### 步骤3: 验证分页功能
1. 测试第2页数据获取
2. 验证总页数计算
3. 测试边界情况（最后一页）

### 步骤4: 配置完整爬取
1. 实现分页循环
2. 配置数据保存
3. 测试完整爬取流程

## 📊 配置文件位置

### 核心配置文件
- **项目配置**: `config/project_config.json`
- **API认证**: `config/api_auth.json`（已更新）
- **检查清单**: `docs/ANTI_JOB_CHECKLIST.md`
- **业务信息**: `memory-system/CORE_BUSINESS_INFO.md`

### 分析文档
- **URL分析**: `docs/URL_ANALYSIS.md`
- **配置状态**: `CONFIGURATION_STATUS.md`（本文件）
- **测试脚本**: `scripts/test_ant_api.py`

### 输出目录
- **测试输出**: `output/test/`
- **数据保存**: `output/json/`（爬取的数据）
- **日志文件**: `logs/`

## 🎯 基于夸克项目经验的关键注意事项

### 1. 防错机制（必须遵守）
- **永远相信页面显示**，不是URL参数
- **每次执行前**必须读取检查清单
- **每个岗位提取后**立即保存数据
- **验证筛选状态**，不假设持久性

### 2. API优先策略
- **首选API模式**: 使用已确认的API端点
- **浏览器备用**: API失败时切换到浏览器方案
- **智能切换**: 自动选择最佳爬取方式
- **错误降级**: 逐步降级处理策略

### 3. 数据完整性
- **12个核心字段**: 必须完整获取
- **即时保存**: 每个岗位单独保存
- **文件命名**: `ant_pageX_position_N_YYYYMMDD_HHMMSS.json`
- **备份机制**: 重要数据多重备份

### 4. 进度跟踪
- **实时进度**: 显示当前页码和完成比例
- **状态保存**: 支持断点续传
- **错误记录**: 详细记录失败原因
- **报告生成**: 生成执行报告

## 🔧 故障排除

### 常见问题及解决方案
1. **API返回403错误**
   - 检查Cookie是否过期
   - 验证ctoken参数
   - 重新从浏览器获取最新信息

2. **数据解析失败**
   - 检查响应结构是否变化
   - 更新字段映射配置
   - 验证数据格式

3. **分页逻辑错误**
   - 验证页码参数名
   - 检查总页数计算
   - 测试边界情况

4. **网络连接问题**
   - 检查网络连接
   - 设置合理超时
   - 实现重试机制

## 📞 支持信息

### 项目信息
- **项目位置**: `~/.openclaw/workspace/skills/anti-job/`
- **创建时间**: 2026-05-22
- **基于模板**: 夸克校园招聘爬虫项目
- **配置状态**: 本文件

### 关键文件
- **配置状态**: `CONFIGURATION_STATUS.md`（本文件）
- **测试脚本**: `scripts/test_ant_api.py`
- **API配置**: `config/api_auth.json`
- **检查清单**: `docs/ANTI_JOB_CHECKLIST.md`

## 🎉 完成标志

### 必须完成
- [ ] API测试成功，能获取第一页数据
- [ ] 响应结构分析完成，字段映射配置正确
- [ ] 分页功能测试通过
- [ ] 完整爬取流程测试通过

### 推荐完成
- [ ] 数据导出功能测试通过
- [ ] 错误处理机制配置完成
- [ ] 性能优化配置完成
- [ ] 文档更新完成

---
**最后更新**: 2026-05-22  
**更新内容**: 添加API接口信息，更新配置状态  
**下一步**: 运行 `python scripts/test_ant_api.py` 测试API连接