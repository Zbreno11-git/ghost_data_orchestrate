"""Drive the built evidence viewer in a real browser (S7 C7.2/C7.4). Developer tool, not shipped in code.zip.

Needs Playwright (not a runtime dependency): `python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright`, then
run this file with that interpreter. It checks, on the given HTML file:
- it loads with no console error and makes **no network request** (every request is recorded);
- the case list, search, filters and a click-through to COMPLETE, INCOMPLETE, NOT_APPLICABLE, unresolved and
  heuristic cases render their labels;
- a hostile excerpt (`</script><img onerror=…>`) injected into a copy of the page's data renders as inert text;
- desktop (1280 px) and phone (390 px) widths have no horizontal page scroll; screenshots are saved.
Exit 1 on any failure.

Usage: <pw-python> scripts/viewer_browser_check.py --html viewer.html --shots <dir>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

HOSTILE = '</script><img src=x onerror="window.__pwned=1"><script>window.__pwned=2</script>'


def hostile_copy(html: str, out: Path) -> None:
    """Inject the hostile string into the first provenance excerpt of the page's embedded data."""
    from viewer.build import script_safe_json
    m = re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)', html, re.S)
    data = json.loads(m.group(2))
    if not data["prov"]:
        raise SystemExit("the page carries no provenance (legacy or failed run): nothing to test the excerpt path on")
    first = next(iter(data["prov"].values()))
    first["excerpt"] = {"note": HOSTILE}
    data["cases"][0]["reasons"] = [HOSTILE] + data["cases"][0]["reasons"]
    out.write_text(html[:m.start(2)] + script_safe_json(data) + html[m.end(2):], encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, type=Path)
    ap.add_argument("--shots", required=True, type=Path)
    a = ap.parse_args(argv)
    from playwright.sync_api import sync_playwright
    a.shots.mkdir(parents=True, exist_ok=True)
    fails, report = [], {}
    hostile = a.shots / "hostile.html"
    hostile_copy(a.html.read_text(encoding="utf-8"), hostile)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        report["browser"] = f"chromium {browser.version}"
        for name, width, height in (("desktop", 1280, 900), ("phone", 390, 844)):
            page = browser.new_page(viewport={"width": width, "height": height})
            errors, requests = [], []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("request", lambda r: requests.append(r.url))
            t0 = time.time()
            page.goto(a.html.resolve().as_uri())
            page.wait_for_selector("#list li button")
            report[f"{name}_load_s"] = round(time.time() - t0, 2)
            total = page.locator("#count").inner_text()
            for cid, must in (("case_63", ["HEURISTIC PREDICTION", "Predicted complete, not proven"]),):
                page.fill("#q", cid)
                page.locator(f'#list button[data-case="{cid}"]').click()
                body = page.locator("#detail").inner_text()
                fails += [f"{name}: {cid} lacks {s!r}" for s in must if s not in body]
            page.fill("#q", "")
            for status, must in (("NOT_APPLICABLE", "does not authorize deletion"), ("INCOMPLETE", "Proposed remediation — not executed"),
                                 ("COMPLETE", "Verification evidence")):
                page.select_option("#fs", status)
                page.locator("#list li button").first.click()
                if must not in page.locator("#detail").inner_text():
                    fails.append(f"{name}: first {status} case lacks {must!r}")
            page.select_option("#fs", "")
            page.select_option("#fp", "resolved")
            page.locator("#list li button").first.click()
            if "support: resolved" not in page.locator("#detail").inner_text():
                fails.append(f"{name}: resolved filter")
            page.select_option("#fp", "")
            page.fill("#q", "no-such-case-zzz")
            if "No case matches" not in page.locator("#list").inner_text():
                fails.append(f"{name}: empty result text")
            page.fill("#q", "")
            page.locator("#list li button").first.click()
            scroll = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            if scroll > 0:
                fails.append(f"{name}: horizontal page scroll {scroll}px")
            page.screenshot(path=str(a.shots / f"{name}.png"), full_page=False)
            local = [u for u in requests if not u.startswith("file://")]
            if local or errors:
                fails.append(f"{name}: network {local[:3]} errors {errors[:3]}")
            report[f"{name}_cases"] = total
            page.close()
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(hostile.resolve().as_uri())
        page.wait_for_selector("#list li button")
        page.locator("#list li button").first.click()
        for d in page.locator("#detail details").all():
            d.evaluate("e => e.open = true")
        pwned = page.evaluate("window.__pwned")
        text = page.locator("#detail").inner_text()
        if pwned is not None or HOSTILE not in text or page.locator("#detail img").count():
            fails.append(f"hostile excerpt: pwned={pwned} shown_as_text={HOSTILE in text} imgs={page.locator('#detail img').count()}")
        report["hostile"] = "inert text" if pwned is None and HOSTILE in text else "FAILED"
        page.screenshot(path=str(a.shots / "hostile.png"))
        browser.close()
    report["failures"] = fails
    print(json.dumps(report, indent=1))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
