#!/usr/bin/env python3
"""selftest_sheet_frozen_wrapper.py — on a FROZEN sheet the art_sheet.py setDecision wrapper records nothing
(SHEET_FROZEN_WRAPPER_SILENCE_STAMP).

The template's setDecision refuses a frozen sheet ("decisions are read-only") and returns. The wrapper in COMMON_JS used
to carry on after calling it: it stamped decidedAt, wrote the primary slot's pick from whatever decision the record
already held, and queued the row — so the in-page record showed a ruling the template never accepted (and a prefill
turned into "his" pick at ingest).

The page is loaded as in selftest_sheet_hotkey_keydown (render script, template page script, DOMContentLoaded). A row
holds a saved record (decision A, no decidedAt, no slots); the sheet is frozen; a pick arrives both as a direct
window.setDecision call and as a real digit keydown. The record must be byte-identical afterwards, nothing queued, and
the template's frozen message shown. Controls: unfrozen, the same pick lands (the instrument can see a write); and with
the fix line removed, the frozen pick stamps again (the checks would go red).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import selftest_sheet_bulk_nobulk as BN  # noqa: E402
import selftest_sheet_hotkey_keydown as HK  # noqa: E402

FAILS: list[str] = []
FIX_LINE = "if (!it_ || (typeof frozen !== 'undefined' && frozen)) return orig(id, key, opts);"

DRIVE = r"""
(__listeners['window:DOMContentLoaded'] || []).concat(__listeners['document:DOMContentLoaded'] || []).forEach(f => f());
const kd = (__listeners['window:keydown'] || [])[0];
if (!kd) throw new Error('no keydown listener found');
const errs = []; window.showErr = m => errs.push(String(m));
let queued = 0; const q0 = window.queue; window.queue = function () { queued++; return q0.apply(this, arguments); };
const saved = { decision: 'A', note: '', prefill: 'A' };
DEC['RM_Pod'] = JSON.parse(JSON.stringify(saved));
frozen = __FROZEN;
window.setDecision('RM_Pod', 'B');
const afterCall = JSON.parse(JSON.stringify(DEC['RM_Pod'] || null));
shown = ITEMS.slice(); focusIdx = 0;
kd({ key: '2', shiftKey: false, ctrlKey: false, metaKey: false, altKey: false, target: {}, preventDefault() {} });
const afterKey = JSON.parse(JSON.stringify(DEC['RM_Pod'] || null));
console.log(JSON.stringify({ saved, afterCall, afterKey, queued, errs }));
"""


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def run(frozen: bool, mutate: bool = False):
    import sheet_js_harness as H
    render = H.render_script()
    if mutate:
        if FIX_LINE not in render:
            raise RuntimeError("fix line not found in COMMON_JS (mutation control cannot be placed)")
        render = render.replace(FIX_LINE, "", 1)
    cfg = {"sheetId": "selftest_frozen_wrapper", "title": "t", "options": HK.opts(False), "groupLabel": "group",
           "media": True, "schema": 2}
    pre = ("const __CFG = %s; const __ITEMS = %s; const __FROZEN = %s;\n"
           % (json.dumps(cfg), json.dumps(HK.ITEMS), json.dumps(frozen))) + HK._stub() \
        + "globalThis.scrollBy = () => {}; globalThis.scrollTo = () => {};\n"
    prog = pre + render + "\n" + BN.page_script() + "\n;(() => {\n" + DRIVE + "\n})();"
    r = subprocess.run([H.node(), "-e", prog], capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("node failed: " + (r.stderr or r.stdout)[-1200:])
    return json.loads([ln for ln in r.stdout.splitlines() if ln.strip()][-1])


def main() -> int:
    import sheet_js_harness as H
    if not H.node():
        print("UNMEASURED: node not found")
        return 3
    if not BN.TEMPLATE.exists():
        print("UNMEASURED: template not reachable at %s" % BN.TEMPLATE)
        return 3

    o = run(frozen=True)
    check(o["afterCall"] == o["saved"], "frozen: window.setDecision(B) leaves the saved record byte-identical "
          "(no decidedAt, no slots pick): %s" % json.dumps(o["afterCall"]))
    check(o["afterKey"] == o["saved"], "frozen: keydown 2 leaves the saved record byte-identical")
    check(o["queued"] == 0, "frozen: nothing queued for save (queued=%d)" % o["queued"])
    check(any("frozen" in e for e in o["errs"]) and not any("not a set of" in e for e in o["errs"]),
          "frozen: the template's frozen message is shown, not a lane-guard message: %s" % o["errs"][:2])

    u = run(frozen=False)              # control: the instrument sees a write when one is allowed
    ua = u["afterCall"] or {}
    check(ua.get("decision") == "B" and ua.get("decidedAt")
          and ((ua.get("slots") or {}).get("R/Grown") or {}).get("pick") == "B" and u["queued"] > 0,
          "control [unfrozen]: the same pick records B, decidedAt and the grown slot's pick, and queues")

    m = run(frozen=True, mutate=True)  # control: without the fix the frozen pick stamps again
    ma = m["afterCall"] or {}
    check(ma != m["saved"] and ma.get("decidedAt"),
          "control [fix removed]: the frozen pick stamps decidedAt again — the frozen checks above would go red")

    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
