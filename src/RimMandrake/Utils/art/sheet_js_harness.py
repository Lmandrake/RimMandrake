#!/usr/bin/env python3
"""sheet_js_harness.py — run the biome art sheet's own page JS outside a browser (node) and inside one (headless Edge),
for selftests. Not a selftest itself.

  run_js(snippet)                 the sheet's RENDER script (BIOME_BODY + COMMON_JS) with the template globals stubbed,
                                  then SNIPPET; returns whatever SNIPPET console.log()s as JSON.
  item_html(item, dec)            window.itemBody(item) for one row -> HTML string (the real row markup).
  edge_probe(body_html, probe_js) a page carrying the template's CSS + the sheet's CSS + BODY_HTML, opened in headless Edge;
                                  PROBE_JS runs on load and must set document.getElementById('probe').textContent.
                                  Returns that text, or None with the reason (UNMEASURED) when Edge cannot run.
"""
from __future__ import annotations

import sys as _rm_sys, pathlib as _rm_pl  # noqa: E401
_rm_sys.path.insert(0, str(_rm_pl.Path(__file__).resolve().parents[4] / "src" / "RimMandrake" / "Utils"))
from rmpaths import rm_path, rm_str, rm_win  # noqa: E402,F401  (data root: rmpaths.py)
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

STUBS = r"""
const window = globalThis; const errs = [];
const document = {readyState: 'complete', querySelector: () => null, querySelectorAll: () => [], addEventListener: () => {},
  getElementById: () => null, createElement: () => ({style: {}, children: []}), body: {appendChild: () => {}}};
const setInterval = () => 0; const fetch = () => Promise.resolve({ok: false}); const addEventListener = () => {};
const location = {href: ''};
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
let frozen = false; const showErr = m => errs.push(m);
let DEC = {}; let byId = new Map(); const OPTS = [];
const queue = () => {}, patchRow = () => {}, paintCounts = () => {}, prefillOf = it => (it && it.prefill) || '';
const setDecision = (id, key) => { DEC[id] = DEC[id] || {decision: '', note: ''}; DEC[id].decision = key; DEC[id].decidedAt = 'T'; };
const cssEsc = s => String(s);
"""


def node() -> str | None:
    n = shutil.which("node") or str(Path.home() / ".local/bin/node")
    return n if Path(n).exists() else None


def render_script() -> str:
    import art_sheet as A
    return A.BIOME_BODY.replace("%LETTERS%", A.LETTERS).replace("%NEAR%", str(A.NEAR)) + A.COMMON_JS


def run_js(snippet: str, timeout: int = 60):
    n = node()
    if not n:
        raise RuntimeError("UNMEASURED: node not found")
    prog = STUBS + render_script() + "\n;(() => {\n" + snippet + "\n})();"
    r = subprocess.run([n, "-e", prog], capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RuntimeError("node failed: " + (r.stderr or r.stdout)[-800:])
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    return json.loads(lines[-1]) if lines else None


def item_html(item: dict, dec: dict | None = None) -> str:
    return run_js("DEC = " + json.dumps({item["id"]: dec} if dec else {}) + "; byId = new Map([[" + json.dumps(item["id"])
                  + ", " + json.dumps(item) + "]]); console.log(JSON.stringify(window.itemBody(byId.get("
                  + json.dumps(item["id"]) + "))));")


def page_css() -> str:
    import art_sheet as A
    tpl = (A.SKILL / "sheet_template.html").read_text()
    m = re.search(r"<style>(.*?)</style>", tpl, re.S)
    return "<style>" + (m.group(1) if m else "") + "</style>" + A.STYLE + A.BIOME_STYLE


SCRATCH_WIN, SCRATCH_WSL = rm_win("scratch", "sheet_probe"), rm_str("scratch", "sheet_probe")


def edge_probe(body_html: str, probe_js: str, files: dict | None = None, width: int = 1600, timeout: int = 180):
    """-> (probe text or None, problem text)."""
    import gate_browser as GB
    if not Path(GB.EDGE).is_file():
        return None, f"UNMEASURED: Edge not found at {GB.EDGE}"
    run = f"p{os.getpid()}_{int(time.time() * 1000)}"
    work = Path(SCRATCH_WSL) / run
    work.mkdir(parents=True, exist_ok=True)
    for rel, data in (files or {}).items():
        (work / rel).parent.mkdir(parents=True, exist_ok=True)
        (work / rel).write_bytes(data)
    html = ("<!doctype html><html><head><meta charset='utf-8'>" + page_css() + "</head><body>"
            f"<div id='list' style='width:{width - 40}px'>" + body_html + "</div><pre id='probe'>PENDING</pre><script>"
            "addEventListener('load', () => setTimeout(() => { try {" + probe_js +
            "} catch (e) { document.getElementById('probe').textContent = 'ERROR ' + e; } }, 300));</script></body></html>")
    (work / "page.html").write_text(html, encoding="utf-8")
    marker = "probe_" + run
    url = "file:///" + (SCRATCH_WIN + "\\" + run + "\\page.html").replace("\\", "/")
    try:
        r = subprocess.run([GB.EDGE, "--headless=new", "--disable-gpu", f"--window-size={width},1200",
                            "--virtual-time-budget=5000", "--allow-file-access-from-files", "--disable-extensions",
                            "--user-data-dir=" + SCRATCH_WIN + "\\" + marker, "--no-first-run", "--dump-dom", url],
                           capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"UNMEASURED: headless Edge failed ({type(e).__name__})"
    finally:
        GB.stop_marked(marker)
        shutil.rmtree(Path(SCRATCH_WSL) / marker, ignore_errors=True)
    shutil.rmtree(work, ignore_errors=True)
    m = re.search(r'<pre id="probe">(.*?)</pre>', r.stdout, re.S)
    if not m:
        return None, "UNMEASURED: no probe element in the dumped DOM: " + r.stdout[-200:]
    return m.group(1), ""
