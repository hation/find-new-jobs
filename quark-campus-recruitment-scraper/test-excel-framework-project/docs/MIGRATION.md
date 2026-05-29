# 🚀 招聘爬取方案迁移模板

## 🎯 **迁移目标**
将夸克校园招聘爬取方案迁移到其他公司招聘系统

## 📊 **组件复用分析**

### ✅ **可以直接复用的组件（80%）**

#### **1. 架构框架（100%复用）**
```python
# 智能选择器框架
crawler_selector_optimized.py
    ├── QuarkCrawlerSelectorOptimized  # 改名为 CompanyCrawlerSelector
    ├── test_api_connection()          # API连接测试
    ├── get_api_failure_reason()       # 失败原因分析
    ├── ask_user_for_switch()          # 用户交互询问
    └── smart_crawl_with_user_interaction()  # 智能爬取流程

# 统一入口框架
quark_crawler.py
    ├── 命令行参数解析
    ├── 模式选择逻辑
    ├── 状态查询功能
    └── 数据导出功能

# 数据处理框架
merge_to_excel.py                     # Excel导出
detailed_data_check.py                # 数据完整性检查
```

#### **2. 配置文件模板（100%复用结构）**
```json
{
  "api_endpoint": "新公司的API地址",
  "authentication": {
    "csrf_token": "新公司的CSRF令牌",
    "cookies": {},
    "headers": {}
  },
  "parameters": {
    "categories": "筛选参数",
    "pageIndex": 1,
    "pageSize": 10
  }
}
```

### ⚠️ **需要定制的业务组件（20%）**

#### **1. API爬取器定制点**
```python
# 需要修改的部分：
api_crawler_configurable.py
    ├── API端点和参数映射
    ├── 请求头和认证方式
    ├── 响应数据解析逻辑
    ├── 岗位数据字段映射
    └── 分页逻辑和总数计算
```

#### **2. 浏览器爬取器定制点**
```python
# 需要修改的部分：
browser_crawler.py
    ├── 页面URL和选择器
    ├── 筛选条件交互
    ├── 分页导航逻辑
    ├── 岗位详情页提取
    └── 反爬虫处理策略
```

## 🛠️ **迁移步骤**

### **第1步：创建新项目结构**
```bash
# 1. 创建新公司项目目录
mkdir new_company_recruitment_scraper
cd new_company_recruitment_scraper

# 2. 复制可复用框架
cp ../quark-campus-recruitment-scraper/quark_crawler.py .
cp ../quark-campus-recruitment-scraper/merge_to_excel.py .
cp ../quark-campus-recruitment-scraper/detailed_data_check.py .

# 3. 创建scripts目录和框架
mkdir scripts config output
```

### **第2步：配置智能选择器**
```python
# scripts/crawler_selector_optimized.py
# 只需要修改类名和导入
class NewCompanyCrawlerSelectorOptimized:
    # 其他代码保持不变
    # 只需要更新API爬取器和浏览器爬取器的导入
```

### **第3步：定制API爬取器**
```python
# scripts/api_crawler_configurable.py
# 重点修改以下部分：

class NewCompanyApiCrawlerConfigurable:
    def __init__(self, config_path=None):
        # 1. 更新API端点
        self.api_url = "https://new-company.com/api/positions"
        
        # 2. 更新请求参数映射
        self.base_params = {
            "page": 1,          # 新公司的页码参数名
            "size": 10,         # 新公司的页大小参数名
            "category": ""      # 新公司的筛选参数
        }
    
    def fetch_page(self, page_index=1, page_size=10):
        # 3. 更新请求逻辑（POST/GET，参数格式）
        # 4. 更新响应解析逻辑
        # 5. 更新数据提取逻辑
    
    def _parse_position_data(self, raw_data):
        # 6. 更新字段映射
        return {
            "position_id": raw_data.get("id"),
            "position_name": raw_data.get("title"),  # 新公司的字段名
            "work_location": raw_data.get("location"),
            # ... 其他字段
        }
```

### **第4步：定制浏览器爬取器**
```python
# scripts/browser_crawler.py
# 重点修改以下部分：

class NewCompanyCampusScraper:
    def __init__(self, config=None):
        # 1. 更新页面URL
        self.list_url = "https://new-company.com/careers"
        
        # 2. 更新页面选择器
        self.selectors = {
            "position_list": ".job-list .item",          # 岗位列表选择器
            "position_title": ".job-title",              # 岗位标题选择器
            "position_link": ".job-link",                # 详情链接选择器
            "pagination": ".pagination",                 # 分页选择器
            "next_page": ".next-page",                   # 下一页选择器
        }
    
    def scrape_positions(self):
        # 3. 更新页面交互逻辑
        # 4. 更新数据提取逻辑
```

### **第5步：配置认证信息**
```json
// config/api_auth.json
{
  "api_endpoint": "https://new-company.com/api/positions",
  "authentication": {
    "csrf_token": "从浏览器获取的新公司CSRF",
    "cookies": {
      "SESSION": "新公司的会话令牌",
      "XSRF-TOKEN": "新公司的XSRF令牌"
    },
    "headers": {
      "User-Agent": "Mozilla/5.0...",
      "Content-Type": "application/json",
      "Referer": "https://new-company.com/careers"
    }
  },
  "parameters": {
    "page": 1,
    "size": 10,
    "categories": "技术类,产品类,运营类"
  }
}
```

## 📋 **迁移检查清单**

### **API方案迁移检查项**
- [ ] API端点URL确认
- [ ] 请求方法确认（GET/POST）
- [ ] 认证方式确认（CSRF/Cookie/OAuth）
- [ ] 请求参数格式确认
- [ ] 响应数据格式确认
- [ ] 分页参数确认（page/size/total）
- [ ] 筛选参数确认
- [ ] 数据字段映射确认

### **浏览器方案迁移检查项**
- [ ] 页面URL确认
- [ ] 页面元素选择器确认
- [ ] 筛选条件交互确认
- [ ] 分页导航确认
- [ ] 详情页提取确认
- [ ] 反爬虫策略确认

### **通用框架检查项**
- [ ] 类名和导入更新
- [ ] 配置文件路径更新
- [ ] 输出目录结构确认
- [ ] 命令行参数更新
- [ ] 错误处理逻辑确认

## 🚀 **快速迁移脚本**

创建一个自动化迁移脚本：

```python
# migrate_to_new_company.py
import os
import shutil

def migrate_quark_to_new_company(new_company_name):
    """迁移夸克方案到新公司"""
    
    # 定义源和目标
    quark_dir = "quark-campus-recruitment-scraper"
    new_dir = f"{new_company_name}_recruitment_scraper"
    
    # 1. 创建新目录
    os.makedirs(new_dir, exist_ok=True)
    os.makedirs(f"{new_dir}/scripts", exist_ok=True)
    os.makedirs(f"{new_dir}/config", exist_ok=True)
    os.makedirs(f"{new_dir}/output", exist_ok=True)
    
    # 2. 复制通用框架
    shutil.copy(f"{quark_dir}/quark_crawler.py", f"{new_dir}/company_crawler.py")
    shutil.copy(f"{quark_dir}/merge_to_excel.py", f"{new_dir}/merge_to_excel.py")
    shutil.copy(f"{quark_dir}/detailed_data_check.py", f"{new_dir}/detailed_data_check.py")
    
    # 3. 复制智能选择器（稍后手动修改）
    shutil.copy(f"{quark_dir}/scripts/crawler_selector_optimized.py", 
                f"{new_dir}/scripts/crawler_selector_optimized.py")
    
    # 4. 创建配置文件模板
    create_config_template(new_dir, new_company_name)
    
    print(f"✅ 迁移完成！请在 {new_dir} 目录中继续定制")
```

## 💡 **最佳实践建议**

### **1. 增量迁移策略**
```bash
# 第一步：先迁移框架
cp crawler_selector_optimized.py  # 智能选择器框架
cp quark_crawler.py              # 统一入口框架

# 第二步：测试框架
python3 company_crawler.py --mode status

# 第三步：逐步定制API和浏览器爬取器
```

### **2. 测试驱动迁移**
```python
# 创建测试用例
def test_new_company_api():
    """测试新公司API连接"""
    # 1. 测试API端点
    # 2. 测试认证信息
    # 3. 测试数据解析
    # 4. 测试分页逻辑
```

### **3. 文档驱动开发**
```markdown
# 新公司招聘系统分析文档
## API接口分析
- 端点：https://company.com/api/positions
- 方法：POST
- 参数：{page: 1, size: 10, category: "tech"}

## 页面结构分析
- 列表页选择器：.job-list .item
- 详情页选择器：.job-detail
- 分页选择器：.pagination
```

## 📞 **技术支持**

### **遇到问题时检查**
1. **API连接失败**：检查CSRF令牌和Cookie
2. **数据解析失败**：检查响应结构和字段映射
3. **页面交互失败**：检查选择器和页面结构
4. **分页逻辑错误**：检查分页参数和总数计算

### **快速调试命令**
```bash
# 测试API连接
python3 -c "from scripts.api_crawler_configurable import NewCompanyApiCrawlerConfigurable; c = NewCompanyApiCrawlerConfigurable(); print(c.test_api_connection())"

# 测试页面元素
python3 -c "from scripts.browser_crawler import NewCompanyCampusScraper; s = NewCompanyCampusScraper(); print(s.test_page_elements())"
```

---

**迁移完成标志**：`python3 company_crawler.py --mode optimized` 能够成功爬取新公司岗位数据