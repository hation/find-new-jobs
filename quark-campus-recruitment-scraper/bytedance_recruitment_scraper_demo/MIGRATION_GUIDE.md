# 🚀 字节跳动招聘爬取器迁移指南

## ✅ 已完成的工作

### 框架迁移
1. ✅ 统一入口: `bytedance_crawler.py`
2. ✅ 数据处理: `merge_to_excel.py`, `detailed_data_check.py`
3. ✅ 智能选择器: `crawler_selector_optimized.py`
4. ✅ 目录结构: 完整的项目结构

### 定制模板
1. ✅ API爬取器模板: `bytedance_api_crawler.py`
2. ✅ 配置文件模板: `config/api_auth.json`

## 🛠️ 下一步定制工作

### 1. 获取字节跳动API信息
```bash
# 打开字节跳动招聘网站
# https://jobs.bytedance.com/experienced

# 使用浏览器开发者工具:
# 1. 打开Network标签
# 2. 筛选XHR请求
# 3. 找到岗位列表API请求
# 4. 记录请求URL、方法、参数、头部
```

### 2. 填写配置文件
```json
{
  "api_endpoint": "实际的字节跳动API地址",
  "csrf_token": "从请求参数或Cookie中获取",
  "cookies": {
    "SESSION": "实际的会话Cookie",
    "XSRF-TOKEN": "实际的XSRF令牌"
  }
}
```

### 3. 实现API解析逻辑
修改 `bytedance_api_crawler.py` 中的:
- `fetch_page()`: 实现字节跳动的API请求逻辑
- `_parse_bytedance_response()`: 解析字节跳动的响应结构

### 4. 测试和验证
```bash
# 测试API连接
python3 scripts/bytedance_api_crawler.py

# 测试统一入口
python3 bytedance_crawler.py --mode status
```

## 📋 字节跳动特定信息

### 可能的关键信息
- **API端点**: `https://jobs.bytedance.com/api/xxx`
- **认证方式**: CSRF + Cookie
- **分页参数**: `page`, `page_size`
- **筛选参数**: `category`, `location`, `keyword`

### 数据字段映射参考
| 标准字段 | 字节跳动字段 |
|---------|-------------|
| position_id | id |
| position_name | title |
| work_location | city |
| department | department |
| salary_range | salary |

## 🚀 快速开始

```bash
# 1. 进入项目目录
cd bytedance_recruitment_scraper_demo

# 2. 配置认证信息
vim config/api_auth.json

# 3. 实现API解析
vim scripts/bytedance_api_crawler.py

# 4. 测试运行
python3 bytedance_crawler.py --mode smart
```

## 📞 遇到问题?

### 常见问题
1. **API端点错误**: 检查字节跳动招聘网站的实际API
2. **认证失败**: 检查CSRF令牌和Cookie是否有效
3. **数据解析失败**: 检查字节跳动的响应结构

### 调试建议
```python
# 在bytedance_api_crawler.py中添加调试代码
import pprint
pprint.pprint(response.json())  # 打印完整响应
```

---

**完成标志**: 能够成功爬取字节跳动招聘网站的岗位数据
