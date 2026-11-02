#!/usr/bin/env python3
"""prove_levelling_life.py - live clause L1 of LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE, read-only.

Reads RM_Levelling.ProofTiming("life") through jawa/static_call. The readout covers the whole process
(never reset): the start-up pre-JIT result and the slowest Levelling cycle since launch. The clause holds
when, after a cold launch and >=1000 ticks of BENCH_r17_midrain:
  prejit ran with Compiled > 0 and Failed == 0, workCycles >= 4 and maxMs < 20 (the readout's pass=True
  also checks prejit and maxMs; this script adds the contract's >= 4 cycles).

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


def judge(text: str) -> tuple[int, str]:
    """ProofTiming('life') text -> (exit code, verdict line). Pure, so it is testable offline."""
    m = LIFE.search(text or "")
    if not m:
        return 2, f"INSTRUMENT ERROR: no LEVELLIFE line in {text!r:.300}"
    ok, bad, n, ms = int(m["ok"]), int(m["bad"]), int(m["n"]), float(m["ms"])
    fails = []
    if ok == 0 or bad:
        fails.append(f"prejit {ok}/{bad}")
    if n < 4:
        fails.append(f"only {n} work cycles (need >= 4: run the save longer)")
    if ms >= 20.0:
        fails.append(f"lifetime max {ms:.2f} ms >= 20")
    if m["pass"] != "True" and not fails:
        fails.append("readout says pass=" + m["pass"])
    if fails:
        return 1, "FAIL L1: " + "; ".join(fails) + " | " + text.strip()
    return 0, f"PASS L1: prejit {ok}/0, {n} cycles, lifetime max {ms:.2f} ms | " + text.strip()


def main() -> int:
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    try:
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        s = rb.RimBridge(host=host, port=port, token=token, timeout=60.0)
        s.connect()
        r = s.call("jawa/static_call", {"type": "RimMandrake.FlowWorks.Machinery.RM_Levelling",
                                        "method": "ProofTiming", "args": "life"}) or {}
    except Exception as e:  # noqa: BLE001 - any bridge failure is an instrument error, never a verdict
        print(f"INSTRUMENT ERROR: {type(e).__name__}: {e}")
        return 2
    text = r if isinstance(r, str) else json.dumps(r)
    rc, line = judge(text)
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
