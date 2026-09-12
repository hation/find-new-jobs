# 销售岗位采集工具集（sales/）

一键采集多家大厂招聘官网的销售类岗位，并汇总导出为 Excel。

## 功能概览

- 采集 **6 个平台**：美团、滴滴、腾讯、字节跳动、蚂蚁、夸克
- 按各平台**官方岗位类别**精准抓取（销售 + 部分相关类别）
- 自动抓取每个岗位的**岗位职责 + 任职要求**
- 统一合并为 **Excel 汇总表**，含各平台独立 sheet 和数据统计

## 目录结构

```
sales/
├── collect_didi.py        滴滴（销售/商业分析/职能与支持/战略/安全）
├── collect_meituan.py     美团（销售类别，全国）
├── collect_tencent.py     腾讯（销售、服务与支持/战略与投资）
├── collect_bytedance.py   字节跳动（销售/市场/IT支持，深圳）
├── collect_anti.py        蚂蚁（官方API关键词 key=销售）
├── collect_quark.py       夸克（全量岗位 + 本地销售关键词过滤）
├── merge_to_excel.py      合并所有平台数据 → Excel
├── bytedance_config.json  字节签名/cookie（会过期，勿提交到 git）
├── bytedance_config.example.json  字节配置模板
└── output/                采集结果（JSON + Excel，git 已忽略）
```

## 快速开始

```bash
# 1. 安装依赖（一次性）
pip3 install requests pandas openpyxl

# 2. 采集各平台（可只跑需要的平台）
python3 sales/collect_didi.py
python3 sales/collect_meituan.py
python3 sales/collect_tencent.py
python3 sales/collect_bytedance.py
python3 sales/collect_anti.py
python3 sales/collect_quark.py

# 3. 合并导出 Excel
python3 sales/merge_to_excel.py
```

最后生成的 Excel 位于 `sales/output/销售岗位汇总_日期.xlsx`。

## 各平台说明

| 平台 | 脚本 | 抓取类别 | 认证要求 |
|------|------|---------|---------|
| 美团 | collect_meituan.py | 销售（类别 11010，全国） | 无 |
| 滴滴 | collect_didi.py | 销售/商业分析/职能与支持/战略/安全 | 无 |
| 腾讯 | collect_tencent.py | 销售、服务与支持 / 战略与投资 | 无 |
| 字节跳动 | collect_bytedance.py | 销售/市场/IT支持（深圳） | **签名+cookie，会过期** |
| 蚂蚁 | collect_anti.py | key=销售 关键词搜索 | cookie（5月份至今有效） |
| 夸克 | collect_quark.py | 全量+本地过滤 | cookie + CSRF |

## 字节跳动签名刷新（重要）

字节的 API 需要 `_signature` 签名 + cookie，**有时效性（几小时到一天）**，过期后脚本会失败。刷新方法：

1. 浏览器打开 `https://jobs.bytedance.com/experienced/position`
2. 按 `F12` → `Network`（网络）面板 → 刷新页面
3. 找到名为 `search/job/posts` 的请求
4. 复制：
   - URL 中 `_signature=` 后面的值 → 填入配置的 `_signature`
   - `Request Headers` 里的 `cookie` 值 → 填入配置的 `cookies`
5. 保存到 `sales/bytedance_config.json`，重新运行脚本

> 配置模板见 `sales/bytedance_config.example.json`。此文件含登录凭据，**请勿提交到 git**（已由 .gitignore 排除）。

## 输出字段说明

Excel 每行包含 13 列：

| 列 | 说明 |
|----|------|
| 平台 | 美团/滴滴/腾讯/字节跳动/蚂蚁/夸克 |
| 岗位名称 | 职位标题 |
| 工作地点 | 城市 |
| 部门 | 所属部门/BG |
| 岗位类别 | 官方类别（销售/市场/战略等） |
| 发布时间 | 发布日期 |
| 详情链接 | 官方职位页链接 |
| 薪资 | 部分平台未公开，多为空 |
| 学历要求 | 部分平台未公开 |
| 工作经验 | 部分平台有（如腾讯） |
| 岗位职责 | 完整职责描述 |
| 任职要求 | 完整任职要求 |
| 岗位编号 | 平台内部 ID |

## 常见问题

**Q: 某平台返回 0 条？**
可能是该平台 cookie/签名过期。腾讯/美团/滴滴无需认证，可直接重试；蚂蚁/夸克需检查 cookie；字节需刷新签名。

**Q: 数据过期怎么办？**
重新运行对应平台的采集脚本即可，会生成新的时间戳文件。`merge_to_excel.py` 自动使用每个平台**最新的**数据文件。

**Q: 想改城市/类别？**
- 美团：改 `collect_meituan.py` 中的 `cityList`（空=全国）
- 字节：改 `collect_bytedance.py` 中的 `CATEGORIES` 和 `LOCATION`
- 滴滴：改 `collect_didi.py` 中的 `JOB_TYPES`
