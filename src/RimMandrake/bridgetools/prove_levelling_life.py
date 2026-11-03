#!/usr/bin/env python3
"""prove_levelling_life.py - live clause L1 of LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE, read-only.

The clause: after a COLD launch, the first Levelling cycle on BENCH_r17_midrain map1 (325x325, the 100 hose rigs) and
every cycle of the next >= 1000 ticks stay under 20 ms. Three read-only bridge reads decide it:
  1. RM_Levelling.ProofTiming("life")  - whole-process readout (never reset): pre-JIT result, cycles walked, slowest cycle.
  2. RM_Levelling.ProofTiming("")      - LEVELTIME; its first=[...] holds the first 3 Levelling calls of the process
     (only a "reset" arg clears it; this script never passes one). Each entry carries map=, walked=, ports=, tick=.
  3. the ticksGame jawa/static_call returns beside the second read - ticks now.
It holds when ALL of:
  - prejit Compiled > 0 and Failed == 0;  workCycles >= 4;  lifetime maxMs < 20 (and the readout's own pass=True);
  - the first WORKING (walked > 0) entry in first=[...] is the r17 map1 cycle: map=1, ports >= 28, walked >= 35000
    (it4 cold launch measured map=1 ports=28 walked=39752; it2 reproduced walked=39752 exactly; evidence
    D:\\ClaudeWork\\rimmandrake\\levelling_spike\\run\\it4_SETUP_pt.txt);
  - every first=[...] entry up to it sits in the r17 load window: tick in [R17_TICK_LO, R17_TICK_HI) (the save loads at
    tick 48007; one pump cycle is 250 ticks). A process that loaded another save first, or a profile that was reset
    later, puts the first entries elsewhere and fails;
  - ticksGame now - that first r17 tick >= 1000, and that cycle's ms <= the lifetime max (same process, so it must be).
Exit 0 = the clause holds, 1 = it does not (or the game cannot show it yet), 2 = instrument error.
It calls nothing that changes the game.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LIFE = re.compile(r"LEVELLIFE prejit=(?P<ok>\d+)/(?P<bad>\d+) .*?workCycles=(?P<n>\d+) maxMs=(?P<ms>[\d.]+) .*pass=(?P<pass>\w+)")
FIRST = re.compile(r"\bfirst=\[(?P<body>.*)\]\s*$", re.S)
ENTRY = re.compile(r"^(?P<ms>[\d.]+)ms\(.*?:walked=(?P<walked>\d+):ports=(?P<ports>\d+):.*?:map=(?P<map>-?\d+):tick=(?P<tick>\d+)$")

R17_MAP = 1            # BENCH_r17_midrain map1 is Map.Index 1 (it4: map=1)
R17_MIN_PORTS = 28     # it4 first map1 cycle: ports=28
R17_MIN_WALKED = 35000  # it4/it2 first map1 cycle: walked=39752
R17_TICK_LO, R17_TICK_HI = 48000, 48300  # the save loads at tick 48007 (it4 first=[...] tick=48007); one cycle = 250 ticks
MIN_TICKS_RUN = 1000
MIN_CYCLES = 4
BAR_MS = 20.0


def entries(time_text: str) -> list[dict]:
    """LEVELTIME text -> its first=[...] entries, parsed; an unparseable entry is kept as {'raw': ...}."""
    m = FIRST.search((time_text or "").strip())
    if not m or not m["body"].strip():
        return []
    out = []
    for raw in m["body"].split(" | "):
        e = ENTRY.match(raw.strip())
        out.append({"ms": float(e["ms"]), "walked": int(e["walked"]), "ports": int(e["ports"]), "map": int(e["map"]),
                    "tick": int(e["tick"])} if e else {"raw": raw})
    return out


def judge(life_text: str, time_text: str = "", ticks_now: int | None = None) -> tuple[int, str]:
    """(ProofTiming('life'), ProofTiming(''), ticksGame) -> (exit code, verdict line). Pure, so it is testable offline."""
    m = LIFE.search(life_text or "")
    if not m:
        return 2, f"INSTRUMENT ERROR: no LEVELLIFE line in {life_text!r:.300}"
    if "LEVELTIME" not in (time_text or ""):
        return 2, f"INSTRUMENT ERROR: no LEVELTIME line in {time_text!r:.300}"
    if ticks_now is None:
        return 2, "INSTRUMENT ERROR: no ticksGame"
    ok, bad, n, ms = int(m["ok"]), int(m["bad"]), int(m["n"]), float(m["ms"])
    fails = []
    if ok == 0 or bad:
        fails.append(f"prejit {ok}/{bad}")
    if n < MIN_CYCLES:
        fails.append(f"only {n} work cycles (need >= {MIN_CYCLES}: run the save longer)")
    if ms >= BAR_MS:
        fails.append(f"lifetime max {ms:.2f} ms >= {BAR_MS:g}")
    if m["pass"] != "True" and not fails:
        fails.append("readout says pass=" + m["pass"])
    es = entries(time_text)
    if any("raw" in e for e in es):
        return 2, "INSTRUMENT ERROR: unparseable first=[...] entry " + repr(next(e["raw"] for e in es if "raw" in e))[:200]
    work = next((i for i, e in enumerate(es) if e["walked"] > 0), None)
    if work is None:
        fails.append(f"no working cycle among the process's first {len(es)} Levelling calls (first=[] empty or all walked=0)")
    else:
        w = es[work]
        if w["map"] != R17_MAP or w["ports"] < R17_MIN_PORTS or w["walked"] < R17_MIN_WALKED:
            fails.append(f"first working cycle is not r17 map1 (map={w['map']} ports={w['ports']} walked={w['walked']};"
                         f" need map={R17_MAP} ports>={R17_MIN_PORTS} walked>={R17_MIN_WALKED})")
        out = [e["tick"] for e in es[:work + 1] if not R17_TICK_LO <= e["tick"] < R17_TICK_HI]
        if out:
            fails.append(f"first calls at tick {out} are outside the r17 load window [{R17_TICK_LO},{R17_TICK_HI})"
                         " (another save loaded first in this process, or the profile was reset)")
        if ticks_now - w["tick"] < MIN_TICKS_RUN:
            fails.append(f"only {ticks_now - w['tick']} ticks since the first r17 cycle (need >= {MIN_TICKS_RUN})")
        if w["ms"] > ms + 0.005:
            fails.append(f"first r17 cycle {w['ms']:.2f} ms > lifetime max {ms:.2f} ms (readouts disagree)")
    if fails:
        return 1, "FAIL L1: " + "; ".join(fails) + " | " + life_text.strip()
    w = es[work]
    return 0, (f"PASS L1: prejit {ok}/0, {n} cycles, lifetime max {ms:.2f} ms; first r17 map1 cycle {w['ms']:.2f} ms"
               f" (ports={w['ports']} walked={w['walked']} tick={w['tick']}), {ticks_now - w['tick']} ticks since | "
               + life_text.strip())


def main() -> int:
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    try:
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        s = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
        s.connect()
        texts, ticks = [], None
        for arg in ("life", ""):
            r = s.call("jawa/static_call", {"type": "RimMandrake.FlowWorks.Machinery.RM_Levelling",
                                            "method": "ProofTiming", "args": arg}) or {}
            texts.append(str(r.get("result", "")) if isinstance(r, dict) else str(r))
            ticks = r.get("ticksGame") if isinstance(r, dict) else None  # static_call reports ticksGame with the result
    except Exception as e:  # noqa: BLE001 - any bridge failure is an instrument error, never a verdict
        print(f"INSTRUMENT ERROR: {type(e).__name__}: {e}")
        return 2
    rc, line = judge(texts[0], texts[1], int(ticks) if isinstance(ticks, (int, float)) else None)
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
