#!/usr/bin/env python3
"""selftest for prove_level_alloc.judge (LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR live clause A1), offline.

The round5 100-rig readout (428.4 KB, evidence perf_L0_timed.txt) and a just-under-bar one go green; the item's own
rehearsal reading (8747.8 KB), an over-bar 100-rig reading, a rehearsal-scale link count, an all-GC run, a short run, the
wrong map and garbage must not. Exit 0 = every case as expected.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prove_level_alloc as P  # noqa: E402

ROOT = HERE.parents[2]
EVIDENCE = ROOT / "infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/perf_L0_timed.txt"


def perf(kb="428.4", ac=20, gcs=0, links=100, calls=20, ms="6.902"):
    return (f"LEVELPERF calls={calls} msAvg={ms} msMax=10.672 msPerTick=0.02761 allocKBAvg={kb} allocCalls={ac} gcs={gcs}"
            f" links={links} moves=755 cycleTicks=250")


def round5_text():
    """The real round5 LEVEL_PERF_ALLOC row's perf string, read from the committed evidence copy."""
    for line in EVIDENCE.read_text(encoding="utf-8").splitlines():
        if line.startswith("LEVEL_PERF_ALLOC"):
            return re.search(r'"perf": "(LEVELPERF [^"]*)"', line)[1]   # the row's detail is truncated, not whole JSON
    raise SystemExit("evidence row LEVEL_PERF_ALLOC missing from " + str(EVIDENCE))


BIG = (325, 325)
CASES = [
    ("round5 real readout, 428.4 KB at 100 links: PASS", round5_text(), BIG, 0),
    ("1024.0 KB exactly (bar is <=): PASS", perf("1024.0"), BIG, 0),
    ("1024.1 KB: FAIL", perf("1024.1"), BIG, 1),
    ("the item's own 8747.8 KB at 100 links: FAIL", perf("8747.8", ac=18, gcs=2), BIG, 1),
    ("rehearsal scale, 6 links: SITE", perf("8747.8", ac=198, gcs=2, links=6, calls=20), BIG, 2),
    ("every call saw a GC (NaN): UNMEASURED", perf("NaN", ac=0, gcs=20), BIG, 2),
    ("only 9 GC-free calls: UNMEASURED", perf("300.0", ac=9, gcs=11), BIG, 2),
    ("ran 4 calls not 20: INSTRUMENT", perf("300.0", ac=4, calls=4), BIG, 2),
    ("250 map: SITE", perf(), (250, 250), 2),
    ("no map: SITE", perf(), None, 2),
    ("refusal text: INSTRUMENT", "REFUSED: arg must be n (1..200) on the current map", BIG, 2),
]


class Rec:
    """A client recording its calls; `boom` raises on every call."""
    def __init__(self, boom=False):
        self.calls, self.boom = [], boom

    def call(self, tool, params=None):
        self.calls.append((tool, params))
        if self.boom:
            raise RuntimeError("bridge gone")
        return {}


def site_cases():
    """-> [(name, ok)]: the proof line stands on the staged scene, not the save, and the proof puts maxLength back."""
    out = []
    r = Rec()
    P.put_back(r)
    out.append(("put_back sets hose maxLength to the shipped 40",
                r.calls == [("jawa/mod_settings_field", {"typeName": P.HOSE_SETTINGS, "action": "set", "field": "maxLength", "value": "40"})]))
    P.put_back(None)
    out.append(("put_back with no client does not raise (reaching this line is the check)", True))
    P.put_back(Rec(boom=True))
    out.append(("put_back on a dead bridge does not raise over the reading (reaching this line is the check)", True))
    for item in ("LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR", "PERF_SCENE_REMEASURE_BASINS_OFF_EDGE"):
        text = (ROOT / "infrastructure/state/live_proofs" / (item + ".txt")).read_text(encoding="utf-8")
        site = [ln for ln in text.splitlines() if ln.startswith("live-site A1:")]
        out.append((f"{item}: the site stages the scene, with the time it needs",
                    len(site) == 1 and "--game --stage-with FlowWorks --max-seconds" in site[0]))
        out.append((f"{item}: the site loads no r17 (it peaks at links=50)", len(site) == 1 and "--save" not in site[0]))
    src = (HERE / "prove_level_alloc.py").read_text(encoding="utf-8")
    out.append(("the links gate and the bar stand", P.MIN_LINKS == 100 and P.BAR_KB == 1024.0 and "finally:\n        put_back(s)" in src))
    return out


def main() -> int:
    bad = 0
    for name, ok in site_cases():
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {name}")
    for name, text, size, want in CASES:
        rc, line = P.judge(text, size)
        ok = rc == want
        bad += not ok
        print(f"{'ok ' if ok else 'BAD'} {name}: exit {rc} (want {want}) {line[:120]}")
    for reply, want in (({"sizeX": 325, "sizeZ": 325}, BIG), ({"result": {"sizeX": 250, "sizeZ": 250}}, (250, 250)),
                        ({"size": "(325, 1, 325)"}, BIG), ({}, None)):
        got = P._map_size(reply)
        bad += got != want
        print(f"{'ok ' if got == want else 'BAD'} _map_size({reply}) = {got} (want {want})")
    print(f"{len(CASES) + 4 - bad}/{len(CASES) + 4} PASS" if not bad else f"FAILED {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
