#!/usr/bin/env python3
"""selftest_gate_browser.py — req 13's throwaway sidecar never deadlocks on its own request log (2026-10-19).

The bug: gate_browser.browser_render read the sidecar's stdout PIPE only until the URL. The sidecar logs one line per
HTTP request, every image on the scratch copy 404s, and after ~64 KB the pipe was full: the sidecar blocked mid-request
and Edge waited until the 600 s timeout (then the gate retried: 20 min). A 178-row sheet never gated.

This serves a sheet with N_IMG image tags through browser_render, with Edge swapped for a stdlib fetcher that loads
the page and then requests every image (each a 404 and a log line, ~300 KB of log in all). It must finish in seconds
and count every <img>. No Edge, no Windows process, no network beyond localhost.

    python3 src/RimMandrake/Utils/art/selftest_gate_browser.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import textwrap
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gate_browser as GB  # noqa: E402

N_IMG = 4000
LIMIT_S = 45.0
FAILS = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


FETCHER = textwrap.dedent('''
    import re, sys, urllib.request, urllib.error
    from concurrent.futures import ThreadPoolExecutor
    url = sys.argv[1]
    page = urllib.request.urlopen(url, timeout=10).read().decode("utf-8", "replace")
    base, _, query = url.partition("?")
    def get(src):
        try:
            urllib.request.urlopen(base.rstrip("/") + "/" + src + "?" + query, timeout=10).read()
            return 200
        except urllib.error.HTTPError as e:
            return e.code
    with ThreadPoolExecutor(16) as ex:      # like a browser: many requests in flight, each a log line on the sidecar
        codes = list(ex.map(get, re.findall(r'<img src="([^"]+)"', page)))
    sys.stderr.write("fetched %d images, %d were 404\\n" % (len(codes), codes.count(404)))
    sys.stdout.write(page)
''')


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="gatebrowser_") as td:
        td = Path(td)
        fetch = td / "fetch.py"
        fetch.write_text(FETCHER)
        imgs = "\n".join(f'<img src="missing/picture_{i:05d}_with_a_long_enough_name_to_fill_the_log.png">' for i in range(N_IMG))
        sheet = td / "pipe_sheet_2026-10-19.html"
        sheet.write_text(f"<!doctype html><html><head><meta charset='utf-8'></head><body>{imgs}</body></html>")
        dec = td / "pipe_sheet_2026-10-19.decisions.json"
        dec.write_text(json.dumps({"sheetId": "pipe_sheet_2026-10-19", "decisions": {}}))
        orig = (GB.EDGE, GB.edge_cmd)
        GB.EDGE = sys.executable                                   # "Edge is installed": the fetcher stands in for it
        GB.edge_cmd = lambda url, profile: [sys.executable, str(fetch), url]
        try:
            t0 = time.time()
            n, errs, prob = GB.browser_render(sheet, dec, timeout=int(LIMIT_S))
            dt = time.time() - t0
        finally:
            GB.EDGE, GB.edge_cmd = orig
        check(prob == "", f"no problem reported ({prob!r})")
        check(n == N_IMG, f"counts every <img>: {n} of {N_IMG}")
        check(dt < LIMIT_S, f"{N_IMG} 404 image requests served in {dt:.1f} s (< {LIMIT_S:.0f} s; the pipe bug hung to the timeout)")
        check(not (td / ".gatecheck_pipe_sheet_2026-10-19").exists(), "scratch dir removed")
        check(json.loads(dec.read_text()) == {"sheetId": "pipe_sheet_2026-10-19", "decisions": {}}, "the real decisions file is untouched")
    check(GB.EDGE_TIMEOUT_S < 600 and GB.EDGE_TIMEOUT_S <= 120, f"Edge stage hard cap {GB.EDGE_TIMEOUT_S} s (was 600 s + a retry)")
    import scaled_review_gate as SG
    src = Path(SG.__file__).read_text()
    check('"Timeout" in prob' not in src, "the gate no longer retries a timed-out render")
    print(f"{'FAIL' if FAILS else 'PASS'} selftest_gate_browser ({len(FAILS)} failing)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
