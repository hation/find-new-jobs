#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""采集浪潮社会招聘销售岗位：Playwright + Angular scope 取全量数据(含职位描述)"""
import glob
import json
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE = "/Users/xingan/Documents/software/zhaopin/find_new_job"
OUT_DIR = f"{BASE}/sales/output"
URL = "https://inspur.hcmcloud.cn/recruit#/portal_job_list?job_class=_HB5_c29j!WFs&filter_dict=_HB5_eyJf!m9iX2NsYXNzIjoic29j!WFsIiwic2VsZWN0X2RlcGFydCI6bnVsbH0%253D"


def find_chrome():
    pats = [
        os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"),
        os.path.expanduser("~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"),
    ]
    for pat in pats:
        hits = glob.glob(pat)
        if hits:
            return sorted(hits)[-1]
    return None


FIND_CTRL = """() => {
    const seen = new Set();
    let found = null;
    const walk = (el) => {
        const s = angular.element(el).scope();
        if (s && !seen.has(s.$id)) {
            seen.add(s.$id);
            if (s.paging && s.card_env && s.paging.total_count) {
                found = s;
                return;
            }
        }
        for (const c of el.children) { if (found) return; walk(c); }
    };
    walk(document.body);
    return found;
}"""


def set_pagesize_200(page):
    return page.evaluate("""() => {
        const seen = new Set();
        let done = false;
        const walk = (el) => {
            const s = angular.element(el).scope();
            if (s && !seen.has(s.$id)) {
                seen.add(s.$id);
                if (s.paging && s.card_env && s.paging.total_count) {
                    try {
                        s.$apply(function() {
                            s.paging.page_size = 200;
                            s.paging._page_size = 200;
                            if (typeof s.fetchData === 'function') s.fetchData();
                        });
                        done = true;
                    } catch (e) {}
                    return;
                }
            }
            for (const c of el.children) { if (done) return; walk(c); }
        };
        walk(document.body);
        return done;
    }""")


def get_data(page):
    return page.evaluate("""() => {
        const seen = new Set();
        let out = null;
        const walk = (el) => {
            const s = angular.element(el).scope();
            if (s && !seen.has(s.$id)) {
                seen.add(s.$id);
                if (s.paging && s.card_env && s.paging.total_count) {
                    out = s.card_env.data;
                    return;
                }
            }
            for (const c of el.children) { if (out) return; walk(c); }
        };
        walk(document.body);
        return out;
    }""")


def split_desc(job_desc):
    """把 job_desc 拆成岗位职责 / 任职要求"""
    duty, req = "", ""
    if job_desc:
        # 常见分隔：任职资格/任职要求/资格要求
        m = re.split(r"任职资格|任职要求|资格要求", job_desc)
        duty = m[0].replace("岗位职责", "").replace("职责描述", "").strip()
        req = m[1].strip() if len(m) > 1 else ""
    return duty, req


def normalize(job):
    duty, req = split_desc(job.get("job_desc") or "")
    return {
        "platform": "浪潮",
        "position_name": job.get("name", ""),
        "work_location": job.get("work_city") or job.get("work_province") or "",
        "department": job.get("department_name") or "",
        "category": (job.get("job_categ") or {}).get("name") or "",
        "publish_time": (job.get("release_date") or "")[:16],
        "detail_url": "",
        "salary": "",
        "education": "",
        "experience": "",
        "job_duty": duty.replace("\n", " "),
        "job_requirement": req.replace("\n", " "),
        "source_id": str(job.get("id", "")),
    }


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    exe = find_chrome()
    if not exe:
        print("❌ 未找到 Playwright Chromium，请先运行: playwright install chromium")
        return
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=exe)
        page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36", viewport={"width": 1440, "height": 1000})
        page.goto(URL, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        try:
            page.get_by_text("我已阅读并同意", exact=False).first.click(timeout=3000)
        except Exception:
            pass
        page.wait_for_timeout(6000)
        page.evaluate("""() => {
            const items = document.querySelectorAll('#filter-item-job_category .item-content');
            for (const it of items) if ((it.textContent || '').trim() === '销售') { it.click(); return; }
        }""")
        page.wait_for_timeout(5000)

        # 改page_size并刷新
        set_pagesize_200(page)
        page.wait_for_timeout(8000)
        raw = get_data(page) or []
        print(f"✅ 从Angular scope获取 {len(raw)} 个销售岗位")
        data = [normalize(j) for j in raw]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = f"{OUT_DIR}/inspur_sales_{ts}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump({"platform": "浪潮", "count": len(data), "positions": data}, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存: {out}")
        browser.close()


if __name__ == "__main__":
    main()
