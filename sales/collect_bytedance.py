#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集字节跳动岗位：按官方类别(销售/市场/IT支持)采集，列表API自带完整职责与要求"""
import json
import os
import time
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
CONFIG_PATH = f"{BASE}/sales/bytedance_config.json"
API_URL = "https://jobs.bytedance.com/api/v1/search/job/posts"

CATEGORIES = {
    "销售": "6709824272505768200,6704215938645887239,6704215966085024003,6709824272459630861,6709824273038444807",
    "市场": "6704216950135851275,6704216021651163395",
    "IT支持": "6704217005358057732",
}
LOCATION = "CT_128"  # 深圳

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN",
    "Content-Type": "application/json",
    "Origin": "https://jobs.bytedance.com",
    "Referer": "https://jobs.bytedance.com/experienced/position",
    "Portal-Channel": "office",
    "Portal-Platform": "pc",
    "Website-Path": "society",
}


def load_auth():
    cfg = json.load(open(CONFIG_PATH))
    return cfg["_signature"], cfg["cookies"]


def fetch_page(signature, cookies, cats, offset, limit=10):
    params = {
        "keyword": "", "limit": limit, "offset": offset,
        "job_category_id_list": cats, "tag_id_list": "", "location_code_list": LOCATION,
        "subject_id_list": "", "recruitment_id_list": "", "portal_type": 2,
        "job_function_id_list": "", "storefront_id_list": "", "portal_entrance": 1,
        "_signature": signature,
    }
    body = {
        "keyword": "", "limit": limit, "offset": offset,
        "job_category_id_list": cats.split(","), "location_code_list": [LOCATION],
        "portal_type": 2, "portal_entrance": 1,
        "recruitment_id_list": [], "job_function_id_list": [], "tag_id_list": [], "storefront_id_list": [],
    }
    r = requests.post(API_URL, params=params, headers=HEADERS, cookies=cookies, json=body, timeout=30)
    j = r.json()
    if j.get("code") != 0:
        print(f"  ⚠️ 请求失败: code={j.get('code')} msg={j.get('msg')}")
        return [], 0
    d = j.get("data") or {}
    return d.get("job_post_list") or [], d.get("count") or 0


def normalize(job, cat_name):
    city = job.get("city_info") or {}
    jc = job.get("job_category") or {}
    pub = job.get("publish_time")
    pub_str = ""
    if pub:
        try:
            pub_str = datetime.fromtimestamp(pub / 1000).strftime("%Y-%m-%d")
        except Exception:
            pub_str = str(pub)
    return {
        "platform": "字节跳动",
        "position_name": job.get("title", ""),
        "work_location": city.get("name", ""),
        "department": "",
        "category": jc.get("name") or cat_name,
        "publish_time": pub_str,
        "detail_url": f"https://jobs.bytedance.com/experienced/position/{job.get('id')}/detail" if job.get("id") else "",
        "salary": "",
        "education": "",
        "experience": "",
        "job_duty": (job.get("description") or "").replace("\n", " "),
        "job_requirement": (job.get("requirement") or "").replace("\n", " "),
        "source_id": job.get("id", ""),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 字节跳动：类别采集", list(CATEGORIES.keys()))
    signature, cookies = load_auth()
    all_positions = []
    for cat_name, cats in CATEGORIES.items():
        offset, count = 0, None
        while True:
            items, count = fetch_page(signature, cookies, cats, offset)
            if not items:
                break
            for it in items:
                all_positions.append(normalize(it, cat_name))
            print(f"  {cat_name}: 已获取 {len(all_positions)} 条 (本类count={count})")
            offset += len(items)
            if offset >= count:
                break
            time.sleep(1)
    print(f"✅ 共爬取 {len(all_positions)} 个岗位")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/bytedance_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "字节跳动", "count": len(all_positions), "positions": all_positions}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
