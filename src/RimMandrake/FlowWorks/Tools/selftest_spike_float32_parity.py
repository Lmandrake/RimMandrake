#!/usr/bin/env python3
"""SPIKES_PARITY_FIX_FLOAT32_MIRROR: the Python spike mirror (fw_scenes_spikes.py floor_rect / submerged_alpha /
layout) equals the C# RM_SpikeDrawMath BIT FOR BIT as float32, not to 1e-4.

The C# runs in float32 (x0 + Margin = 0.0499999970, not 0.05), so a double mirror can take the other side of a
threshold (cap, lo/hi, bot, cellTop) and keep different stakes. The reference is spike_parity_golden.json: the
production C# run by spike_parity/gen_golden.py (dotnet.exe) over every FloorRect neighbourhood, every alpha, and
~8k Layout rects, among them the rects a boundary search found where doubles and float32 keep DIFFERENT stakes.

Checks: the golden is current (its C# source hash == the sources now); floor_rect, submerged_alpha and layout equal the
C# output lines exactly; x0 + Margin is the float32 0.0499999970. Can-fail: the pre-fix double mirror
(spike_parity/f64_mirror.py) disagrees with the golden, and keeps a different stake COUNT on some threshold rect.

    python3 selftest_spike_float32_parity.py      # exit 0 = all ok
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "spike_parity"))
import fw_scenes_spikes as spk  # noqa: E402
import gen_golden as gen  # noqa: E402
from f64_mirror import layout_f64  # noqa: E402

FAILS = []


def want(ok, what):
    print(("ok   " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def line(quads):
    return " ".join([str(len(quads))] + [gen.bits(v) for q in quads for v in q])


def main():
    g = json.loads(gen.GOLDEN.read_text())
    want(g["source_sha256"] == gen.source_sha(),
         "golden is current: its C# source hash == %s now (else re-run spike_parity/gen_golden.py)" % ", ".join(gen.SOURCES))

    fo = []
    for d, n, s, w, e, faces, outline in gen.floor_cases():
        fo.append(" ".join(gen.bits(v) for v in spk.floor_rect(d, n, s, w, e, bool(faces), bool(outline))))
    want(len(fo) == g["floor_rect"]["cases"] and hashlib.sha256("\n".join(fo).encode()).hexdigest() == g["floor_rect"]["sha256"],
         "floor_rect == C# FloorRect bit for bit over %d neighbourhoods x faces/outline" % len(fo))

    bad = [(f, o, gen.bits(spk.submerged_alpha(f))) for f, o in g["submerged_alpha"] if gen.bits(spk.submerged_alpha(f)) != o]
    want(not bad and len(g["submerged_alpha"]) >= 6, "submerged_alpha == C# SubmergedAlpha bit for bit, fill -1..6 %s" % bad[:3])

    cases = g["layout"]
    want(len(cases) > 5000 and sum(c[6] > 0 for c in cases) > 4000,
         "sanity: the golden holds %d layouts, %d with stakes" % (len(cases), sum(c[6] > 0 for c in cases)))
    want(g["threshold_split_cases"] > 0, "sanity: the golden holds %d rects where doubles and float32 keep different stakes"
         % g["threshold_split_cases"])
    miss, miss64, count64 = [], 0, 0
    for v, seed, a, b, c, d, cnt, dig in cases:
        r = [gen.unbits(x) for x in (a, b, c, d)]
        ln = line(spk.layout(v, seed, *r))
        if hashlib.sha256(ln.encode()).hexdigest()[:16] != dig or int(ln.split(" ")[0]) != cnt:
            miss.append((v, seed, a, b, c, d))
        q64 = layout_f64(v, seed, *r, spk.library(v), spk.MARGIN, spk.hash32)
        miss64 += hashlib.sha256(line(q64).encode()).hexdigest()[:16] != dig
        count64 += len(q64) != cnt
    want(not miss, "layout == C# Layout bit for bit over %d rects (mismatch %d, first %s)" % (len(cases), len(miss), miss[:2]))
    full = [c for c in g["layout_full"] if line(spk.layout(c[0], c[1], *[gen.unbits(x) for x in c[2:6]])) != c[6]]
    want(not full and g["layout_full"], "layout == C# for the %d cases stored whole" % len(g["layout_full"]))

    lo = np.float32(0.04) + np.float32(spk.MARGIN)
    want(gen.bits(lo) == "3d4ccccc" and abs(float(lo) - 0.0499999970) < 1e-9 and float(lo) != 0.05,
         "x0 + Margin at x0 = 0.04 is float32 %.10f (bits %s), as the C#" % (float(lo), gen.bits(lo)))
    fx = spk.layout(*spk.PARITY_LAYOUT)
    want(len(fx) == 18, "SpikeDrawChecks parity fixture: 18 stakes (%d)" % len(fx))

    want(miss64 > 0, "can-fail: the pre-fix double mirror differs from the C# on %d of %d rects" % (miss64, len(cases)))
    want(count64 > 0, "can-fail: ... and keeps a different stake COUNT on %d (a threshold decision)" % count64)
    print("ALL OK" if not FAILS else "%d FAILED" % len(FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
