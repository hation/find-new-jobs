#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集联想中国社会招聘岗位：分页爬取 + 销售关键词过滤 + 详情(og:description)"""
import json
import os
import re
import time
import html as H
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
LIST_URL = "https://jobs.lenovo.com/zh_CN/careers/SearchJobs/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    "Accept": "text/html",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

# 联想中国社会招聘筛选
FILTERS = {
    "13036": "[12016619]",  # 地点=中国
    "7715": "[327883]",     # 招聘类型=社会招聘
    "listFilterMode": 1,
    "jobRecordsPerPage": 10,
}

SALES_KEYWORDS = ["销售", "客户", "大客户", "渠道", "商务", "市场", "营销", "BD", "Sales", "Account", "业务拓展", "招商", "区域"]


def fetch_page(offset):
    params = {**FILTERS, "jobOffset": offset}
    r = requests.get(LIST_URL, params=params, headers=HEADERS, timeout=30)
    html = r.text
    jobs = []
    # 按 article 卡片解析
    for m in re.finditer(r'<article class="article article--result">(.*?)</article>', html, re.S):
        card = m.group(1)
        title_m = re.search(r'<a href="(https://jobs\.lenovo\.com/zh_CN/careers/JobDetail/[^"]+)">\s*([^<]+?)\s*</a>', card)
        if not title_m:
            continue
        href, title = title_m.group(1), H.unescape(title_m.group(2)).strip()
        cat_m = re.search(r'<span class="paragraph">\s*([^<]+?)\s*</span>', card)
        loc_m = re.search(r'<span>([^<]*(?:中国|北京|上海|广州|深圳|武汉|成都|西安|大连|厦门|南京|杭州|苏州|天津|重庆|合肥|济南|福州|沈阳|长沙|郑州|青岛|宁波|无锡|佛山|东莞|珠海)[^<]*)</span>', card)
        jobs.append({
            "title": title,
            "href": href,
            "category": H.unescape(cat_m.group(1)).strip() if cat_m else "",
            "location": H.unescape(loc_m.group(1)).strip() if loc_m else "",
            "job_id": href.rstrip("/").split("/")[-1],
        })
    return jobs


def is_sales(job):
    cat = job["category"]
    title = job["title"]
    # 排除测试岗位
    if "evergreen" in title.lower() or title.lower().startswith("parent-"):
        return False
    # 排除明确的非销售类别
    if cat == "Accounting/Finance":
        return False
    if not cat and len(title) < 5:
        return False
    text = title + " " + cat
    return any(kw.lower() in text.lower() for kw in SALES_KEYWORDS)


def fetch_detail(href):
    """抓详情页 og:title / og:description"""
    try:
        r = requests.get(href, headers=HEADERS, timeout=30)
        html = r.text
        desc_m = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        title_m = re.search(r'<meta property="og:title" content="([^"]*)"', html)
        return {
            "title": H.unescape(title_m.group(1)).strip() if title_m else "",
            "description": H.unescape(desc_m.group(1)).strip() if desc_m else "",
        }
    except Exception as e:
        print(f"  ⚠️ 详情失败 {href}: {e}")
        return {"title": "", "description": ""}


def normalize(job, detail):
    desc = detail.get("description") or ""
    # og:description 通常是"岗位职责：xxx；任职要求：xxx"，拆开
    duty, req = "", ""
    for part in re.split(r"(?:任职要求|Qualifications)\s*[:：]?", desc):
        if not duty:
            duty = part
        else:
            req = part
    if "岗位职责" in duty:
        duty = duty.split("岗位职责", 1)[-1]
    return {
        "platform": "联想",
        "position_name": detail.get("title") or job["title"],
        "work_location": job["location"],
        "department": "",
        "category": job["category"],
        "publish_time": "",
        "detail_url": job["href"],
        "salary": "",
        "education": "",
        "experience": "",
        "job_duty": duty.replace("\n", " ").strip(),
        "job_requirement": req.replace("\n", " ").strip(),
        "source_id": job["job_id"],
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 联想：中国社会招聘全部岗位 + 销售过滤")
    all_jobs = []
    offset = 0
    while True:
        jobs = fetch_page(offset)
        if not jobs:
            break
        all_jobs.extend(jobs)
        print(f"  offset={offset}: 本页{len(jobs)}条, 累计{len(all_jobs)}")
        offset += len(jobs)
        time.sleep(0.8)
    print(f"✅ 共 {len(all_jobs)} 个岗位")
    sales = [j for j in all_jobs if is_sales(j)]
    print(f"🎯 命中销售关键词: {len(sales)} 个")
    data = []
    for i, job in enumerate(sales, 1):
        detail = fetch_detail(job["href"])
        data.append(normalize(job, detail))
        print(f"  [{i}/{len(sales)}] {job['title'][:35]}")
        time.sleep(0.8)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/lenovo_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "联想", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
