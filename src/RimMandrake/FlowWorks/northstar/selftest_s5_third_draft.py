#!/usr/bin/env python3
"""selftest_s5_third_draft.py -- scene S5's third draft in the sealed scenes file states the exactly-level numbers.

WATER_SCENES_S5_JUDGE_THIRD_DRAFT (plan P10, owner R3 2026-10-17 "Redraw scene S5 with level-water numbers"; R1 exactly
level water; R9 one surface within 1 cm). Checks, on design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json:
  1. the seal recomputes over legend+global+scenes and equals seal.value and the newest revision's new_seal, whose
     old_seal is the 2026-10-17 second-draft seal;
  2. legend, global and S1-S4, S6 are unchanged from the second draft (their content hashes are pinned below);
  3. every litre figure S5 claims is the exact level solution (Fractions, worked from geometry), and the level_water
     oracle settles each part to the same numbers within 1 dL a square;
  4. no whole-notch bound of the second draft survives in S5.

    python3 src/RimMandrake/FlowWorks/northstar/selftest_s5_third_draft.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import selftest_level_water as t  # noqa: E402

REPO = HERE.parents[3]
SCENES = REPO / "design/RimMandrake/vv_methods/water_scenes_2026-10-16.scenes.json"
SECOND_DRAFT_SEAL = "1e0a16af8f1229f1c71d752853507ebb5e3fd2120ce9d3cdfd41c2b3323f05e1"
# content hashes of what the third draft must NOT touch (canonical JSON, as at the second-draft seal)
PINNED = {
    "legend": "d9915a761dd18c1a4f954ccc54b623b10c37a6b6969544e1a385b26c67eaf238",
    "global": "21145262f39e19157862bae226d9b1ea2b05bf8187c3130d0c31233f8049ee0f",
    "S1": "c3c72d372cff1195a2a62f4cc187e64b2e3b9c6e17f4904e4d5c601533c996ec",
    "S2": "af852449481dabd0ec79ecf525e9bb07fe0a187198df7433d4ee46746d53bde3",
    "S3": "46969412d5f0e8731c09fd9c5d27a6b7c6d95a1222d2947e4df38026d3a73f0d",
    "S4": "7452caf1f139725f0ed9d682aeb6c3e19e8bb56e2fbbb93bd895b324ab14161e",
    "S6": "5f0ece8c1fad9808858669fc29e428b4852a4f3004eee17e8b8e9997585b36a1",
}
L_PER_M_SQ = 2000          # 1 m of water in one square = 2,000 L (scenes file, global units)
FAILS = []


def check(name, ok, detail=""):
    print("%s  %s%s" % ("PASS" if ok else "FAIL", name, ("  [%s]" % detail) if detail else ""))
    if not ok:
        FAILS.append(name)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"))


def h(x):
    return hashlib.sha256(canon(x).encode()).hexdigest()


def litres(x):
    """A litre figure as the scenes file writes it: thousands comma, one decimal (to the decilitre)."""
    return "{:,.1f}".format(float(x))


def level(squares, total_m_sq):
    """Exact surface s (metres BELOW ground, >= 0) for squares given as (count, floor depth in m) holding total_m_sq
    metre-squares of water, with every listed square under water; returns s and per-group water depth."""
    n = sum(c for c, _ in squares)
    s = (sum(c * F(d) for c, d in squares) - F(total_m_sq)) / n
    assert all(F(d) > s for _, d in squares), "a listed square would be dry"
    return s, [F(d) - s for _, d in squares]


def main():
    d = json.loads(SCENES.read_text())
    scenes = {s["id"]: s for s in d["scenes"]}
    s5 = scenes["S5"]

    # 1. seal
    got = h({k: d[k] for k in ("legend", "global", "scenes")})
    rev = d["revisions"][-1]
    check("seal recomputes and equals seal.value", got == d["seal"]["value"], got[:12])
    check("newest revision is the third draft: new_seal = seal, old_seal = 2026-10-17 second draft",
          rev.get("new_seal") == got and rev.get("old_seal") == SECOND_DRAFT_SEAL
          and rev.get("item") == "WATER_SCENES_S5_JUDGE_THIRD_DRAFT", "%s -> %s" % (rev.get("old_seal", "")[:8],
                                                                                    rev.get("new_seal", "")[:8]))

    # 2. nothing else moved
    parts = {"legend": d["legend"], "global": d["global"]}
    parts.update({k: scenes[k] for k in ("S1", "S2", "S3", "S4", "S6")})
    for k, v in parts.items():
        check("%s unchanged since the second draft" % k, h(v) == PINNED[k], h(v)[:12])

    text = {e["id"]: e["claim"] for e in s5["expected"]}

    # 3. numbers: exact level solution, in litres to the decilitre
    sA, (pA, cA) = level([(9, 2), (10, "0.5")], 18)              # 36,000 L = 18 m-squares
    check("S5.b surface 5/19 m below ground", sA == F(5, 19), str(sA))
    for want in (litres(cA * L_PER_M_SQ), litres(9 * pA * L_PER_M_SQ), litres(10 * cA * L_PER_M_SQ), "0.263 m",
                 "0.237 m", "1.737 m", "36,000.0 L", "ALL TEN"):
        check("S5.b states %s" % want, want in text["S5.b"])
    sB, (pB, cB) = level([(1, 2), (10, "0.5")], 2)
    check("S5.c surface 5/11 m below ground", sB == F(5, 11), str(sB))
    for want in (litres(cB * L_PER_M_SQ), litres(pB * L_PER_M_SQ), litres(10 * cB * L_PER_M_SQ), "0.455 m",
                 "1.545 m", "4.5 cm", "4,000.0 L", "ALL TEN"):
        check("S5.c states %s" % want, want in text["S5.c"])
    _, (cE,) = level([(36, 1)], 4)
    for want in (litres(cE * L_PER_M_SQ), "0.111 m", "all 36", "8,000.0 L"):
        check("S5.g states %s" % want, want in text["S5.g"])
    _, (pF, cF) = level([(1, 2), (1, 2)], 2)
    check("S5.h each square 1 m (2,000.0 L)", pF == cF == 1 and "2,000.0 L" in text["S5.h"])
    cG = F(4000, 6)                                               # pond emptied into six 0.5 m cells, hoses empty
    check("S5.i six cells under the brim", cG < F(1, 2) * L_PER_M_SQ)
    for want in (litres(cG), "0.333 m", "All six", "4,000.0 L"):
        check("S5.i states %s" % want, want in text["S5.i"])
    for want in ("1,000.0 L",):
        check("S5.f states %s" % want, want in text["S5.f"])
    check("S5.e: the cut-off run is its own body", "a body of their own" in text["S5.e"])

    # oracle agreement (the shipped-kernel twin): within 1 dL a square
    U = t.U
    dl = lambda x: x * L_PER_M_SQ * 10                               # metres in one square -> dL
    o, canal, _, cons = t.s5_pond(9, 36)
    check("oracle A: every canal square = level solution +-1 dL", all(abs(o.W[c] - dl(cA)) <= 1 for c in canal),
          str([o.W[c] for c in canal]))
    check("oracle A: conserved", cons)
    o, canal, _, cons = t.s5_pond(1, 4)
    check("oracle B: every canal square = level solution +-1 dL", all(abs(o.W[c] - dl(cB)) <= 1 for c in canal),
          str([o.W[c] for c in canal]))
    check("oracle B: pond = level solution +-1 dL a square", abs(o.bodies[0]["dl"] - dl(pB)) <= 11, o.bodies[0]["dl"])
    o = t.oracle(8, 8)
    basin = [(x, z) for x in range(1, 7) for z in range(1, 7)]
    for c in basin:
        o.dig(c, 2)
    for c in [(3, 3), (4, 3), (3, 4), (4, 4)]:
        o.set_fill(c, 2)
    t.run_still(o)
    check("oracle E: every basin square = level solution +-1 dL", all(abs(o.W[c] - dl(cE)) <= 1 for c in basin)
          and sum(o.W[c] for c in basin) == 8 * U)
    o, canal, _, _ = t.s5_pond(1, 4, canal_len=1, canal_d=4)
    check("oracle F: 1 m each", o.W[canal[0]] == dl(cF) and o.bodies[0]["dl"] == dl(pF))

    # 4. no whole-notch bound survives
    blob = canon({k: s5[k] for k in ("setup", "expected", "fails_if", "exclusions")}).lower()
    for gone in ("at most 9", "never a 5th", "5th canal cell", "cells 1-4", "at most one canal cell", "27,000",
                 "top 0.5 m", "which 8 basin cells", "keeps at least 3,000"):
        check("S5 no longer says %r" % gone, gone not in blob)

    print("%d failure(s)" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
