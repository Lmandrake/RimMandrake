#!/usr/bin/env python3
"""selftest_siege_canfire_cache.py - offline guard for WEB_SIEGE_DESIGN_SPIDERS_BRING_SHADE A2 (siege/setting_off_refuses).

Vanilla IncidentWorker.CanFireNow caches CanFireNowSub per game tick (private lastCheckCanRunTick / lastCanRunResult,
RimWorld/IncidentWorker.cs, read through RimSage 2026-11-15). ProofEligibility asks twice in one tick (off, then on), so the
"on" ask read the "off" answer back: "reason Eligible ... canFire False" on SteveDesktop 2026-11-06, 11-13 and 11-14
(findings WEBWORK_SETTING_OFF_REFUSES_FAILS_7B03A7/_15059A/_21B95D). The mod's worker was never wrong; the proof was.

  C1 no bare `Worker.CanFireNow(` in RM_WebworkSiegeProof.cs: every ask goes through CanFireNowFresh
  C2 CanFireNowFresh clears lastCheckCanRunTick before the ask and again after it (so the storyteller never reads a
     proof-settings answer), and fails loudly when the field is missing instead of asking a cached worker
  C3 ProofEligibility asks through CanFireNowFresh

Live confirmation (UNRUN here, offline night): validation.py --chains siege on a quicktest map, row setting_off_refuses PASS.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source", "RM_WebworkSiegeProof.cs")


def body(text, name):
    """The brace-matched body of the first method named `name`, or None."""
    m = re.search(r"\b%s\s*\([^)]*\)\s*\{" % re.escape(name), text)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(text) and depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[m.end():i - 1]


def check(text):
    fails = []
    code = re.sub(r"//[^\n]*", "", text)
    helper = body(code, "CanFireNowFresh")
    bare = [m.start() for m in re.finditer(r"Worker\.CanFireNow\(", code)]
    inside = 0
    if helper is not None:
        inside = len(re.findall(r"Worker\.CanFireNow\(", helper))
    if len(bare) != inside:
        fails.append("C1 %d CanFireNow ask(s) outside CanFireNowFresh" % (len(bare) - inside))
    if helper is None:
        fails.append("C2 no CanFireNowFresh helper")
    else:
        if '"lastCheckCanRunTick"' not in code:
            fails.append("C2 the helper does not name IncidentWorker.lastCheckCanRunTick")
        ask = helper.find("Worker.CanFireNow(")
        resets = [m.start() for m in re.finditer(r"\.SetValue\(", helper)]
        if ask < 0 or not any(r < ask for r in resets) or not any(r > ask for r in resets):
            fails.append("C2 the cache is not cleared both before and after the ask")
        if not re.search(r"==\s*null\)\s*throw", helper):
            fails.append("C2 a missing cache field does not fail loudly")
    elig = body(code, "ProofEligibility")
    if elig is None or "CanFireNowFresh(" not in elig:
        fails.append("C3 ProofEligibility does not ask through CanFireNowFresh")
    return fails


def main():
    with open(SRC, encoding="utf-8") as f:
        text = f.read()
    fails = check(text)
    # the guard must see a broken proof: the base (bare ask in ProofEligibility) has to fail C1 and C3
    broken = "public static string ProofEligibility(string a) { bool can = X.Worker.CanFireNow(parms); }"
    if not {"C1", "C3"} <= {f[:2] for f in check(broken)}:
        fails.append("C0 the guard passes a bare CanFireNow ask")
    for f in fails:
        print("FAIL", f)
    print("ALL PASS" if not fails else "FAILED %d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
