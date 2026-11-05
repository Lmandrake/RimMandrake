#!/usr/bin/env python3
"""prove_level_nodrain.py - live clause A1 of PERF_SCENE_REMEASURE_BASINS_OFF_EDGE.

The item: the 325x325 perf scene's basins (z2..321) sit inside the 10-square edge band, so with edge sinks on (shipped) both
basins drain off the map (~2084 levels/pulse in the offline bench) and the A3 timing measured drain churn, not levelling.
Done when (item note 2026-10-29): the basins sit >= 10 squares inside the edge OR edge sinks are off, and the A3 levelling
bars are re-measured with no off-map drain. pipe_levelling_perf_proof.py now builds the interior scene (--basins interior)
and refuses a verdict on a draining one; a fresh 200-rig interior scene costs ~1 h of serial hose lays, over a live proof's
limit, so this clause takes the other branch the item allows: edge sinks OFF, on the saved 325 scene.

Site: the saved BENCH_r17_midrain (current map map1, 325x325, the 100 hose rigs), loaded by the item's live-site line.
Bridge calls, in order:
  1. jawa/map_info                                        the current map must be 325x325 (else exit 2, SITE);
  2. RM_NorthstarProofs.ProofDrainGate                    before: the gate must read True here (shipped setting on) -- the
                                                          sanity probe that the instrument can see an open gate;
  3. jawa/mod_settings_field set edgeSinksEnabled=False   RimMandrakeFlowWorksSettings (the setting the pulse reads);
  4. ProofDrainGate                                       gate=False (no drain edge, setting off) and the sunk total s0;
  5. ProofLevelPerf("4") then ProofLevelPerf("20")        warm-up (not judged), then the measured cycles;
  6. ProofDrainGate                                       gate still False: no off-map drain. The gate is the instrument
                                                          (the kernel sinks nothing with it closed); ProofLevelPerf runs
                                                          RM_Levelling.Tick, not the excavation pulse, so `sunk` not above
                                                          s0 is corroboration only (it catches a pulse that ran open);
  7. (finally) edgeSinksEnabled put back to the value read before step 3.
ProofLevelPerf runs real RM_Levelling.Tick cycles (water moves); nothing is saved.

Holds when (the A3 bars of pipe_levelling_perf_proof.py, PROVISIONAL, no owner number): msAvg <= 16 ms a cycle, msPerTick
<= 0.1 ms, allocKBAvg <= 1024 KB over >= 10 GC-free calls, links >= 100 (100-rig scale), moves > 0 (levelling work was
timed), and the drain reads above. Exit 0 = holds, 1 = a bar failed, 2 = could not be measured (instrument or site).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NPROOF = "RimMandrake.FlowWorks.RM_NorthstarProofs"
FWSET = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
PERF = re.compile(r"LEVELPERF calls=(?P<calls>\d+) msAvg=(?P<ms>[\d.]+) msMax=(?P<max>[\d.]+) msPerTick=(?P<tick>[\d.]+)"
                  r" allocKBAvg=(?P<kb>NaN|[\d.]+) allocCalls=(?P<ac>\d+) gcs=(?P<gcs>\d+) links=(?P<links>\d+)"
                  r" moves=(?P<moves>-?\d+)")
GATE = re.compile(r"DRAINGATE gate=(?P<gate>True|False) setting=(?P<setting>True|False) drainEdge=(?P<edge>True|False)"
                  r" sunk=(?P<sunk>-?[\d.]+)")
BAR_MS_CYCLE, BAR_MS_TICK, BAR_KB = 16.0, 0.1, 1024.0
MIN_LINKS, MIN_ALLOC_CALLS, MAP_SIDE = 100, 10, 325
CALLS, WARMUP = 20, 4


def gate(text):
    """ProofDrainGate text -> dict(gate, setting, edge: bool, sunk: float) or None. Pure."""
    m = GATE.search(text or "")
    if not m:
        return None
    return {"gate": m["gate"] == "True", "setting": m["setting"] == "True", "edge": m["edge"] == "True", "sunk": float(m["sunk"])}


def judge(perf_text, map_size, before, during, after):
    """(ProofLevelPerf("20") text, (x, z), the three ProofDrainGate texts) -> (exit code, verdict line). Pure."""
    if map_size is None or tuple(map_size) != (MAP_SIDE, MAP_SIDE):
        return 2, f"SITE: current map is {map_size}, need {MAP_SIDE}x{MAP_SIDE} (load BENCH_r17_midrain, map1)"
    g0, g1, g2 = gate(before), gate(during), gate(after)
    if g0 is None or g1 is None or g2 is None:
        return 2, f"INSTRUMENT ERROR: no DRAINGATE line (old FlowWorks deploy?): {before!r:.120} | {during!r:.120} | {after!r:.120}"
    if not g0["gate"]:
        return 2, f"INSTRUMENT ERROR: the drain gate read closed before the setting was touched (sanity probe): {before.strip()}"
    if g1["gate"] or g2["gate"]:
        why = "a drain edge setter is on the map" if (g1["edge"] or g2["edge"]) else "the setting did not take"
        return 2, f"SITE: the drain gate stayed open ({why}): {during.strip()} | {after.strip()}"
    if g2["sunk"] > g1["sunk"]:
        return 2, f"SITE: {g2['sunk'] - g1['sunk']:.3f} levels sank off the map during the timing with the gate closed | {after.strip()}"
    m = PERF.search(perf_text or "")
    if not m:
        return 2, f"INSTRUMENT ERROR: no LEVELPERF line in {perf_text!r:.300}"
    calls, links, ac, moves = int(m["calls"]), int(m["links"]), int(m["ac"]), int(m["moves"])
    if calls != CALLS:
        return 2, f"INSTRUMENT ERROR: asked for {CALLS} calls, the readout ran {calls} | {perf_text.strip()}"
    if links < MIN_LINKS:
        return 2, f"SITE: links={links} < {MIN_LINKS}: not the 100-rig scene | {perf_text.strip()}"
    if moves <= 0:
        return 2, f"SITE: moves={moves}: no levelling work was timed | {perf_text.strip()}"
    if m["kb"] == "NaN" or ac < MIN_ALLOC_CALLS:
        return 2, f"UNMEASURED: only {ac} GC-free calls of {calls} (need >= {MIN_ALLOC_CALLS}) | {perf_text.strip()}"
    ms, tick, kb = float(m["ms"]), float(m["tick"]), float(m["kb"])
    bad = [s for s, c in ((f"msAvg {ms:.3f} > {BAR_MS_CYCLE:g}", ms > BAR_MS_CYCLE),
                          (f"msPerTick {tick:.5f} > {BAR_MS_TICK:g}", tick > BAR_MS_TICK),
                          (f"allocKBAvg {kb:.1f} > {BAR_KB:g}", kb > BAR_KB)) if c]
    tail = f"links={links} moves={moves}, edge sinks off, gate closed (sunk flat at {g1['sunk']:.3f}: corroboration) | {perf_text.strip()}"
    if bad:
        return 1, "FAIL A1: " + "; ".join(bad) + " | " + tail
    return 0, (f"PASS A1: msAvg {ms:.3f} <= {BAR_MS_CYCLE:g}, msPerTick {tick:.5f} <= {BAR_MS_TICK:g}, allocKBAvg {kb:.1f} <="
               f" {BAR_KB:g} over {ac} GC-free calls, " + tail)


def _map_size(info):
    """jawa/map_info reply -> (x, z) or None (prove_level_alloc's reader)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import prove_level_alloc as PLA  # noqa: E402
    return PLA._map_size(info)


def run(s):
    """The bridge sequence on a connected client `s` (call(tool, params) -> dict). -> (exit code, line). The setting is put
    back in a finally whatever happens after it was set."""
    def static(method, arg=""):
        r = s.call("jawa/static_call", {"type": NPROOF, "method": method, "args": arg}) or {}
        return str(r.get("result", "")) if isinstance(r, dict) else str(r)

    def field(action, value=None):
        p = {"typeName": FWSET, "action": action, "field": "edgeSinksEnabled"}
        if value is not None:
            p["value"] = value
        return s.call("jawa/mod_settings_field", p) or {}

    size = _map_size(s.call("jawa/map_info", {}) or {})
    if size != (MAP_SIDE, MAP_SIDE):
        return judge("", size, "", "", "")
    before = static("ProofDrainGate")
    v0 = field("get").get("value")
    if v0 is None:
        return 2, "INSTRUMENT ERROR: jawa/mod_settings_field could not read edgeSinksEnabled"
    try:
        field("set", "False")
        during = static("ProofDrainGate")
        warm = static("ProofLevelPerf", str(WARMUP))
        perf = static("ProofLevelPerf", str(CALLS))
        after = static("ProofDrainGate")
    finally:
        field("set", str(v0))
    rc, line = judge(perf, size, before, during, after)
    return rc, line + " | warm-up: " + warm.strip()[:160] + " | setting put back to " + str(v0)


def main() -> int:
    sys.path.insert(0, str(ROOT / "src/RimMandrake/Utils"))
    try:
        import rimbridge_client as rb  # noqa: E402
        host, port, token = rb.resolve_endpoint()
        s = rb.RimBridge(host=host, port=port, token=token, timeout=120.0)
        s.connect()
        rc, line = run(s)
    except Exception as e:  # noqa: BLE001 - any bridge failure is an instrument error, never a verdict
        print(f"INSTRUMENT ERROR: {type(e).__name__}: {e}")
        return 2
    print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
