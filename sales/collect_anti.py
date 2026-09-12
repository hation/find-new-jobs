#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集蚂蚁国际销售岗位：官方API key=销售 关键词搜索"""
import json
import os
import time
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
CONFIG_PATH = f"{BASE}/anti-job/config/ant_api_auth.json"


def load_config():
    cfg = json.load(open(CONFIG_PATH))
    url = cfg["api_endpoints"]["full_url"]
    cookies = {k: v for k, v in cfg["authentication"]["cookies"].items()}
    headers = {k: v for k, v in cfg["authentication"]["headers"].items() if not k.startswith("_")}
    return url, cookies, headers


def fetch_page(url, cookies, headers, page, page_size):
    body = {
        "regions": "", "categories": "", "subCategories": "",
        "bgCode": "", "socialQrCode": "",
        "pageIndex": page, "pageSize": page_size,
        "channel": "group_official_site", "language": "zh",
        "key": "销售",
    }
    for attempt in range(4):
        try:
            r = requests.post(url, headers=headers, cookies=cookies, json=body, timeout=30)
            j = r.json()
            if j.get("success"):
                content = j.get("content") or []
                return content, j.get("totalCount", 0)
            print(f"  ⚠️ 第{page}页第{attempt+1}次失败: {j.get('errorMsg')}，稍后重试")
        except Exception as e:
            print(f"  ⚠️ 第{page}页第{attempt+1}次异常: {e}，稍后重试")
        time.sleep(8 * (attempt + 1))
    return [], 0


def normalize(job):
    jid = job.get("id", "")
    return {
        "platform": "蚂蚁",
        "position_name": job.get("name", ""),
        "work_location": ", ".join(job.get("workLocations") or []),
        "department": job.get("department") or "",
        "category": ", ".join(job.get("categories") or []),
        "publish_time": (job.get("publishTime") or "")[:16],
        "detail_url": job.get("positionUrl") or f"https://talent.antgroup.com/off-campus/position/{jid}" if jid else "",
        "salary": "",
        "education": "",
        "experience": "",
        "job_duty": (job.get("description") or "").replace("\n", " "),
        "job_requirement": (job.get("requirement") or "").replace("\n", " "),
        "source_id": str(jid),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 蚂蚁：官方API key=销售 关键词搜索")
    url, cookies, headers = load_config()
    all_positions = []
    page, page_size = 1, 10
    total = None
    while True:
        items, total_now = fetch_page(url, cookies, headers, page, page_size)
        total = total_now if total_now else total
        if not items:
            break
        all_positions.extend(items)
        print(f"  第{page}页: {len(items)}条 (累计{len(all_positions)}/{total})")
        if total and len(all_positions) >= total:
            break
        page += 1
        time.sleep(1)
    print(f"✅ 共爬取 {len(all_positions)} 个销售岗")
    data = [normalize(j) for j in all_positions]
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/anti_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "蚂蚁", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
