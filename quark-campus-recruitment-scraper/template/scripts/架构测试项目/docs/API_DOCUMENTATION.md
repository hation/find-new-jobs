# 📚 API 文档模板

## 🎯 文档概览

### 📋 文档目的
本模板用于记录项目API的完整信息，包括：
- API端点定义和用法
- 认证机制说明
- 请求/响应格式规范
- 错误代码定义
- 使用示例和最佳实践

### 🔄 文档维护
- **负责人**: TODO: 填写API文档负责人
- **更新频率**: 每次API变更时更新
- **审核流程**: 代码审查 + 文档审查
- **版本控制**: 与代码版本同步

---

## 🏗️ API 架构

### API 分层设计
```
┌─────────────────────────────────────────┐
│           表现层 (Presentation)          │
│  • 请求/响应格式                        │
│  • 错误处理机制                         │
│  • 版本控制策略                         │
├─────────────────────────────────────────┤
│           业务层 (Business)              │
│  • 数据验证规则                         │
│  • 业务逻辑处理                         │
│  • 权限控制逻辑                         │
├─────────────────────────────────────────┤
│           数据层 (Data)                  │
│  • 数据访问接口                         │
│  • 数据转换逻辑                         │
│  • 缓存策略实现                         │
├─────────────────────────────────────────┤
│           基础设施层 (Infrastructure)    │
│  • 认证鉴权服务                         │
│  • 限流防护机制                         │
│  • 监控日志系统                         │
└─────────────────────────────────────────┘
```

### API 版本策略
```yaml
版本策略:
  当前版本: v1
  版本格式: 主版本.次版本.修订版本
  
版本管理:
  - 向后兼容: 次版本更新保持兼容
  - 重大变更: 主版本更新可能不兼容
  - 弃用策略: 提前3个月通知
  
版本标识:
  - URL路径: /api/v1/endpoint
  - 请求头: X-API-Version: v1
  - 响应头: X-API-Version: v1
```

---

## 🔐 认证与授权

### 1. 认证机制
#### CSRF Token + Cookie 认证（推荐）
```http
# 请求示例
GET /api/v1/positions?page=1 HTTP/1.1
Host: api.example.com
X-CSRF-Token: c6ea8927-62fd-42ab-9eab-d1f3da836dfc
Cookie: SESSION=abc123def456; XSRF-TOKEN=xyz789
User-Agent: Mozilla/5.0
Accept: application/json
```

#### Token 认证（备用方案）
```http
# 请求示例
GET /api/v1/positions?page=1 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-API-Key: your_api_key_here
```

### 2. 认证流程
```mermaid
sequenceDiagram
    participant C as 客户端
    participant S as 服务器
    
    Note over C,S: 首次认证流程
    
    C->>S: 1. 访问登录页面
    S-->>C: 2. 返回登录表单 + CSRF Token
    
    C->>S: 3. 提交登录信息（含CSRF Token）
    S->>S: 4. 验证凭证，生成会话
    
    S-->>C: 5. 设置会话Cookie
    S-->>C: 6. 返回认证成功
    
    Note over C,S: 后续API调用
    
    C->>S: 7. API请求（带Cookie和CSRF Token）
    S->>S: 8. 验证Cookie和CSRF Token
    S-->>C: 9. 返回API数据
```

### 3. 认证配置
```json
{
  "authentication": {
    "type": "csrf_cookie",
    "csrf_token": {
      "source": "url_param",
      "param_name": "_csrf",
      "example": "c6ea8927-62fd-42ab-9eab-d1f3da836dfc"
    },
    "cookies": {
      "required": ["SESSION", "XSRF-TOKEN"],
      "optional": ["USER_ID", "LANG"],
      "domain": ".example.com",
      "path": "/",
      "secure": true,
      "http_only": true
    },
    "headers": {
      "required": ["X-CSRF-Token", "User-Agent"],
      "optional": ["X-Requested-With", "Referer"]
    }
  }
}
```

### 4. 权限控制
```yaml
权限层级:
  公开权限:
    - GET /api/v1/positions (列表)
    - GET /api/v1/positions/{id} (详情)
    
  用户权限:
    - POST /api/v1/applications (申请职位)
    - GET /api/v1/profile (个人资料)
    
  管理员权限:
    - POST /api/v1/positions (创建职位)
    - PUT /api/v1/positions/{id} (更新职位)
    - DELETE /api/v1/positions/{id} (删除职位)
```

---

## 📡 API 端点

### 1. 岗位相关 API

#### 1.1 获取岗位列表
```http
GET /api/v1/positions
```

**查询参数**:
| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，从1开始 |
| pageSize | integer | 否 | 10 | 每页数量，最大50 |
| sort | string | 否 | create_time_desc | 排序字段 |
| category | string | 否 | - | 岗位类别 |
| location | string | 否 | - | 工作地点 |
| keyword | string | 否 | - | 搜索关键词 |

**请求示例**:
```bash
curl -X GET "https://api.example.com/api/v1/positions?page=1&pageSize=10&sort=create_time_desc" \
  -H "X-CSRF-Token: your_csrf_token" \
  -H "Cookie: SESSION=your_session_cookie"
```

**成功响应** (HTTP 200):
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "total": 152,
    "page": 1,
    "pageSize": 10,
    "totalPages": 16,
    "hasMore": true,
    "items": [
      {
        "id": "123456",
        "title": "后端开发工程师",
        "department": "技术部",
        "location": "北京",
        "experience": "3-5年",
        "education": "本科及以上",
        "salary": "20-40k",
        "description": "岗位描述内容...",
        "requirements": "岗位要求内容...",
        "createdAt": "2026-05-20T10:30:00Z",
        "updatedAt": "2026-05-20T10:30:00Z"
      }
    ]
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

**分页元数据**:
```json
{
  "pagination": {
    "current": 1,
    "pageSize": 10,
    "total": 152,
    "pages": 16
  },
  "sorting": {
    "field": "createdAt",
    "order": "desc"
  },
  "filtering": {
    "applied": ["category", "location"],
    "available": {
      "categories": ["技术", "产品", "运营", "设计"],
      "locations": ["北京", "上海", "深圳", "杭州"]
    }
  }
}
```

#### 1.2 获取岗位详情
```http
GET /api/v1/positions/{id}
```

**路径参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| id | string | 是 | 岗位ID |

**请求示例**:
```bash
curl -X GET "https://api.example.com/api/v1/positions/123456" \
  -H "X-CSRF-Token: your_csrf_token" \
  -H "Cookie: SESSION=your_session_cookie"
```

**成功响应** (HTTP 200):
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "id": "123456",
    "title": "后端开发工程师",
    "department": {
      "id": "tech",
      "name": "技术部",
      "parent": "engineering"
    },
    "location": {
      "city": "北京",
      "district": "海淀区",
      "address": "中关村软件园",
      "coordinates": {
        "latitude": 39.983,
        "longitude": 116.307
      }
    },
    "requirements": {
      "experience": "3-5年",
      "education": "本科及以上",
      "skills": ["Java", "Spring", "MySQL", "Redis"],
      "certifications": ["PMP", "OCP"],
      "languages": ["英语四级以上"]
    },
    "compensation": {
      "salary": "20-40k",
      "bonus": "年终奖",
      "stock": "期权",
      "benefits": ["五险一金", "补充医疗保险", "年度体检", "带薪年假"]
    },
    "description": {
      "overview": "负责公司核心业务系统开发...",
      "responsibilities": [
        "负责后端服务架构设计和开发",
        "参与系统性能优化和稳定性保障",
        "编写高质量、可维护的代码"
      ],
      "challenges": [
        "高并发场景下的系统设计",
        "复杂业务逻辑的抽象和实现"
      ]
    },
    "process": {
      "steps": ["简历筛选", "技术面试", "HR面试", "Offer"],
      "timeline": "2-3周",
      "contact": "hr@example.com"
    },
    "statistics": {
      "views": 1250,
      "applications": 85,
      "favorites": 42,
      "createdAt": "2026-05-15T09:00:00Z",
      "updatedAt": "2026-05-20T14:30:00Z",
      "expiresAt": "2026-06-15T23:59:59Z"
    },
    "related": {
      "similarPositions": ["123457", "123458"],
      "teamMembers": ["user1", "user2"]
    }
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

#### 1.3 搜索岗位
```http
GET /api/v1/positions/search
```

**查询参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| q | string | 是 | 搜索关键词 |
| fields | string | 否 | 搜索字段（title,description,requirements） |
| highlight | boolean | 否 | 是否返回高亮片段 |

**请求示例**:
```bash
curl -X GET "https://api.example.com/api/v1/positions/search?q=Java工程师&highlight=true" \
  -H "X-CSRF-Token: your_csrf_token" \
  -H "Cookie: SESSION=your_session_cookie"
```

**成功响应** (HTTP 200):
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "query": "Java工程师",
    "total": 24,
    "tookMs": 45,
    "hits": [
      {
        "id": "123456",
        "title": "Java后端开发工程师",
        "score": 0.95,
        "highlight": {
          "title": "<em>Java</em>后端开发<em>工程师</em>",
          "description": "需要精通<em>Java</em>编程...",
          "requirements": "熟悉<em>Java</em>相关技术栈..."
        }
      }
    ],
    "facets": {
      "departments": [
        {"value": "技术部", "count": 18},
        {"value": "平台部", "count": 6}
      ],
      "locations": [
        {"value": "北京", "count": 12},
        {"value": "上海", "count": 8},
        {"value": "深圳", "count": 4}
      ],
      "experienceLevels": [
        {"value": "1-3年", "count": 8},
        {"value": "3-5年", "count": 12},
        {"value": "5年以上", "count": 4}
      ]
    }
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

### 2. 筛选器 API

#### 2.1 获取筛选选项
```http
GET /api/v1/filters
```

**请求示例**:
```bash
curl -X GET "https://api.example.com/api/v1/filters" \
  -H "X-CSRF-Token: your_csrf_token" \
  -H "Cookie: SESSION=your_session_cookie"
```

**成功响应** (HTTP 200):
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "categories": [
      {
        "id": "tech",
        "name": "技术类",
        "subcategories": [
          {"id": "backend", "name": "后端开发"},
          {"id": "frontend", "name": "前端开发"},
          {"id": "mobile", "name": "移动开发"},
          {"id": "qa", "name": "测试"}
        ]
      },
      {
        "id": "product",
        "name": "产品类",
        "subcategories": [
          {"id": "pm", "name": "产品经理"},
          {"id": "ux", "name": "用户体验"}
        ]
      }
    ],
    "locations": [
      {"id": "beijing", "name": "北京", "count": 45},
      {"id": "shanghai", "name": "上海", "count": 32},
      {"id": "shenzhen", "name": "深圳", "count": 28}
    ],
    "experienceLevels": [
      {"id": "intern", "name": "实习生", "count": 12},
      {"id": "junior", "name": "初级(0-2年)", "count": 25},
      {"id": "mid", "name": "中级(2-5年)", "count": 48},
      {"id": "senior", "name": "高级(5年以上)", "count": 32}
    ],
    "educationLevels": [
      {"id": "college", "name": "大专", "count": 18},
      {"id": "bachelor", "name": "本科", "count": 75},
      {"id": "master", "name": "硕士", "count": 32},
      {"id": "doctor", "name": "博士", "count": 5}
    ],
    "salaryRanges": [
      {"id": "0-10k", "name": "10k以下", "count": 15},
      {"id": "10-20k", "name": "10-20k", "count": 38},
      {"id": "20-30k", "name": "20-30k", "count": 42},
      {"id": "30-50k", "name": "30-50k", "count": 25},
      {"id": "50k+", "name": "50k以上", "count": 8}
    ],
    "updateTime": "2026-05-20T10:30:00Z"
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

### 3. 统计数据 API

#### 3.1 获取数据统计
```http
GET /api/v1/statistics
```

**查询参数**:
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| period | string | 否 | 统计周期（day, week, month） |
| startDate | string | 否 | 开始日期（YYYY-MM-DD） |
| endDate | string | 否 | 结束日期（YYYY-MM-DD） |

**请求示例**:
```bash
curl -X GET "https://api.example.com/api/v1/statistics?period=month" \
  -H "X-CSRF-Token: your_csrf_token" \
  -H "Cookie: SESSION=your_session_cookie"
```

**成功响应** (HTTP 200):
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    "period": {
      "start": "2026-05-01",
      "end": "2026-05-20",
      "days": 20
    },
    "summary": {
      "totalPositions": 152,
      "newPositions": 28,
      "updatedPositions": 45,
      "totalViews": 12500,
      "totalApplications": 850,
      "avgResponseTime": "2.3天"
    },
    "trends": {
      "dailyNewPositions": [
        {"date": "2026-05-01", "count": 5},
        {"date": "2026-05-02", "count": 3},
        {"date": "2026-05-03", "count": 7}
      ],
      "categoryDistribution": [
        {"category": "技术类", "count": 85, "percentage": 56},
        {"category": "产品类", "count": 32, "percentage": 21},
        {"category": "运营类", "count": 20, "percentage": 13},
        {"category": "设计类", "count": 15, "percentage": 10}
      ],
      "locationDistribution": [
        {"location": "北京", "count": 45, "percentage": 30},
        {"location": "上海", "count": 32, "percentage": 21},
        {"location": "深圳", "count": 28, "percentage": 18},
        {"location": "杭州", "count": 25, "percentage": 16},
        {"location": "其他", "count": 22, "percentage": 15}
      ]
    },
    "insights": [
      "技术类岗位占比最高（56%）",
      "北京地区岗位最多（30%）",
      "平均响应时间2.3天",
      "本月新增岗位28个"
    ]
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

---

## ⚠️ 错误处理

### 错误响应格式
```json
{
  "success": false,
  "code": 400,
  "message": "具体错误描述",
  "error": {
    "type": "VALIDATION_ERROR",
    "details": {
      "field": "page",
      "reason": "必须为正整数"
    },
    "documentation": "https://api.example.com/docs/errors#validation-error",
    "requestId": "req_1234567890abcdef"
  },
  "timestamp": "2026-05-20T10:30:00Z"
}
```

### 错误代码表
| HTTP状态码 | 错误代码 | 描述 | 解决方案 |
|------------|----------|------|----------|
| 400 | BAD_REQUEST | 请求参数错误 | 检查请求参数格式 |
| 401 | UNAUTHORIZED | 未认证 | 提供有效的认证信息 |
| 403 | FORBIDDEN | 权限不足 | 检查用户权限 |
| 404 | NOT_FOUND | 资源不存在 | 检查资源ID是否正确 |
| 429 | TOO_MANY_REQUESTS | 请求过于频繁 | 降低请求频率 |
| 500 | INTERNAL_SERVER_ERROR | 服务器内部错误 | 联系技术支持 |
| 503 | SERVICE_UNAVAILABLE | 服务不可用 | 稍后重试 |

### 详细错误说明
#### 认证错误 (401)
```json
{
  "success": false,
  "code": 401,
  "message": "认证失败",
  "error": {
    "type": "AUTHENTICATION_FAILED",
    "details": {
      "reason": "CSRF令牌无效",
      "hint": "请重新登录获取新的CSRF令牌"
    },
    "documentation": "https://api.example.com/docs/authentication"
  }
}
```

#### 限流错误 (429)
```json
{
  "success": false,
  "code": 429,
  "message": "请求过于频繁",
  "error": {
    "type": "RATE_LIMIT_EXCEEDED",
    "details": {
      "limit": "100请求/小时",
      "remaining": 0,
      "resetAt": "2026-05-20T11:30:00Z"
    },
    "documentation": "https://api.example.com/docs/rate-limits"
  }
}
```

#### 验证错误 (400)
```json
{
  "success": false,
  "code": 400,
  "message": "参数验证失败",
  "error": {
    "type": "VALIDATION_ERROR",
    "details": [
      {
        "field": "page",
        "message": "必须为正整数",
        "value": "abc"
      },
      {
        "field": "pageSize", 
        "message": "必须在1到50之间",
        "value": 100
      }
    ]
  }
}
```

---

## 🚀 使用示例

### Python 示例
```python
import requests
import json

class APIClient:
    def __init__(self, base_url, csrf_token, cookies):
        self.base_url = base_url
        self.csrf_token = csrf_token
        self.cookies = cookies
        self.session = requests.Session()
        
    def get_positions(self, page=1, page_size=10, **filters):
        """获取岗位列表"""
        url = f"{self.base_url}/api/v1/positions"
        params = {
            'page': page,
            'pageSize': page_size,
            **filters
        }
        
        headers = {
            'X-CSRF-Token': self.csrf_token,
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                cookies=self.cookies,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API错误: {response.status_code}")
                print(f"响应内容: {response.text[:200]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return None
            
    def get_position_detail(self, position_id):
        """获取岗位详情"""
        url = f"{self.base_url}/api/v1/positions/{position_id}"
        
        headers = {
            'X-CSRF-Token': self.csrf_token,
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.get(
                url,
                headers=headers,
                cookies=self.cookies,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API错误: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return None

# 使用示例
if __name__ == "__main__":
    # 配置认证信息
    config = {
        'base_url': 'https://api.example.com',
        'csrf_token': 'your_csrf_token_here',
        'cookies': {
            'SESSION': 'your_session_cookie_here'
        }
    }
    
    # 创建客户端
    client = APIClient(**config)
    
    # 获取第一页数据
    result = client.get_positions(page=1, page_size=10)
    
    if result and result.get('success'):
        data = result.get('data', {})
        items = data.get('items', [])
        
        print(f"获取到 {len(items)} 条数据")
        print(f"总页数: {data.get('totalPages', 0)}")
        
        # 处理数据
        for item in items:
            print(f"ID: {item.get('id')}")
            print(f"标题: {item.get('title')}")
            print(f"地点: {item.get('location')}")
            print("-" * 50)
    else:
        print("获取数据失败")
```

### JavaScript 示例
```javascript
class APIClient {
    constructor(baseUrl, csrfToken, cookies) {
        this.baseUrl = baseUrl;
        this.csrfToken = csrfToken;
        this.cookies = cookies;
    }
    
    async getPositions(page = 1, pageSize = 10, filters = {}) {
        const url = new URL(`${this.baseUrl}/api/v1/positions`);
        
        // 设置查询参数
        url.searchParams.append('page', page);
        url.searchParams.append('pageSize', pageSize);
        
        // 添加筛选参数
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                url.searchParams.append(key, filters[key]);
            }
        });
        
        const headers = {
            'X-CSRF-Token': this.csrfToken,
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        };
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: headers,
                credentials: 'include', // 自动发送cookies
                mode: 'cors'
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                console.error(`API错误: ${response.status}`);
                const errorText = await response.text();
                console.error(`响应内容: ${errorText.substring(0, 200)}`);
                return null;
            }
        } catch (error) {
            console.error(`请求异常: ${error}`);
            return null;
        }
    }
    
    async getPositionDetail(positionId) {
        const url = `${this.baseUrl}/api/v1/positions/${positionId}`;
        
        const headers = {
            'X-CSRF-Token': this.csrfToken,
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/json'
        };
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: headers,
                credentials: 'include',
                mode: 'cors'
            });
            
            if (response.ok) {
                return await response.json();
            } else {
                console.error(`API错误: ${response.status}`);
                return null;
            }
        } catch (error) {
            console.error(`请求异常: ${error}`);
            return null;
        }
    }
}

// 使用示例
(async () => {
    // 配置认证信息
    const config = {
        baseUrl: 'https://api.example.com',
        csrfToken: 'your_csrf_token_here'
    };
    
    // 创建客户端
    const client = new APIClient(config.baseUrl, config.csrfToken);
    
    // 获取第一页数据
    const result = await client.getPositions(1, 10);
    
    if (result && result.success) {
        const data = result.data || {};
        const items = data.items || [];
        
        console.log(`获取到 ${items.length} 条数据`);
        console.log(`总页数: ${data.totalPages || 0}`);
        
        // 处理数据
        items.forEach(item => {
            console.log(`ID: ${item.id}`);
            console.log(`标题: ${item.title}`);
            console.log(`地点: ${item.location}`);
            console.log('-'.repeat(50));
        });
    } else {
        console.log('获取数据失败');
    }
})();
```

### cURL 示例
```bash
#!/bin/bash

# 配置变量
BASE_URL="https://api.example.com"
CSRF_TOKEN="your_csrf_token_here"
SESSION_COOKIE="your_session_cookie_here"

# 函数：获取岗位列表
get_positions() {
    local page=$1
    local page_size=$2
    
    curl -X GET "${BASE_URL}/api/v1/positions?page=${page}&pageSize=${page_size}" \
      -H "X-CSRF-Token: ${CSRF_TOKEN}" \
      -H "Cookie: SESSION=${SESSION_COOKIE}" \
      -H "User-Agent: Mozilla/5.0" \
      -H "Accept: application/json" \
      --silent \
      | python3 -m json.tool
}

# 函数：获取岗位详情
get_position_detail() {
    local position_id=$1
    
    curl -X GET "${BASE_URL}/api/v1/positions/${position_id}" \
      -H "X-CSRF-Token: ${CSRF_TOKEN}" \
      -H "Cookie: SESSION=${SESSION_COOKIE}" \
      -H "User-Agent: Mozilla/5.0" \
      -H "Accept: application/json" \
      --silent \
      | python3 -m json.tool
}

# 使用示例
echo "获取第一页岗位列表:"
get_positions 1 10

echo -e "\n获取岗位详情:"
get_position_detail "123456"
```

---

## 🔧 最佳实践

### 1. 请求优化
```python
# 好的实践
def optimized_request():
    """优化的API请求"""
    
    # 1. 设置合理的超时
    timeout = (5, 30)  # 连接5秒，读取30秒
    
    # 2. 使用会话保持连接
    session = requests.Session()
    
    # 3. 启用连接池
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=10,
        max_retries=3
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    # 4. 设置合理的请求头
    headers = {
        'User-Agent': 'Your-App/1.0.0',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    # 5. 实现指数退避重试
    for attempt in range(3):
        try:
            response = session.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            if attempt < 2:  # 前两次重试
                time.sleep(2 ** attempt)  # 指数退避
            else:
                raise
```

### 2. 错误处理最佳实践
```python
class RobustAPIClient:
    """健壮的API客户端"""
    
    def handle_error(self, response):
        """统一错误处理"""
        
        if response.status_code == 401:
            # 认证错误，需要重新登录
            self.refresh_auth()
            raise AuthenticationError("请重新登录")
            
        elif response.status_code == 429:
            # 限流错误，等待后重试
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            raise RateLimitError(f"请等待{retry_after}秒后重试")
            
        elif response.status_code >= 500:
            # 服务器错误，记录并通知
            self.log_error(response)
            self.notify_admin(f"服务器错误: {response.status_code}")
            raise ServerError("服务器内部错误，请稍后重试")
            
        else:
            # 其他错误
            try:
                error_data = response.json()
                raise APIError(
                    f"API错误: {error_data.get('message', '未知错误')}",
                    code=response.status_code,
                    details=error_data.get('error', {})
                )
            except ValueError:
                raise APIError(f"HTTP错误: {response.status_code}")
```

### 3. 缓存策略
```python
import requests_cache
from datetime import timedelta

class CachedAPIClient:
    """带缓存的API客户端"""
    
    def __init__(self):
        # 安装缓存
        requests_cache.install_cache(
            'api_cache',
            backend='sqlite',
            expire_after=timedelta(hours=1),
            allowable_codes=[200],
            allowable_methods=['GET']
        )
        
    def get_with_cache(self, url, force_refresh=False):
        """带缓存的GET请求"""
        
        if force_refresh:
            # 强制刷新缓存
            with requests_cache.disabled():
                response = requests.get(url)
        else:
            response = requests.get(url)
            
        # 检查是否来自缓存
        if getattr(response, 'from_cache', False):
            print(f"从缓存获取: {url}")
        else:
            print(f"从服务器获取: {url}")
            
        return response
```

### 4. 监控和日志
```python
import logging
from datadog import statsd

class MonitoredAPIClient:
    """带监控的API客户端"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def monitored_request(self, method, url, **kwargs):
        """带监控的请求"""
        
        start_time = time.time()
        
        try:
            response = requests.request(method, url, **kwargs)
            elapsed = time.time() - start_time
            
            # 记录成功指标
            statsd.increment('api.requests.total')
            statsd.histogram('api.response_time', elapsed)
            
            if response.status_code == 200:
                statsd.increment('api.requests.success')
            else:
                statsd.increment('api.requests.error')
                
            # 记录详细日志
            self.logger.info(
                f"API请求: {method} {url} - "
                f"状态: {response.status_code} - "
                f"耗时: {elapsed:.2f}s"
            )
            
            return response
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            # 记录失败指标
            statsd.increment('api.requests.failed')
            
            # 记录错误日志
            self.logger.error(
                f"API请求失败: {method} {url} - "
                f"错误: {str(e)} - "
                f"耗时: {elapsed:.2f}s"
            )
            
            raise
```

---

## 📊 性能指标

### 服务级别目标 (SLO)
```yaml
可靠性目标:
  可用性: 99.9%
  错误率: < 0.1%
  成功请求率: > 99%

性能目标:
  P95延迟: < 500ms
  P99延迟: < 1000ms
  吞吐量: > 1000请求/分钟

数据质量目标:
  数据完整性: > 99.5%
  数据新鲜度: < 5分钟
  数据准确性: > 99%
```

### 监控指标
```python
# 关键性能指标
KPIS = {
    'availability': 'api.availability',
    'error_rate': 'api.error_rate', 
    'latency_p95': 'api.latency.p95',
    'latency_p99': 'api.latency.p99',
    'throughput': 'api.requests.per_minute',
    'cache_hit_rate': 'api.cache.hit_rate',
    'data_completeness': 'api.data.completeness',
    'data_freshness': 'api.data.freshness'
}
```

### 容量规划
```yaml
容量规划:
  当前容量:
    请求处理: 1000 RPM
    数据存储: 10GB
    并发连接: 100
    
  扩容阈值:
    CPU使用率: 70%
    内存使用率: 80%
    磁盘使用率: 85%
    
  扩容策略:
    垂直扩展: 增加资源
    水平扩展: 增加实例
    缓存优化: 减少后端负载
```

---

## 🔄 变更管理

### API 变更流程
```
API变更流程:
1. 变更提案
   ├── 描述变更内容
   ├── 分析影响范围
   ├── 制定迁移计划
   └── 评估风险等级

2. 开发实现
   ├── 实现新版本
   ├── 保持向后兼容
   ├── 更新文档
   └── 编写测试

3. 测试验证
   ├── 单元测试
   ├── 集成测试
   ├── 性能测试
   └── 兼容性测试

4. 部署发布
   ├── 灰度发布
   ├── 监控指标
   ├── 收集反馈
   └── 问题修复

5. 生命周期管理
   ├── 版本支持周期
   ├── 弃用通知
   ├── 迁移协助
   └── 最终下线
```

### 版本兼容性矩阵
| API版本 | 支持开始 | 支持结束 | 兼容性 | 迁移指南 |
|---------|----------|----------|--------|----------|
| v1.0    | 2026-01-01 | 2026-12-31 | ✅ 稳定 | - |
| v1.1    | 2026-06-01 | 2027-05-31 | ✅ 向后兼容 | 自动升级 |
| v2.0    | 2027-01-01 | 2028-12-31 | ⚠️ 部分不兼容 | [迁移指南](...) |

---

## 📞 支持与反馈

### 技术支持
- **文档**: https://api.example.com/docs
- **状态页面**: https://status.example.com
- **问题反馈**: api-support@example.com
- **紧急联系**: +86-10-12345678

### 社区资源
- **GitHub**: https://github.com/example/api-client
- **Stack Overflow**: [tag:example-api]
- **开发者论坛**: https://forum.example.com
- **知识库**: https://kb.example.com/api

### 服务等级协议 (SLA)
```yaml
服务承诺:
  正常运行时间: 99.9%
  响应时间: < 24小时（工作日）
  问题解决: < 72小时（紧急问题）
  数据备份: 每日自动备份
  
支持时间:
  工作日: 9:00-18:00 (北京时间)
  紧急支持: 7x24小时
  
联系方式:
  邮箱: api-support@example.com
  电话: +86-10-12345678
  在线聊天: 官网右下角
```

---

## 📝 附录

### A. 请求头参考
| 请求头 | 必填 | 示例值 | 说明 |
|--------|------|--------|------|
| X-CSRF-Token | 是 | c6ea8927-62fd-42ab... | CSRF令牌 |
| Cookie | 是 | SESSION=abc123... | 会话Cookie |
| User-Agent | 是 | Mozilla/5.0 | 用户代理 |
| Accept | 是 | application/json | 接受格式 |
| Accept-Language | 否 | zh-CN,zh;q=0.9 | 语言偏好 |
| Accept-Encoding | 否 | gzip, deflate, br | 编码偏好 |
| Connection | 否 | keep-alive | 连接类型 |

### B. 响应头参考
| 响应头 | 示例值 | 说明 |
|--------|--------|------|
| X-API-Version | v1 | API版本 |
| X-RateLimit-Limit | 100 | 请求限制 |
| X-RateLimit-Remaining | 95 | 剩余请求 |
| X-RateLimit-Reset | 1621500000 | 重置时间戳 |
| Retry-After | 60 | 重试等待秒数 |
| Cache-Control | max-age=300 | 缓存控制 |
| Content-Type | application/json | 内容类型 |

### C. 状态码参考
| 状态码 | 含义 | 处理建议 |
|--------|------|----------|
| 200 | 成功 | 正常处理响应数据 |
| 201 | 创建成功 | 资源创建成功 |
| 204 | 无内容 | 请求成功但无返回数据 |
| 400 | 错误请求 | 检查请求参数 |
| 401 | 未授权 | 提供有效认证 |
| 403 | 禁止访问 | 检查权限设置 |
| 404 | 未找到 | 检查资源ID |
| 429 | 请求过多 | 降低请求频率 |
| 500 | 服务器错误 | 联系技术支持 |
| 502 | 网关错误 | 稍后重试 |
| 503 | 服务不可用 | 检查服务状态 |

### D. 数据格式规范
```json
{
  "命名规范": {
    "字段名": "lower_snake_case",
    "常量名": "UPPER_SNAKE_CASE",
    "类名": "PascalCase",
    "方法名": "lowerCamelCase"
  },
  "时间格式": {
    "ISO8601": "YYYY-MM-DDTHH:mm:ssZ",
    "日期": "YYYY-MM-DD",
    "时间": "HH:mm:ss",
    "时区": "UTC"
  },
  "数值格式": {
    "整数": "不带小数点和前导零",
    "小数": "保留两位小数",
    "百分比": "0.95 表示95%",
    "货币": "保留两位小数，无货币符号"
  }
}
```

---

**API文档版本**: v1.0.0  
**最后更新**: 2026-05-20  
**维护团队**: API开发组  
**文档状态**: ✅ 正式发布  
**使用建议**: 开发前完整阅读，遇到问题时参考错误处理部分