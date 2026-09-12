#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集滴滴岗位：按官方岗位类型(销售/商业分析/职能与支持/战略/安全)采集并抓取详情"""
import json
import os
import time
import requests
from datetime import datetime

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
LIST_URL = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/list"
DETAIL_URL = "https://talent.didiglobal.com/recruit-portal-service/api/job/front/view/{jd_id}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://talent.didiglobal.com/social/list/1?jobType=21",
    "Origin": "https://talent.didiglobal.com",
}
COOKIES = {
    "_OMGID": "ec27041c-eb2d-4492-b532-8ec163593281",
    "language": "zh_cn",
    "SESSION": "1841c93d-6134-4802-9e94-c33567821687",
}

JOB_TYPES = {  # 岗位类型: 名称
    21: "销售",
    24: "商业分析",
    23: "职能与支持",
    15: "战略",
    18: "安全",
}


def fetch_sales_jobs():
    """按岗位类型爬取全部岗位"""
    jobs = []
    for jt, name in JOB_TYPES.items():
        page = 1
        type_count = 0
        while True:
            r = requests.get(
                LIST_URL,
                params={"jobType": jt, "page": page, "recruitType": 1, "size": 16},
                headers=HEADERS, cookies=COOKIES, timeout=30,
            )
            j = r.json()
            meta_code = j.get("meta", {}).get("code")
            data = j.get("data") or {}
            items = data.get("items") or []
            total = data.get("total", 0)
            for it in items:
                it["_type"] = name
            jobs.extend(items)
            type_count += len(items)
            print(f"  {name}(jobType={jt}) 第{page}页: {len(items)}条 (本类型{type_count}/{total})")
            if meta_code != 0 or not items or type_count >= total:
                break
            page += 1
            time.sleep(2)
    return jobs


def fetch_detail(jd_id):
    """抓取单个岗位详情（带重试）"""
    for attempt in range(3):
        try:
            r = requests.get(DETAIL_URL.format(jd_id=jd_id), headers=HEADERS, cookies=COOKIES, timeout=30)
            j = r.json()
            if j.get("meta", {}).get("code") == 0:
                return j.get("data") or {}
        except Exception as e:
            print(f"  ⚠️ 详情抓取失败 jdId={jd_id}: {e}")
        time.sleep(5 * (attempt + 1))
    return {}


def normalize(job, detail):
    jd_id = job.get("jdId") or ""
    return {
        "platform": "滴滴",
        "position_name": job.get("jobName", ""),
        "work_location": job.get("workArea", ""),
        "department": job.get("deptName", ""),
        "category": job.get("_type", ""),
        "publish_time": (detail.get("publishTime") or job.get("createTime") or "")[:16],
        "detail_url": f"https://talent.didiglobal.com/social/detail/{jd_id}" if jd_id else "",
        "salary": "",
        "education": "",
        "experience": "",
        "job_duty": (detail.get("jobDesc") or job.get("jobDuty") or "").replace("\n", " "),
        "job_requirement": (detail.get("qualification") or job.get("jobQualification") or "").replace("\n", " "),
        "source_id": jd_id or job.get("jobNo", ""),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("🚀 滴滴：多岗位类型采集", list(JOB_TYPES.values()))
    jobs = fetch_sales_jobs()
    seen = set()
    unique_jobs = []
    for job in jobs:
        if job.get("jdId") not in seen:
            seen.add(job.get("jdId"))
            unique_jobs.append(job)
    print(f"✅ 列表共 {len(jobs)} 个岗位（去重后 {len(unique_jobs)}），开始抓取详情...")
    data = []
    for i, job in enumerate(unique_jobs, 1):
        detail = fetch_detail(job.get("jdId"))
        data.append(normalize(job, detail))
        print(f"  [{i}/{len(unique_jobs)}] [{job.get('_type','')}] {job.get('jobName','')[:30]} (详情{'✅' if detail else '❌'})")
        time.sleep(1.5)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = f"{OUT_DIR}/didi_sales_{ts}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"platform": "滴滴", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {out}")


if __name__ == "__main__":
    main()
