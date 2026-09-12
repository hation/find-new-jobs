#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集美团销售岗位：使用官方销售类别(11010/1101001)，全国范围"""
import json
import os
import time
import uuid
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
API_URL = "https://zhaopin.meituan.com/api/official/job/getJobList"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://zhaopin.meituan.com",
    "Referer": "https://zhaopin.meituan.com/web/social",
    "X-Requested-With": "XMLHttpRequest",
}


def build_data(page, page_size):
    ts = int(time.time() * 1000)
    return {
        "page": {"pageNo": page, "pageSize": page_size},
        "jobShareType": "1",
        "keywords": "",
        "cityList": [],
        "department": [],
        "jfJgList": [{"code": "11010", "subCode": ["1101001"]}],
        "jobType": [{"code": "3", "subCode": []}],
        "typeCode": [],
        "specialCode": [],
        "u_query_id": uuid.uuid4().hex,
        "r_query_id": f"{ts}{int(time.time())}",
    }


def fetch_page(page, page_size):
    r = requests.post(API_URL, headers=HEADERS, json=build_data(page, page_size), timeout=30)
    j = r.json()
    if j.get("status") != 1:
        print(f"  ⚠️ 第{page}页 API错误: status={j.get('status')} {j.get('message')}")
        return [], 0
    data = j.get("data") or {}
    pg = data.get("page") or {}
    return data.get("list") or [], pg.get("totalCount", 0)


def normalize(job):
    cities = ", ".join(c.get("name", "") for c in (job.get("cityList") or []) if c.get("name"))
    depts = ", ".join(d.get("name", "") for d in (job.get("department") or []) if d.get("name"))
    jid = job.get("jobUnionId", "")
    rt = job.get("refreshTime")
    pub = ""
    if rt:
        try:
            pub = datetime.fromtimestamp(rt / 1000).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pub = str(rt)
    return {
        "platform": "美团",
        "position_name": job.get("name", ""),
        "work_location": cities,
        "department": depts,
        "category": f"{job.get('jobFamily','')}/{job.get('jobFamilyGroup','')}".strip("/"),
        "publish_time": pub,
        "detail_url": f"https://zhaopin.meituan.com/job/{jid}" if jid else "",
        "salary": "",
        "education": "",
        "experience": job.get("workYear") or "",
        "job_duty": (job.get("jobDuty") or "").replace("\n", " "),
        "job_requirement": (job.get("jobRequirement") or "").replace("\n", " "),
        "source_id": jid,
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 美团：官方销售类别(11010)全国范围")
    all_positions = []
    page, page_size = 1, 20
    total = None
    while True:
        items, total_now = fetch_page(page, page_size)
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
    out = f"{OUT_DIR}/meituan_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "美团", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
