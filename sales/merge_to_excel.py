#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并各平台销售岗位数据为Excel汇总表"""
import glob
import json
import os
from datetime import datetime

import pandas as pd

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"

COLUMNS = [
    "platform", "position_name", "work_location", "department", "category",
    "publish_time", "detail_url", "salary", "education", "experience",
    "job_duty", "job_requirement", "source_id",
]
COL_CN = {
    "platform": "平台", "position_name": "岗位名称", "work_location": "工作地点",
    "department": "部门", "category": "岗位类别", "publish_time": "发布时间",
    "detail_url": "详情链接", "salary": "薪资", "education": "学历要求",
    "experience": "工作经验", "job_duty": "岗位职责", "job_requirement": "任职要求",
    "source_id": "岗位编号",
}


def latest_file_for(platform):
    files = sorted(glob.glob(f"{OUT_DIR}/{platform}_sales_*.json"))
    return files[-1] if files else None


def clean(value):
    return "" if value is None else value


def main():
    platforms = ["didi", "meituan", "anti", "quark", "bytedance", "tencent", "lenovo"]
    all_rows = []
    per_platform = {}

    for p in platforms:
        f = latest_file_for(p)
        if not f:
            print(f"⚠️ 缺少 {p} 的数据文件")
            continue
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        rows = data.get("positions", [])
        for row in rows:
            all_rows.append({c: clean(row.get(c, "")) for c in COLUMNS})
        per_platform[p] = rows
        print(f"📄 {p}: {len(rows)} 个岗位 <- {os.path.basename(f)}")

    df = pd.DataFrame(all_rows, columns=COLUMNS).rename(columns=COL_CN)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = f"{OUT_DIR}/销售岗位汇总_{ts}.xlsx"

    with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="全部销售岗位", index=False)

        for p, rows in per_platform.items():
            if not rows:
                continue
            sub = pd.DataFrame([{c: clean(r.get(c, "")) for c in COLUMNS} for r in rows], columns=COLUMNS).rename(columns=COL_CN)
            sub.to_excel(writer, sheet_name=PLATFORM_NAMES.get(p, p), index=False)

        summary = pd.DataFrame({
            "平台": [PLATFORM_NAMES.get(p, p) for p in per_platform if per_platform[p]],
            "销售岗位数": [len(per_platform[p]) for p in per_platform if per_platform[p]],
        })
        summary.loc[len(summary)] = ["合计", len(df)]
        summary.to_excel(writer, sheet_name="数据汇总", index=False)

    print(f"\n🎉 汇总完成: {len(df)} 个销售岗位")
    print(f"📁 Excel文件: {out_file}")
    return out_file


PLATFORM_NAMES = {"didi": "滴滴", "meituan": "美团", "anti": "蚂蚁", "quark": "夸克", "bytedance": "字节跳动", "tencent": "腾讯", "lenovo": "联想"}


if __name__ == "__main__":
    main()
