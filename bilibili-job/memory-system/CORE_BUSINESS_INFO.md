# CORE_BUSINESS_INFO.md - B站招聘数据爬取器

## 🎯 业务目标
**核心任务**: 爬取B站（哔哩哔哩）官方招聘网站的岗位数据

### 数据源信息
- **网站名称**: B站招聘（哔哩哔哩招聘）
- **网站地址**: https://jobs.bilibili.com
- **数据范围**: 社招岗位（全职）
- **目标数据**: 所有公开的招聘岗位信息

### 技术信息
- **API端点**: POST https://jobs.bilibili.com/api/srs/position/positionList
- **请求方法**: POST
- **认证方式**: Cookie + Headers认证
- **分页方式**: pageNum参数分页

## 📊 数据字段映射

### B站原始字段 → 标准字段
| B站字段名 | 标准字段名 | 说明 | 是否必需 |
|-----------|------------|------|----------|
| `id` | `position_id` | 岗位唯一ID | ✅ |
| `positionName` | `title` | 岗位标题 | ✅ |
| `postCodeName` | `category` | 岗位类别 | ✅ |
| `workLocation` | `location` | 工作地点 | ✅ |
| `pushTime` | `publish_time` | 发布时间 | ✅ |
| `positionDescription` | `description` | 岗位描述 | ✅ |
| `positionTypeName` | `position_type` | 岗位类型（全职/实习） | ✅ |
| `hotRecruit` | `is_hot` | 是否热招 | ✅ |
| `recruitType` | `recruit_type` | 招聘类型 | ✅ |

### 扩展字段（需要从详情页获取）
1. **部门信息** (`department`): 所属部门
2. **学历要求** (`education_requirement`): 学历要求
3. **工作经验** (`experience_requirement`): 工作经验要求
4. **薪资范围** (`salary_range`): 薪资范围
5. **岗位标签** (`tags`): 技能标签

## 🔧 技术配置

### 请求参数（固定部分）
```json
{
  "pageSize": 10,
  "positionName": "",
  "postCode": ["03", "05", "11", "08", "07"],
  "postCodeList": ["03", "05", "11", "08", "07"],
  "workLocationList": [],
  "workTypeList": ["3"],
  "positionTypeList": ["3"],
  "deptCodeList": [],
  "recruitType": 0,
  "practiceTypes": [],
  "onlyHotRecruit": 0
}
```

### 认证信息
- **必需Headers**:
  - `x-appkey: ops.ehr-api.auth`
  - `x-channel: social`
  - `x-usertype: 2`
  - `x-csrf: <动态获取>`
- **必需Cookie**: 包含buvid3、_uuid等认证信息

### 分页策略
- **每页数量**: 10条（固定）
- **最大页数**: 50页（500条数据）
- **页码参数**: `pageNum`（从1开始）

## 🚀 实施计划

### 阶段1：基础数据爬取 ✅
- [x] 配置API认证信息
- [x] 实现列表页数据爬取
- [ ] 实现分页逻辑
- [ ] 数据保存和导出

### 阶段2：详情数据补充
- [ ] 获取岗位详情页URL
- [ ] 爬取扩展字段信息
- [ ] 数据合并和去重

### 阶段3：优化和监控
- [ ] 添加错误重试机制
- [ ] 实现数据完整性检查
- [ ] 添加定时爬取功能

## 📈 数据质量要求

### 完整性检查（必须包含）
1. ✅ 岗位ID（唯一标识）
2. ✅ 岗位标题
3. ✅ 工作地点
4. ✅ 岗位类别
5. ✅ 发布时间
6. ✅ 详情链接
7. ✅ 岗位描述
8. ✅ 岗位类型

### 数据验证规则
1. **岗位ID**: 必须为数字且唯一
2. **发布时间**: 必须为有效的日期时间格式
3. **工作地点**: 不能为空
4. **岗位描述**: 至少包含工作职责和要求

## 🛡️ 风险控制

### 反爬虫风险
1. **频率控制**: 每页请求间隔2-3秒
2. **请求头**: 使用完整的浏览器User-Agent
3. **Cookie更新**: 定期检查Cookie有效性
4. **CSRF Token**: 动态获取和更新

### 数据安全
1. **本地存储**: 所有数据保存到本地
2. **实时备份**: 每爬取一页立即保存
3. **去重处理**: 基于position_id去重
4. **完整性检查**: 保存前验证数据完整性

## 📝 更新记录

### 2026-05-22 初始创建
- 基于夸克项目框架创建
- 配置B站API信息
- 定义数据字段映射
- 制定实施计划

### 待完成
- [ ] 实现实际的API请求逻辑
- [ ] 测试数据爬取功能
- [ ] 优化错误处理机制
- [ ] 添加浏览器爬取备选方案