#!/usr/bin/env python3
"""selftest_sheet_column_undo.py — a column click on an art sheet is one undo step of its own.

SHEET_COLUMN_CLICK_WIRE_UNDO: column clicks go through window.artAct -> SLX.*, which rewrote DEC[row] but pushed nothing
on the template's undo stack. Hotkey B then click C then `u` restored the record from before B: one undo lost both acts.

This runs the REAL page as the browser does — the art sheet's RENDER script (art_sheet.BIOME_BODY + COMMON_JS), then the
review-sheets template's own page script (sheet_template.html via ~/.claude/skills/review-sheets) — in node over the
catch-all DOM stub of selftest_sheet_bulk_nobulk.py, and drives the real keydown and click listeners. No browser.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import selftest_sheet_bulk_nobulk as B  # noqa: E402  (STUB, page_script, TEMPLATE)
import sheet_js_harness as H  # noqa: E402  (render_script, node)

ITEM = {
    "id": "RM_Pod", "rev": "s1", "label": "pod", "group": "G", "prefill": "", "thumbs": {}, "letters": ["A", "B", "C"],
    "graphics": [
        {"key": "R/Grown", "res": "R/Grown", "primary": True, "lane": "slot", "pool": False, "facings": ["single"],
         "role": "body", "slot": {"label": "PLANT · GROWN", "kind": "grown", "required": True},
         "cols": [{"letter": "A", "kind": "live", "winner": True, "faces": {"single": "a1"}, "setId": "sa"},
                  {"letter": "B", "kind": "artpipe", "faces": {"single": "b1"}, "setId": "sb", "purgeable": True},
                  {"letter": "C", "kind": "artpipe", "faces": {"single": "c1"}, "setId": "sc", "purgeable": True}]}]}
OPTS = [{"key": L, "label": L, "hotkey": str(i + 1), "color": "#0a0"} for i, L in enumerate("ABC")]

DRIVE = r"""
for (const f of [...(__listeners['document:DOMContentLoaded'] || []), ...(__listeners['window:DOMContentLoaded'] || [])]) {
  try { f({}); } catch (e) {}
}
const kd = (__listeners['window:keydown'] || [])[0];
const clicks = __listeners['document:click'] || [];
if (!kd) throw new Error('no keydown listener found');
if (!clicks.length) throw new Error('no document click listener found (artAct delegation)');
shown = ITEMS.slice(); focusIdx = 0;
const cp = x => x == null ? null : JSON.parse(JSON.stringify(x));
const key = k => kd({ key: k, shiftKey: k === 'U', ctrlKey: false, metaKey: false, altKey: false, target: {}, preventDefault() {} });
const col = (act, L) => {
  const el = { tagName: 'BUTTON', dataset: { id: 'RM_Pod', act, g: 'R/Grown', l: L } };
  const ev = { target: { closest: sel => sel === '[data-act]' ? el : null }, preventDefault() {}, stopPropagation() {} };
  for (const f of clicks) f(ev);
};
const pickOf = r => r && r.slots && r.slots['R/Grown'] ? r.slots['R/Grown'].pick || r.slots['R/Grown'].state : null;
const o = {};
o.start = cp(DEC.RM_Pod || null);
key('2'); o.afterB = cp(DEC.RM_Pod); o.stackB = undoStack.length;
col('pick', 'C'); o.afterC = cp(DEC.RM_Pod); o.stackC = undoStack.length;
key('u'); o.undo1 = cp(DEC.RM_Pod || null);
key('u'); o.undo2 = cp(DEC.RM_Pod || null);
key('U'); o.redo1 = cp(DEC.RM_Pod || null);
key('U'); o.redo2 = cp(DEC.RM_Pod || null);
const before = undoStack.length; col('pick', 'Z'); o.refusedPushed = undoStack.length - before;
o.pick = { afterB: pickOf(o.afterB), afterC: pickOf(o.afterC), undo1: pickOf(o.undo1), redo2: pickOf(o.redo2) };
console.log(JSON.stringify(o));
"""

FAILS = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main() -> int:
    node = H.node()
    if not node or not B.TEMPLATE.exists():
        print("UNMEASURED: node or the review-sheets template is not reachable")
        return 3
    cfg = {"sheetId": "selftest_column_undo", "title": "t", "options": OPTS}
    pre = ("const __CFG = %s; const __ITEMS = %s;\n" % (json.dumps(cfg), json.dumps([ITEM]))) + B.STUB + "globalThis.scrollBy = () => {};\n"
    # the browser's order: RENDER (injected at FILL IN #3) runs before the template's page script
    prog = pre + H.render_script() + "\n;\n" + B.page_script() + "\n;(() => {\n" + DRIVE + "\n})();"
    r = subprocess.run([node, "-e", prog], capture_output=True, text=True, timeout=60)
    if r.returncode:
        print("FAIL node run: " + (r.stderr or r.stdout)[-1200:])
        return 1
    o = json.loads([ln for ln in r.stdout.splitlines() if ln.strip()][-1])
    strip = lambda d: {k: v for k, v in (d or {}).items() if k not in ("at", "decidedAt")}  # noqa: E731
    check(o["afterB"] and o["afterB"]["decision"] == "B" and o["pick"]["afterB"] == "B" and o["stackB"] == 1,
          "control: hotkey 2 sets B as the slot pick and pushes one undo entry (%s)" % o["pick"])
    check(o["pick"]["afterC"] == "C" and o["stackC"] == 2, "a column click on C pushes its own undo entry (stack %s)" % o["stackC"])
    check(strip(o["undo1"]) == strip(o["afterB"]), "u after B then click C restores the record AFTER B, not before it")
    check(o["undo2"] == o["start"], "a second u restores the record from before B")
    check(strip(o["redo1"]) == strip(o["afterB"]) and o["pick"]["redo2"] == "C", "U, U re-applies B then the C click")
    check(o["refusedPushed"] == 0, "a refused column click (a letter the slot lacks) pushes no undo entry")
    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
