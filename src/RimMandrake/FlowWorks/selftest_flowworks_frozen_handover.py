#!/usr/bin/env python3
"""FROZEN_OVERFLOW_DIG_FIX_ICE_POURS_LIQUID (offline, no game): reads FlowWorks source and fails on the pre-fix code.

HandOverTakenCells (Sheet/RM_MapComponent_Sheet.cs) runs before the kernel pulse and hands a wet square the engine now owns
(dug under the sheet: Receiver; a lake under it: Sink) to the channel or lake. It had no Tier.Ice check, so a sheet frozen
on undug ground poured into the canal as liquid the moment that square was dug, against D10 (RM_SheetMath: ice neither
flows nor returns; ReturnAndAbsorb skips it). The handover now skips an iced square in BOTH branches, before any Credit or
HandOver; Freeze (which walks every Occ cell whatever its kind) thaws it later and the next pulse hands it over.
Carries a planted regression (the pre-fix body) that must fail.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "Source")
FAILS = []


def check(name, ok):
    print("  %-5s %s" % ("ok" if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


def read(rel):
    return open(os.path.join(SRC, rel), encoding="utf-8").read()


def body_of(src, sig):
    i = src.index(sig)
    j = src.index("{", i)
    d = 0
    for k in range(j, len(src)):
        d += {"{": 1, "}": -1}.get(src[k], 0)
        if d == 0:
            return src[j:k + 1]
    raise ValueError(sig)


ICE_SKIP = re.compile(r"if \(state\.Tiers\[k\] == Tier\.Ice\)\s*\{?\s*continue;")


def skips_ice_first(body):
    """True when the per-square loop skips an iced square before either branch can pour it."""
    loop = body[body.index("foreach (int k in taken)"):]
    m = ICE_SKIP.search(loop)
    if not m:
        return False
    first_pour = min(loop.index(t) for t in ("HandOver(state", "Credit(k") if t in loop)
    first_sink = loop.index("Kind.Sink")
    return m.start() < first_pour and m.start() < first_sink


def main():
    sheet = read(os.path.join("Sheet", "RM_MapComponent_Sheet.cs"))
    body = body_of(sheet, "private void HandOverTakenCells()")
    check("handover: an iced square is skipped before the Sink and Receiver branches pour it", skips_ice_first(body))
    old = ICE_SKIP.sub("if (false) { continue;", body)
    check("handover: can-fail, the pre-fix body (no ice skip) is refused", not skips_ice_first(old))
    kernel = read("RM_SheetMath.cs")
    ret = body_of(kernel, "private static void ReturnAndAbsorb(State s, World w, Params p, PulseReport rep)")
    check("kernel contract still holds: ReturnAndAbsorb skips ice", "if (s.Tiers[i] == Tier.Ice) continue;" in ret)
    frz = body_of(kernel, "private static void Freeze(State s, World w, Params p, PulseReport rep)")
    check("kernel thaws every Occ cell whatever its kind (a skipped square is handed over after thaw)",
          "foreach (int c in s.Occ)" in frz and "HoldsSheet" not in frz)
    print("FAIL %d" % len(FAILS) if FAILS else "PASS")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
