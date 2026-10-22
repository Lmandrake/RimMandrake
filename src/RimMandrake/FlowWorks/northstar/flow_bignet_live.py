"""FLOW BIG NETWORK live check (FLOW_ORDER_EXTERNAL_INPUT_1 A4: "a dug network over 6000 cells wets end to end off one
source, and its pulse cost is timed; that timing decides whether the default cap rises"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/flow_bignet_live.py <state.json> --phase site|dig|pulse [--fresh-map]
             [--size N] [--max-seconds S]

Resumable in phases (each call stays under the 600 s bridge-call budget; progress is kept in <state.json>):
  site   fresh map (with --fresh-map), wetnessCutoffEnabled OFF for the run (restored by --phase pulse at the end), a
         SIZE x SIZE plot at (12, 20) cleared to Soil, a 3-wide WaterDeep strip on the map edge x = 0..2 and a one-square
         connector row across the sink band (an edge-touching body is limitless by the old rule: the ONE source). With
         --inland the plot is at (106, 90) beside an inland moving-water patch and the setting is left alone; the choice is
         kept in <state.json>, so the dig and pulse phases need no --inland.
  dig    digs the plot 2 notches (1 m), dry, row by row from the source side; resumes where it stopped.
  pulse  jawa/flowworks_pulse in batches of up to 500 (no game ticks), reading the far corner square and the plot's
         excavation summary; stops when the far corner is wet or --max-seconds runs out. The pulse cost is the tool's
         DurationMs / pulses per batch.
Rows (written by --phase pulse):
  FLOW_BIGNET_WETS_END_TO_END   EXPECT the far corner (the square farthest from the source) wet; cells > 6000.
  FLOW_BIGNET_PULSE_COST        MEASURED: ms per pulse per batch (no bar: the owner's cap decision).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
NSP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
S_FW = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
ITEM = "FLOW_ORDER_EXTERNAL_INPUT_1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--phase", required=True, choices=("site", "dig", "pulse"))
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--size", type=int, default=80)
    ap.add_argument("--max-seconds", type=float, default=520)
    ap.add_argument("--inland", action="store_true", help="inland moving-water source, plot at (106, 90)")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    st = json.load(open(a.state)) if os.path.exists(a.state) else {"script": "flow_bignet_live.py", "rows": []}
    if a.phase != "site" and "inland" in st:
        a.inland = st["inland"]          # a dig/pulse call without --inland would otherwise address the wrong plot

    def save():
        with open(a.state + ".tmp", "w", encoding="utf-8") as f:
            json.dump(st, f, indent=1, default=str)
        os.replace(a.state + ".tmp", a.state)

    t_start = time.time()
    # SITE (first live run): the plot started at x=8 inside the map-edge sink band (isSink at x 8..9) and the painted strip
    # was never classified as a body (body_report 'formedByThisCall'), so 114,500 pulses wetted nothing. The plot starts at
    # x=12, a one-square connector row joins it to the strip across the sink band, and the strip is classified at once.
    ox, oz, n = 12, 20, a.size
    if a.inland:
        # second design (belt live 2026-10-22): an INLAND moving-water patch (WaterMovingChestDeep 6x6 at (100,120)) is
        # limitless by the wetness rule's movingWater clause with the shipped settings, and the plot sits well clear of
        # every map-edge sink band
        ox, oz = 106, 90
    if a.phase == "site":
        if a.fresh_map:
            B.call("rimworld/go_to_main_menu")
            B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
        ok, _ = V._wait_playing(B, leave_s=0)
        st["site_calm"] = V.site_calm(B)
        # read the setting only once: a re-run of this phase would otherwise record the already-OFF value as the original
        if "wetness0" not in st:
            st["wetness0"] = (B.call("jawa/mod_settings_field", typeName=S_FW, action="get", field="wetnessCutoffEnabled") or {}).get("value")
        st["inland"] = a.inland
        if not a.inland:
            B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="wetnessCutoffEnabled", value="False")
        rect = (0, oz - 2, ox + n + 2, n + 4) if not a.inland else (96, oz - 2, n + 14, n + 4)
        B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
        r = "%d,%d,%d,%d" % rect
        B.call("jawa/destroy_batch", rects=r, categories="All")
        if a.inland:
            B.call("jawa/set_terrain_batch", ops="Soil:%s;WaterMovingChestDeep:100,%d,6,6" % (r, oz + n // 2 - 3))
        else:
            B.call("jawa/set_terrain_batch", ops="Soil:%s;WaterDeep:0,%d,3,%d" % (r, oz, n))
        B.call("jawa/set_roof_batch", ops="None:" + r)
        B.call("jawa/set_fog", action="unfog", rect=r)
        src = (102, oz + n // 2) if a.inland else (1, oz + n // 2)
        st["sourceBody"] = (B.call("jawa/flowworks_body_report", x=src[0], z=src[1], classify=True) or {}).get("body")
        for x in range(106 if a.inland else 3, ox):
            B.call("jawa/flowworks_excavation_drive", x=x, z=oz + n // 2, deepenLevels=2, setFill=-1)
        st.update(origin=[ox, oz], size=n, dugRows=0, phaseSite=time.strftime("%H:%M:%S"))
        save()
        print("site ready", st.get("site_calm", {}).get("ok") if isinstance(st.get("site_calm"), dict) else "", flush=True)
        return 0
    if a.phase == "dig":
        row0 = st.get("dugRows", 0)
        for j in range(row0, n):
            for i in range(n):
                B.call("jawa/flowworks_excavation_drive", x=ox + i, z=oz + j, deepenLevels=2, setFill=-1)
            st["dugRows"] = j + 1
            if (j + 1) % 5 == 0:
                save()
            if time.time() - t_start > a.max_seconds:
                break
        save()
        print("dug rows %d / %d (%.0f s)" % (st["dugRows"], n, time.time() - t_start), flush=True)
        return 0
    # pulse
    far = (ox + n - 1, oz + n - 1)
    batches = st.setdefault("batches", [])
    wet = False
    while time.time() - t_start < a.max_seconds:
        t0 = time.time()
        r = B.call("jawa/flowworks_pulse", count=500, x=far[0], z=far[1], w=1, h=1, includeBodies=False) or {}
        dt = (r.get("operation") or {}).get("DurationMs") or (time.time() - t0) * 1000
        pulses = r.get("pulsesRun") or 0
        last = (r.get("pulses") or [{}])[-1]
        fill = (last.get("fill") or [0])[0]
        batches.append({"pulses": pulses, "ms": dt, "msPerPulse": (dt / pulses) if pulses else None, "farFill": fill})
        save()
        print("batch %d: %d pulses, %.1f ms/pulse, far fill %s" % (len(batches), pulses, (dt / pulses) if pulses else -1, fill), flush=True)
        if fill and fill > 0:
            wet = True
            break
        if not pulses:
            break
    summ = B.call("jawa/flowworks_excavation_report") or {}
    st["report"] = {k: summ.get(k) for k in list(summ.keys())[:20] if k not in ("operation", "state")}
    total = sum(b["pulses"] for b in batches)
    cells = st["size"] ** 2
    per = [b["msPerPulse"] for b in batches if b.get("msPerPulse")]
    # every way out of the loop (wet, out of time, a batch that ran no pulses) records the rows and restores the setting
    st["rows"] = [r_ for r_ in st["rows"] if not r_["id"].startswith("FLOW_BIGNET")]
    st["rows"].append({"id": "FLOW_BIGNET_WETS_END_TO_END", "status": "PASS" if wet and cells > 6000 else "UNMEASURED" if not wet else "FAIL",
                       "class": "MOD" if wet else "HARNESS", "item": ITEM,
                       "detail": {"cells": cells, "pulsesToFarCorner": total if wet else None, "pulsesRun": total, "farCorner": far,
                                  "dugRows": st.get("dugRows")}})
    st["rows"].append({"id": "FLOW_BIGNET_PULSE_COST", "status": "MEASURED", "class": "MOD", "item": ITEM,
                       "detail": {"msPerPulse": per, "meanMsPerPulse": (sum(per) / len(per)) if per else None,
                                  "note": "flowworks_pulse wall time incl. the bridge round trip, per 500-pulse batch"}})
    B.call("jawa/mod_settings_field", typeName=S_FW, action="set", field="wetnessCutoffEnabled",
           value="True" if st.get("wetness0") is None else str(st["wetness0"]))
    save()
    print(json.dumps(st["rows"][-2:] if st["rows"] else {}, default=str)[:800])
    return 0


if __name__ == "__main__":
    sys.exit(main())
