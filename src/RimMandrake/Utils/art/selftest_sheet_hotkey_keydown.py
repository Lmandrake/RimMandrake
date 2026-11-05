#!/usr/bin/env python3
"""selftest_sheet_hotkey_keydown.py — the biome art sheet's lane guard holds on REAL keydown events (SHEET_HOTKEY_PROVE_VIA_KEYDOWN).

The guard (art_sheet.py COMMON_JS, installed on DOMContentLoaded by re-assigning window.setDecision) refuses a letter that
is not a usable set of the row's primary slot. selftest_sheet_slots.hotkey_tests calls window.setDecision directly, so it
cannot see the failure that matters: the template's keydown handler calls its OWN `setDecision` binding, and if that
binding ever stops being a global (const/let, a module, an IIFE) the wrapper never installs and every number hotkey
writes any letter of the sheet as the primary slot's pick — silently.

This test loads the page as a browser would — the RENDER script (BIOME_BODY + COMMON_JS) first, then the review-sheet
template's own page script, then DOMContentLoaded — over the catch-all DOM of selftest_sheet_bulk_nobulk, and fires
real keydown events at the template's real listener: digit hotkeys and shift-digit group bulk. Two mutation controls
prove the instrument can see: with the guard deleted, and with the template's setDecision made non-global, the same
keypress writes the foreign letter (each control must turn the refusal checks red).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import selftest_sheet_bulk_nobulk as BN  # noqa: E402  (catch-all DOM stub + template locator)

FAILS: list[str] = []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def _col(letter, kind, sid, winner=False):
    c = {"letter": letter, "kind": kind, "faces": {"single": letter.lower() + "1"}, "setId": sid}
    if winner:
        c["winner"] = True
    return c


# Row 1: the slot-model plant of selftest_sheet_slots (grown pool A/B/C, young D/G, unassigned E, reference F), with
# `letters` listing every letter the row carries, as a built sheet does.
ROW1 = {"id": "RM_Pod", "rev": "s1", "prefill": "A", "group": "G", "label": "Pod", "thumbs": {},
        "letters": ["A", "B", "C", "D", "E", "F", "G"], "graphics": [
            {"key": "R/Grown", "res": "R/Grown", "primary": True, "lane": "slot", "pool": True, "facings": ["single"],
             "role": "body", "slot": {"label": "PLANT · GROWN (random pool)", "kind": "grown", "required": True},
             "cols": [_col("A", "live", "sa", True), _col("B", "artpipe", "sb"), _col("C", "donor", "sc")]},
            {"key": "R/Young", "res": "R/Young", "primary": False, "lane": "slot", "pool": False, "facings": ["single"],
             "role": "young plant", "slot": {"label": "PLANT · YOUNG (immature)", "kind": "plant_young", "required": False},
             "cols": [_col("D", "live", "sd", True), _col("G", "artpipe", "sg")]},
            {"key": "_byname", "res": None, "primary": False, "lane": "unassigned", "pool": False, "facings": ["single"],
             "role": "renders", "slot": {"label": "RENDERS NOT YET ASSIGNED", "kind": "unassigned"},
             "cols": [_col("E", "artpipe", "se")]},
            {"key": "_reference:RM_Huldu", "res": "_reference:RM_Huldu", "primary": False, "lane": "reference",
             "facings": ["single"], "role": "reference", "slot": {"label": "REFERENCE", "kind": "reference"},
             "cols": [_col("F", "artpipe", "sf")]}]}
# Row 2, same group: D IS a set of its primary slot, so a bulk D is legitimate here and only here.
ROW2 = {"id": "RM_Bush", "rev": "s1", "prefill": "A", "group": "G", "label": "Bush", "thumbs": {},
        "letters": ["A", "B", "C", "D"], "graphics": [
            {"key": "R/Bush", "res": "R/Bush", "primary": True, "lane": "slot", "pool": False, "facings": ["single"],
             "role": "body", "slot": {"label": "PLANT · GROWN", "kind": "grown", "required": True},
             "cols": [_col("A", "live", "ta", True), _col("B", "artpipe", "tb"), _col("C", "artpipe", "tc"),
                      _col("D", "artpipe", "td")]}]}
ITEMS = [ROW1, ROW2]

GUARD_LINE = "if (!usable) { if (typeof showErr === 'function') showErr("
TPL_DECL = "function setDecision(id, key, opts = {}) {"

DRIVE = r"""
(__listeners['window:DOMContentLoaded'] || []).concat(__listeners['document:DOMContentLoaded'] || []).forEach(f => f());
const kd = (__listeners['window:keydown'] || [])[0];
if (!kd) throw new Error('no keydown listener found');
const errs = []; window.showErr = m => errs.push(String(m));
const cp = x => x === undefined ? null : JSON.parse(JSON.stringify(x));
const press = (key, shift) => { shown = ITEMS.slice(); focusIdx = 0;
  kd({ key, shiftKey: !!shift, ctrlKey: false, metaKey: false, altKey: false, target: {}, preventDefault() {} }); };
const o = { wrapped: window.setDecision !== undefined && String(window.setDecision).includes('usable') };
const snap = (name) => { o[name] = { r1: cp(DEC['RM_Pod']), r2: cp(DEC['RM_Bush']), errs: errs.splice(0) }; };
const reset = () => { for (const k of Object.keys(DEC)) delete DEC[k]; errs.length = 0; };
if (__MODE === 'keys') {
  press('4'); snap('otherLane');       // D: a set of the YOUNG lane, not the primary
  press('5'); snap('unassigned');      // E: an unassigned render
  press('6'); snap('reference');       // F: a reference render
  press('8'); snap('absent');          // H: no such set on the row
  press('2'); snap('own');             // B: a set of the primary slot
  press('2'); snap('again');           // the hotkey path re-picks; it is not a toggle
  press('r'); snap('redo');
} else {
  press('$', true); snap('bulkD');     // shift+4: group bulk D over both rows
  reset(); press('@', true); snap('bulkB');
}
console.log(JSON.stringify(o));
"""


def opts(bulk: bool):
    import art_sheet as A
    out = A.pick_options(8)            # A..H, hotkeys 1..8, then redo / hold — the biome sheet's real options
    if bulk:                           # defense in depth: if a template or config change lost bulk:false
        out = [dict(o, bulk=True) if len(o["key"]) == 1 else o for o in out]
    return out


def _stub() -> str:
    """BN.STUB, but an element's querySelector answers another catch-all element (patchRow paints into a row's .label)."""
    old = "if (p === 'querySelector') return () => null;"
    if old not in BN.STUB:
        raise RuntimeError("selftest_sheet_bulk_nobulk.STUB changed: element querySelector line not found")
    return BN.STUB.replace(old, "if (p === 'querySelector') return sel => mk(name + '.q(' + sel + ')');", 1)


def run(mode: str, bulk: bool = False, mutate: str = ""):
    import sheet_js_harness as H
    node = H.node()
    render = H.render_script()
    page = BN.page_script()
    if mutate == "no_guard":
        if GUARD_LINE not in render:
            raise RuntimeError("guard line not found in COMMON_JS (mutation control cannot be placed)")
        render = render.replace(GUARD_LINE, "if (false) { if (typeof showErr === 'function') showErr(", 1)
    elif mutate == "nonglobal":
        if TPL_DECL not in page:
            raise RuntimeError("template setDecision declaration not found (mutation control cannot be placed)")
        page = page.replace(TPL_DECL, "const setDecision = function (id, key, opts = {}) {", 1)
    cfg = {"sheetId": "selftest_hotkey_keydown", "title": "t", "options": opts(bulk), "groupLabel": "group",
           "media": True, "schema": 2}
    pre = ("const __CFG = %s; const __ITEMS = %s; const __MODE = %s;\n"
           % (json.dumps(cfg), json.dumps(ITEMS), json.dumps(mode))) + _stub() + "globalThis.scrollBy = () => {}; globalThis.scrollTo = () => {};\n"
    prog = pre + render + "\n" + page + "\n;(() => {\n" + DRIVE + "\n})();"
    r = subprocess.run([node, "-e", prog], capture_output=True, text=True, timeout=60)
    if r.returncode:
        raise RuntimeError("node failed: " + (r.stderr or r.stdout)[-1200:])
    return json.loads([ln for ln in r.stdout.splitlines() if ln.strip()][-1])


def refused(snapshot) -> bool:
    return snapshot["r1"] is None and any("not a set of" in e for e in snapshot["errs"])


def key_checks(o, tag=""):
    check(o["wrapped"], tag + "the guard wrapper is the window.setDecision the page ends up with")
    check(refused(o["otherLane"]), tag + "keydown 4 (D, a set of the YOUNG lane) is refused: nothing written, error shown")
    check(refused(o["unassigned"]), tag + "keydown 5 (E, an unassigned render) is refused")
    check(refused(o["reference"]), tag + "keydown 6 (F, a reference render) is refused")
    check(refused(o["absent"]), tag + "keydown 8 (H, absent from the row) is refused")
    own = o["own"]["r1"] or {}
    check(own.get("decision") == "B" and ((own.get("slots") or {}).get("R/Grown") or {}).get("pick") == "B",
          tag + "keydown 2 (B, a set of the primary slot) records decision B and the grown slot's pick")
    again = o["again"]["r1"] or {}
    check(again.get("decision") == "B", tag + "keydown 2 again keeps B")
    redo = o["redo"]["r1"] or {}
    check(redo.get("decision") == "redo" and ((redo.get("slots") or {}).get("R/Grown") or {}).get("state") == "redraw",
          tag + "keydown r marks the primary slot redraw")


def main() -> int:
    import sheet_js_harness as H
    if not H.node():
        print("UNMEASURED: node not found")
        return 3
    if not BN.TEMPLATE.exists():
        print("UNMEASURED: template not reachable at %s" % BN.TEMPLATE)
        return 3

    key_checks(run("keys"))

    b = run("bulk")                    # the shipped options: letters are bulk:false, so shift-digit sets nothing
    check(b["bulkD"]["r1"] is None and b["bulkD"]["r2"] is None and b["bulkB"]["r1"] is None,
          "shift+4 / shift+2 with the shipped bulk:false letter options set nothing on any row")
    bb = run("bulk", bulk=True)        # bulk re-enabled: the guard must still refuse per row
    check(bb["bulkD"]["r1"] is None and (bb["bulkD"]["r2"] or {}).get("decision") == "D"
          and any("not a set of" in e for e in bb["bulkD"]["errs"]),
          "shift+4 with bulk enabled: refused on the row where D is the young lane, recorded where D is the primary's")
    check((bb["bulkB"]["r1"] or {}).get("decision") == "B" and (bb["bulkB"]["r2"] or {}).get("decision") == "B",
          "shift+2 with bulk enabled: B (a primary set on both rows) lands on both")

    # Mutation controls: the instrument must see a guard that is gone or never installed.
    for name in ("no_guard", "nonglobal"):
        m = run("keys", mutate=name)
        leaked = ((m["otherLane"]["r1"] or {}).get("decision") == "D")
        check(leaked, f"control [{name}]: the same keydown 4 now writes D — the refusal checks above would go red")
        mb = run("bulk", bulk=True, mutate=name)
        check((mb["bulkD"]["r1"] or {}).get("decision") == "D",
              f"control [{name}]: shift+4 bulk now writes D on the young-lane row")

    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
