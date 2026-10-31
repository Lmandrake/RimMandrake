#!/usr/bin/env python3
"""selftest_sheet_live_guard.py — the page guard, gate req 16, the off-tree refusal and the live URL file."""
import atexit, shutil, sys, tempfile
_T = tempfile.mkdtemp(prefix="st_live_guard_")
atexit.register(shutil.rmtree, _T, True)
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import nonart_sheet as NA
import scaled_review_gate as SG
import serve_gated as SV
import sheet_live_guard as G

PAGE = '<html><head><title>x</title></head><body><p>"</body>" in a string</p></body></html>'
fails = 0


def check(name, ok, detail=""):
    global fails
    print(("ok   " if ok else "FAIL ") + name + (f": {detail}" if detail and not ok else ""))
    fails += not ok


once = G.inject(PAGE)
check("inject adds the guard", G.has_guard(once) and not G.has_guard(PAGE))
check("inject is idempotent", G.inject(once) == once)
check("guard sits after the body content, inside the body", once.index(G.MARK) > once.index("in a string") and once.endswith("</body></html>"))
check("the guard's only exit is a served sidecar", "if (window.__SIDECAR__) return;" in G.GUARD)
check("no dismiss control", "<button" not in G.GUARD and "createElement('button')" not in G.GUARD)
check("no bare-page fallback", G.inject("<p>no body tag</p>").count(G.MARK) == 1)
check("non-art declare carries the guard", G.has_guard(NA.declare("<html><head></head><body></body></html>")))
check("re-declaring keeps one guard", NA.declare(NA.declare("<html><head></head><body></body></html>")).count(G.MARK) == 1)

sheet = Path(_T) / "a_sheet_2026.html"
out = G.write_live(sheet, "http://localhost:1234/?t=abc")
check("live file sits beside the sheet under the name the page asks for", out.name == "a_sheet_2026.live.js" and "localhost:1234" in out.read_text())
G.clear_live(sheet)
check("live file goes when the server stops", not out.exists())
G.clear_live(sheet)      # twice is fine: a killed server may leave nothing to clear


def req16(html):
    return SG.check_live_writer({"html": html}, [])


check("req 16 refuses a page without the guard", req16(PAGE).problems)
cfg = '<script id="CONFIG" type="application/json">{"decisionsPath": "%s"}</script>'
check("req 16 passes a guarded page", not req16(G.inject(PAGE + cfg % "")).problems)
check("req 16 refuses a baked /home path", req16(G.inject(PAGE + cfg % "/home/x/d.json")).problems)
check("req 16 refuses a baked /mnt path", req16(G.inject(PAGE + cfg % "/mnt/d/x.json")).problems)
check("req 16 refuses a baked UNC path", req16(G.inject(PAGE + cfg % "\\\\\\\\wsl$\\\\Ubuntu")).problems)
forged = PAGE.replace("</body>", '<script id="sheet-live-guard"></script></body>')
check("an empty block with the right id is no guard", req16(forged).problems)
check("inject replaces a forged block", G.has_guard(G.inject(forged)) and G.inject(forged).count(G.MARK) == 1)
check("req 16 is in CHECKS", SG.check_live_writer in SG.CHECKS)

check("an art sheet in the clone serves", SV.off_tree_gate(SV.HERE / "serve_gated.py") == 0)
check("a copy outside the clone is refused", SV.off_tree_gate(sheet) == 4)
sys.exit(1 if fails else 0)
