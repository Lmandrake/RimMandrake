#!/usr/bin/env python3
"""prove_level_alloc.py - live clause A1 of LEVEL_ALLOC_SHRINK_EIGHTFOLD_OVER_BAR.

The item: ProofLevelPerf's LEVEL_PERF_ALLOC row read allocKBAvg 8747.8 KB per levelling cycle on the 8-rig rehearsal
against the 1024 KB bar. Done when (item note 2026-10-29) LEVEL_PERF_ALLOC passes (allocKBAvg <= 1024) at 100-rig scale on
the current build; round5 (2026-10-26, FlowWorks fa833277f8) read 428.4 KB at 100 rigs
(infrastructure/state/evidence/LEVEL_STAGING_DIAGNOSE_FREEZE_ON_BIG_MAP/perf_L0_timed.txt).

Site: the scene round5 measured, re-made in the running game by the item's live-site line (src/RimMandrake/FlowWorks/
stage_proof_site.py: a fresh 325x325 map, 100 rigs, hose maxLength held at 80). Not the save BENCH_r17_midrain: every reading
on it peaks at links=50 (GAMEENV_FIX_PROOFSITE_DFFDAFCB_ITEMS_WAIT). This script then makes these bridge calls:
  1. jawa/map_info                              the current map must be 325x325 (else the site is wrong: exit 2);
  2. RM_NorthstarProofs.ProofLevelPerf("4")     warm-up cycles, not judged (the first cycle after a load rebuilds hose
                                                links and components, a one-off cost that is not per-cycle steady state);
  3. RM_NorthstarProofs.ProofLevelPerf("20")    the measured run, the same instrument and call count as round5.
ProofLevelPerf runs real RM_Levelling.Tick cycles on the current map (water moves, as the game would move it 20 cycles
later); it writes no save. Last, whatever happened, it puts hose maxLength back to the shipped 40 the site left at 80.

Holds when: allocKBAvg <= 1024 (the LEVEL_PERF_ALLOC bar, pipe_levelling_perf_proof.py), measured over >= 10 calls with
no GC inside them (allocCalls; GC.GetTotalMemory is a lower bound, meaningful only in a GC-free call), and links >= 100
(100-rig scale; fewer links means the site is not the 100-rig scene: exit 2). msAvg is reported, not judged here.
Exit 0 = the clause holds, 1 = it does not, 2 = it could not be measured (instrument or site).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PERF = re.compile(r"LEVELPERF calls=(?P<calls>\d+) msAvg=(?P<ms>[\d.]+) msMax=(?P<max>[\d.]+) .*?allocKBAvg=(?P<kb>NaN|[\d.]+)"
                  r" allocCalls=(?P<ac>\d+) gcs=(?P<gcs>\d+) links=(?P<links>\d+)")
BAR_KB = 1024.0
MIN_LINKS = 100
MIN_ALLOC_CALLS = 10
MAP_SIDE = 325
CALLS, WARMUP = 20, 4
HOSE_SETTINGS = "RimMandrake.FlowWorks.Hose.RM_HoseSettings"
SHIPPED_MAX_LENGTH = "40"   # HoseMath.DefaultMaxLength; the site holds 80 so a hose reaches the far lip


def judge(perf_text: str, map_size=None) -> tuple[int, str]:
    """(ProofLevelPerf("20") text, (x, z) of the current map) -> (exit code, verdict line). Pure, testable offline."""
    if map_size is None or tuple(map_size) != (MAP_SIDE, MAP_SIDE):
        return 2, f"SITE: current map is {map_size}, need {MAP_SIDE}x{MAP_SIDE} (the site line stages it: FlowWorks/stage_proof_site.py)"
    m = PERF.search(perf_text or "")
    if not m:
        return 2, f"INSTRUMENT ERROR: no LEVELPERF line in {perf_text!r:.300}"
    calls, links, ac = int(m["calls"]), int(m["links"]), int(m["ac"])
    if calls != CALLS:
        return 2, f"INSTRUMENT ERROR: asked for {CALLS} calls, the readout ran {calls} | {perf_text.strip()}"
    if links < MIN_LINKS:
        return 2, f"SITE: links={links} < {MIN_LINKS}: not the 100-rig scene | {perf_text.strip()}"
    if m["kb"] == "NaN" or ac < MIN_ALLOC_CALLS:
        return 2, (f"UNMEASURED: only {ac} GC-free calls of {calls} (need >= {MIN_ALLOC_CALLS}) | {perf_text.strip()}")
    kb = float(m["kb"])
    if kb > BAR_KB:
        return 1, f"FAIL A1: allocKBAvg {kb:.1f} KB > {BAR_KB:g} KB per cycle at links={links} | {perf_text.strip()}"
    return 0, (f"PASS A1: allocKBAvg {kb:.1f} KB <= {BAR_KB:g} KB per cycle over {ac} GC-free calls, links={links},"
               f" msAvg {float(m['ms']):.3f} | {perf_text.strip()}")


def _map_size(info: dict):
    """jawa/map_info reply -> (x, z) or None; reads `size` as [x, y, z] / {x, z} / "(x, y, z)", or sizeX/sizeZ."""
    d = info.get("result", info) if isinstance(info, dict) else {}
    if not isinstance(d, dict):
        return None
    s = d.get("size") or d.get("mapSize")
    if isinstance(s, dict) and "x" in s and "z" in s:
        return int(s["x"]), int(s["z"])
    if isinstance(s, (list, tuple)) and len(s) in (2, 3):
        return int(s[0]), int(s[-1])
    if isinstance(s, str):
        n = re.findall(r"\d+", s)
        if len(n) in (2, 3):
            return int(n[0]), int(n[-1])
    if "sizeX" in d and "sizeZ" in d:
        return int(d["sizeX"]), int(d["sizeZ"])
    return None


def put_back(session) -> None:
    """Hose maxLength -> shipped. Never changes the verdict: the reading is already taken, and a game that cannot answer here
    is restarted by the lane anyway. None: the bridge never opened, so nothing can be asked."""
    if session is None:
        return
    try:
        # restore-check: ok this IS the restore of the 80 the live-site line left; both proofs call it in a finally
        r = session.call("jawa/mod_settings_field", {"typeName": HOSE_SETTINGS, "action": "set", "field": "maxLength",
                                                     "value": SHIPPED_MAX_LENGTH})
        if isinstance(r, dict) and r.get("success") is False:
            print(f"note: hose maxLength not put back: {str(r)[:160]}")
    except Exception as e:  # noqa: BLE001
        print(f"note: hose maxLength not put back: {type(e).__name__}: {e}")


def main() -> int:
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    s = None
    try:
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        s = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
        s.connect()
        size = _map_size(s.call("jawa/map_info", {}) or {})
        if size != (MAP_SIDE, MAP_SIDE):
            rc, line = judge("", size)
            print(line)
            return rc
        texts = []
        for n in (WARMUP, CALLS):
            r = s.call("jawa/static_call", {"type": NPROOF, "method": "ProofLevelPerf", "args": str(n)}) or {}
            texts.append(str(r.get("result", "")) if isinstance(r, dict) else str(r))
    except Exception as e:  # noqa: BLE001 - any bridge failure is an instrument error, never a verdict
        print(f"INSTRUMENT ERROR: {type(e).__name__}: {e}")
        return 2
    finally:
        put_back(s)
    rc, line = judge(texts[1], size)
    print(line + " | warm-up: " + texts[0].strip()[:200])
    return rc


if __name__ == "__main__":
    sys.exit(main())
