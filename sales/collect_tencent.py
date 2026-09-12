#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集腾讯岗位：按官方类别(销售/战略与投资)采集，详情接口获取任职要求"""
import json
import os
import time
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
LIST_URL = "https://careers.tencent.com/tencentcareer/api/post/Query"
DETAIL_URL = "https://careers.tencent.com/tencentcareer/api/post/ByPostId"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://careers.tencent.com/search.html",
}

CATEGORIES = {  # 类别ID: 名称
    40005001: "销售",
    40011: "战略与投资",
}


def fetch_list(cat_id, page_index, page_size=10):
    params = {
        "timestamp": int(time.time() * 1000), "countryId": "", "cityId": "",
        "bgIds": "", "productId": "", "categoryId": cat_id, "parentCategoryId": "",
        "attrId": 1, "keyword": "", "pageIndex": page_index, "pageSize": page_size,
        "language": "zh-cn", "area": "cn",
    }
    r = requests.get(LIST_URL, params=params, headers=HEADERS, timeout=30)
    j = r.json()
    if j.get("Code") != 200:
        print(f"  ⚠️ 请求失败: code={j.get('Code')} msg={j.get('Message')}")
        return [], 0
    d = j.get("Data") or {}
    return d.get("Posts") or [], d.get("Count") or 0


def fetch_detail(post_id):
    params = {"timestamp": int(time.time() * 1000), "postId": post_id, "language": "zh-cn"}
    for _ in range(3):
        try:
            r = requests.get(DETAIL_URL, params=params, headers=HEADERS, timeout=30)
            j = r.json()
            if j.get("Code") == 200:
                return j.get("Data") or {}
        except Exception as e:
            print(f"  ⚠️ 详情失败 {post_id}: {e}")
        time.sleep(3)
    return {}


def normalize(job, detail, type_name):
    return {
        "platform": "腾讯",
        "position_name": job.get("RecruitPostName", ""),
        "work_location": job.get("LocationName", ""),
        "department": job.get("BGName", ""),
        "category": job.get("CategoryName") or type_name,
        "publish_time": (job.get("LastUpdateTime") or "")[:16],
        "detail_url": job.get("PostURL") or f"https://careers.tencent.com/jobdesc.html?postId={job.get('PostId')}",
        "salary": "",
        "education": "",
        "experience": job.get("RequireWorkYearsName") or "",
        "job_duty": (detail.get("Responsibility") or job.get("Responsibility") or "").replace("\n", " "),
        "job_requirement": (detail.get("Requirement") or "").replace("\n", " "),
        "source_id": job.get("PostId", ""),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 腾讯：类别采集", list(CATEGORIES.values()))
    all_posts = []
    for cat_id, name in CATEGORIES.items():
        page, type_count = 1, 0
        while True:
            items, count = fetch_list(cat_id, page)
            if not items:
                break
            for it in items:
                it["_type"] = name
            all_posts.extend(items)
            type_count += len(items)
            print(f"  {name}: 本类已获取 {type_count}/{count} 条")
            if type_count >= count:
                break
            page += 1
            time.sleep(1)
    print(f"✅ 列表共 {len(all_posts)} 个岗位，抓取详情...")
    data = []
    for i, job in enumerate(all_posts, 1):
        detail = fetch_detail(job.get("PostId"))
        data.append(normalize(job, detail, job.get("_type", "")))
        if i % 20 == 0 or i == len(all_posts):
            print(f"  [{i}/{len(all_posts)}] 详情完成")
        time.sleep(1)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/tencent_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "腾讯", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
