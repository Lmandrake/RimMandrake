#!/usr/bin/env python3
"""selftest_vent_site_reuse.py - offline guard for CAULDRON_VENT_ENRICHMENT_HOOKS_1 (vents/vent_weather_multiplier).

The vent is indestructible on purpose (destroyable false, like a geyser), so the pad clean-up cannot remove one. A retry
on the same map (testq attempt .a2) found attempt 1's vent, drunk silent by the vexxiss rows, still on the pad: "Vent
state: recovering, 17%", "Vent output: 0.17x" (SteveDesktop Cauldron_20261106T133702Z and Cauldron_20261114T062213Z, both
.a2; every .a1 passed). Not a mod defect: the site carried an old vent into a row that needs a fresh one.

  C1 RM_Building_CauldronVent.ProofResetVentsIn exists, is public static string(string), and resets all four vent
     fields (temperament, lastBlowoutTick, suppression, silencedUntil) and bloomSeen to their declared defaults
  C2 both site-ready rows (vents_site_ready, gas_site_ready) call it over the pad AFTER the spawn and BEFORE the first read,
     and refuse (UNMEASURED) when it does not answer RESET
  C3 both rows pick the vent standing at the anchor, never rows[0] of whatever list_things returns

Live confirmation (UNRUN here, offline night): validation.py --chains vents run twice on one quicktest Cauldron map, the
second run's vent_weather_multiplier PASS.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CS = os.path.join(HERE, "Source", "RM_CauldronVents.cs")
PY = os.path.join(HERE, "validation.py")
ROWS = ("vents_site_ready", "gas_site_ready")


def method(text, name):
    m = re.search(r"public\s+static\s+string\s+%s\s*\(\s*string\s+\w+\s*\)\s*\{" % name, text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[m.end():i - 1]


def row(py, name):
    """The source of the `with _comp(t, "<name>"...)` block: from its line up to the next `with _comp(` at that indent."""
    m = re.search(r"^( *)with _comp\(t, \"%s\"[^\n]*\n" % name, py, re.M)
    if not m:
        return None
    ind = m.group(1)
    end = re.compile(r"^%s\S" % ind, re.M).search(py, m.end())
    return py[m.end():end.start() if end else len(py)]


def func(py, name):
    """The source of a top-level `def name(` up to the next top-level line."""
    m = re.search(r"^def %s\(" % name, py, re.M)
    if not m:
        return None
    end = re.compile(r"^\S", re.M).search(py, m.end())
    return py[m.start():end.start() if end else len(py)]


def check(cs, py):
    fails = []
    body = method(cs, "ProofResetVentsIn")
    if body is None:
        fails.append("C1 no public static string ProofResetVentsIn(string) in RM_CauldronVents.cs")
    else:
        for f, v in (("temperament", "RM_VentTemperament.Stable"), ("lastBlowoutTick", "NeverBlew"),
                     ("suppression", "0f"), ("silencedUntil", "-1"), ("bloomSeen", "false")):
            if not re.search(r"\.%s\s*=\s*%s\s*;" % (f, re.escape(v)), body):
                fails.append("C1 ProofResetVentsIn does not reset %s to %s" % (f, v))
    for name in ROWS:
        src = row(py, name)
        if src is None:
            fails.append("C2 no %s row in validation.py" % name)
            continue
        spawn, pick = src.find("spawn_batch"), src.find("_vent_at_anchor(")
        first_read = min([i for i in (src.find("vent()"), src.find("gas()"), src.find("_wait(")) if i >= 0] or [len(src)])
        if pick < 0 or not spawn < pick < first_read:
            fails.append("C2 %s does not reset the pad's vents (_vent_at_anchor) between the spawn and the first read" % name)
        if "rows[0]" in src:
            fails.append("C3 %s still takes rows[0]" % name)
    helper = func(py, "_vent_at_anchor")
    if helper is None:
        fails.append("C3 no _vent_at_anchor helper")
    else:
        if '"ProofResetVentsIn"' not in helper:
            fails.append("C2 _vent_at_anchor does not call ProofResetVentsIn")
        if not re.search(r'if not \w+\.startswith\("RESET"\):\s*\n\s*_unmeasured\(', helper):
            fails.append("C2 _vent_at_anchor does not refuse a reset that did not answer RESET")
        if "anchor" not in helper or "min(" not in helper:
            fails.append("C3 _vent_at_anchor does not pick the vent nearest the anchor")
    return fails


def main():
    with open(CS, encoding="utf-8") as f:
        cs = f.read()
    with open(PY, encoding="utf-8") as f:
        py = f.read()
    fails = check(cs, py)
    # the guard must see the broken base shape: a row that takes rows[0] with no reset
    base = 'def x(t):\n    with _comp(t, "vents_site_ready", poison=True):\n        spawn_batch\n        ids["vent"] = rows[0]["id"]\n' \
           '        out = vent()\n    with _comp(t, "gas_site_ready", poison=True):\n        spawn_batch\n        ids["vent"] = rows[0]["id"]\n'
    got = {f[:2] for f in check("", base)}
    if not {"C1", "C2", "C3"} <= got:
        fails.append("C0 the guard passes the base shape (%s)" % sorted(got))
    for f in fails:
        print("FAIL", f)
    print("ALL PASS" if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
