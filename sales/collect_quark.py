#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集夸克销售岗位：爬取全部岗位后按"类别含销售"或名称关键词过滤"""
import json
import os
import time
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
CONFIG_PATH = f"{BASE}/quark-campus-recruitment-scraper/config/api_auth.json"

SALES_KEYWORDS = ["销售", "大客户", "客户经理", "渠道", "商务", "BD", "地推", "招商", "区域经理", "直销", "业务拓展", "销售运营"]


def load_config():
    cfg = json.load(open(CONFIG_PATH))
    url = cfg["api_endpoint"] + "?_csrf=" + cfg["authentication"]["csrf_token"]
    return url, cfg["authentication"]["cookies"], cfg["authentication"]["headers"], cfg["parameters"].copy()


def fetch_page(url, cookies, headers, base, page, page_size):
    body = base.copy()
    body["categories"] = ""
    body["subCategories"] = ""
    body["pageIndex"] = page
    body["pageSize"] = page_size
    r = requests.post(url, headers=headers, cookies=cookies, json=body, timeout=30, allow_redirects=False)
    j = r.json()
    if not j.get("success"):
        print(f"  ⚠️ 第{page}页失败: {j.get('errorMsg')}")
        return [], 0
    content = j.get("content") or {}
    return content.get("datas") or [], content.get("totalCount", 0)


def is_sales(job):
    cats = " ".join(job.get("categories") or [])
    if "销售" in cats:
        return True
    name = job.get("name") or ""
    return any(kw.lower() in name.lower() for kw in SALES_KEYWORDS)


def normalize(job):
    jid = job.get("id", "")
    exp = job.get("experience") or {}
    exp_str = ""
    if exp and (exp.get("from") or exp.get("to")):
        f, t = exp.get("from"), exp.get("to")
        exp_str = f"{f}-{t}年" if f and t else (f"{f}年以上" if f else "经验不限")
    pub = job.get("publishTime")
    if isinstance(pub, (int, float)):
        try:
            pub = datetime.fromtimestamp(pub / 1000).strftime("%Y-%m-%d")
        except Exception:
            pub = str(pub)
    else:
        pub = (pub or "")[:16]
    return {
        "platform": "夸克",
        "position_name": job.get("name", ""),
        "work_location": ", ".join(job.get("workLocations") or []),
        "department": job.get("department") or "",
        "category": ", ".join(job.get("categories") or []),
        "publish_time": pub,
        "detail_url": job.get("positionUrl") or "",
        "salary": "",
        "education": (job.get("degree") or ""),
        "experience": exp_str,
        "job_duty": (job.get("description") or "").replace("\n", " "),
        "job_requirement": (job.get("requirement") or "").replace("\n", " "),
        "source_id": str(jid),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 夸克：爬取全部岗位后按销售过滤")
    url, cookies, headers, base = load_config()
    all_positions = []
    page, page_size = 1, 50
    total = None
    while True:
        items, total_now = fetch_page(url, cookies, headers, base, page, page_size)
        total = total_now if total_now else total
        if not items:
            break
        all_positions.extend(items)
        print(f"  第{page}页: {len(items)}条 (累计{len(all_positions)}/{total})")
        if total and len(all_positions) >= total:
            break
        page += 1
        time.sleep(1.5)
    print(f"✅ 共爬取 {len(all_positions)} 个岗位")
    data = [normalize(j) for j in all_positions if is_sales(j)]
    print(f"🎯 命中销售: {len(data)} 个")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/quark_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "夸克", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
