"""JAWA IN THE SHALLOWS live proof (JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS).

  python.exe src/RimMandrake/FlowWorks/northstar/jawa_shallows_proof.py [out.json] [--cell X,Z] [--kind RUT_Jawa_Colonist]
                                                                       [--fresh-map] [--max-ticks 6000]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every row PASS. Read-only to the ledger.

What it settles (item finding 5, offline 2026-10-21): Captain's eight RM_PitDrowning downs on the GSS theft run were natural
brine, not a pit. RM_Drowning.HeightOf gives a Jawa 0.5 m (BodySize under the 0.75 band edge, HeightByBand[1]), so a vanilla-
passable shallow pool (RM_SwimWater.WaterMetresAt 0.5 m) is over its head standing (0.45 m) and RM_Swim makes it swim until
RM_SwimExhaustion reaches 1, then drown. The theft run logged no position, so this stages the cell instead of hunting it:

Scene: a 5x5 RM_WaterBrineShallow pool (the RM_Stillsand pool terrain, isSourceCell) painted at --cell (default 120,120) on
soil, inside a cleared 11x11 site; one Jawa colonist spawned at the pool's centre and drafted there (two brine squares to any
shore, so no exit in reach). Reads are jawa/static_call RM_PitFillEffects.ProofDrown and RM_Swim.ProofSwim at that cell.

Rows (MEASURED, all on the record with the cell coordinates):
  JS1_cell_is_shallow_brine   the pawn's cell reads RM_WaterBrineShallow
  JS2_jawa_is_rat_sized       ProofDrown H=0.50 for the Jawa
  JS3_shallows_over_its_head  ProofDrown water > 0.45 m (0.9 H) and under=True standing: the shallows are deep water to a Jawa
  JS4_drowning_fires_there    within --max-ticks, RM_PitDrowning appears on the Jawa in that cell, after RM_Swim reads it
                              swimming (class not None), with ProofDrown headUp=False at the first read that has drowning
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

FILL_TYPE = "RimMandrake.FlowWorks.RM_PitFillEffects"
SWIM_TYPE = "RimMandrake.FlowWorks.Swimming.RM_Swim"
BRINE = "RM_WaterBrineShallow"
JAWA_H = 0.5
HEAD_FRACTION = 0.9            # RM_RelativeRulesMath.DefaultHeadFraction (Mod Settings pitDrowningHeadFraction default)
CHUNK = 250


# ============================================================================ verdicts (pure; selftest_jawa_shallows_proof.py)
def parse(txt):
    """'DROWN id H=0.50 lying=False ...' / 'SWIM id class=Swimmer ...' -> dict with 'id'; '' / REFUSED -> {}."""
    txt = (txt or "").strip()
    if not txt or txt.startswith("REFUSED"):
        return {}
    toks = txt.split()
    kv = {"tag": toks[0]}
    if len(toks) > 1 and "=" not in toks[1]:
        kv["id"] = toks[1]
    for tok in toks[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            kv[k] = v
    return kv


def _f(kv, k):
    try:
        return float(kv[k])
    except (KeyError, ValueError, TypeError):
        return None


def terrain_verdict(terrain):
    if not terrain:
        return "UNMEASURED", {"why": "no terrain read at the cell"}
    return ("PASS" if terrain == BRINE else "FAIL"), {"terrain": terrain, "want": BRINE}


def height_verdict(drown):
    h = _f(drown, "H")
    if h is None:
        return "UNMEASURED", {"why": "no DROWN line", "drown": drown}
    return ("PASS" if abs(h - JAWA_H) < 1e-3 else "FAIL"), {"H": h, "want": JAWA_H}


def over_head_verdict(drown):
    """Standing (lying=False) in water over 0.9 H, and the mod agrees (under=True)."""
    h, w = _f(drown, "H"), _f(drown, "water")
    if h is None or w is None:
        return "UNMEASURED", {"why": "no DROWN line", "drown": drown}
    det = {"water": w, "H": h, "headUnderAt": round(h * HEAD_FRACTION, 4), "lying": drown.get("lying"),
           "under": drown.get("under")}
    if drown.get("lying") != "False":
        return "UNMEASURED", dict(det, why="the Jawa was not standing at the first read (the standing threshold is the claim)")
    ok = w > h * HEAD_FRACTION + 1e-4 and drown.get("under") == "True"
    return ("PASS" if ok else "FAIL"), det


def drowning_verdict(trace):
    """trace: [{tick, severity, drown{}, swim{}}] in order, severity = RM_PitDrowning on the Jawa (0 when absent).
    PASS: a swim read with class != None comes first, then a read with severity > 0 whose ProofDrown says headUp=False."""
    if not trace:
        return "UNMEASURED", {"why": "no reads"}
    swam = next((i for i, r in enumerate(trace) if (r.get("swim") or {}).get("class") not in (None, "None")), None)
    fired = next((i for i, r in enumerate(trace) if (r.get("severity") or 0) > 0), None)
    det = {"reads": len(trace), "firstSwimRead": swam, "firstDrowningRead": fired,
           "lastTick": trace[-1].get("tick"), "lastSeverity": trace[-1].get("severity")}
    if fired is None:
        return "FAIL", dict(det, why="RM_PitDrowning never appeared on the Jawa in the pool")
    r = trace[fired]
    det.update(tickAtFire=r.get("tick"), drownAtFire=r.get("drown"), swimAtFire=r.get("swim"))
    if swam is None or swam > fired:
        return "FAIL", dict(det, why="drowning came before (or without) any swimming read")
    if (r.get("drown") or {}).get("headUp") != "False":
        return "FAIL", dict(det, why="drowning fired while ProofDrown said headUp")
    return "PASS", det


# ============================================================================ live
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--cell", default="120,120")
    ap.add_argument("--kind", default="RUT_Jawa_Colonist")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--max-ticks", type=int, default=6000)
    a = ap.parse_args()
    import proof_hose as PH           # noqa: E402  (bridge-side imports only on a live run)
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "jawa_shallows_proof_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    x, z = (int(v) for v in a.cell.split(","))
    rows = []
    res = {"script": "jawa_shallows_proof.py", "item": "JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS",
           "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "cell": [x, z], "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "cell": [x, z], "detail": det})
        print("%-30s %-10s %s" % (rid, st, json.dumps(det, default=str)[:300]), flush=True)
        save()

    def static(typ, meth):
        r = B.call("jawa/static_call", type=typ, method=meth, args="%d,%d" % (x, z)) or {}
        txt = str(r.get("result") or r.get("message") or r.get("error") or "")
        return (parse(txt) if r.get("success") is True else {}), txt

    def terrain_at():
        ops = str(B.call("jawa/get_terrain_batch", rects="%d,%d,1,1" % (x, z)).get("ops") or "")
        for run in ops.split(";"):
            if ":" in run:
                return run.rsplit(":", 1)[0]
        return None

    def severity(pid):
        for h in (B.call("jawa/pawn_get", pawn=pid).get("pawns") or [{}])[0].get("hediffs") or []:
            if h.get("def") == "RM_PitDrowning":
                try:
                    return float(h.get("severity") or 0)
                except (TypeError, ValueError):
                    return 0.0
        return 0.0

    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("JS0_site_ready", "UNMEASURED", {"why": "game not Playing"})
        print("VERDICT: UNMEASURED (game not Playing)", flush=True)
        return 2
    res["site_calm"] = V.site_calm(B)
    site = (x - 5, z - 5, 11, 11)
    try:
        V.prepare_site(B, site, rows, "JS0_site_ready")
    except Exception as e:            # noqa: BLE001  a failed prep is recorded, the paint below still runs
        res["prepare_site_error"] = repr(e)[:300]
    B.call("jawa/set_terrain", x=site[0], z=site[1], terrainDef="Soil", width=11, height=11)
    B.call("jawa/set_terrain", x=x - 2, z=z - 2, terrainDef=BRINE, width=5, height=5)
    r = B.call("jawa/spawn_pawn", kindDef=a.kind, x=x, z=z, faction="player", count=1) or {}
    pid = ((r.get("pawns") or [{}])[0]).get("id")
    res["spawn"] = {k: r.get(k) for k in ("success", "error", "message")}
    if not pid:
        row("JS0_site_ready", "UNMEASURED", {"why": "Jawa spawn refused", "spawn": res["spawn"]})
        print("VERDICT: UNMEASURED (Jawa spawn refused)", flush=True)
        return 2
    B.call("jawa/order_pawn", pawnId=pid, x=x, z=z, draft=True, waitTicks=0, unpause=False)
    res["pawn"] = pid

    st, det = terrain_verdict(terrain_at())
    row("JS1_cell_is_shallow_brine", st, det)
    drown, dtxt = static(FILL_TYPE, "ProofDrown")
    swim, stxt = static(SWIM_TYPE, "ProofSwim")
    res["first_read"] = {"drown": dtxt, "swim": stxt}
    st, det = height_verdict(drown)
    row("JS2_jawa_is_rat_sized", st, dict(det, txt=dtxt))
    st, det = over_head_verdict(drown)
    row("JS3_shallows_over_its_head", st, dict(det, txt=dtxt, swim=stxt))

    trace = [{"tick": 0, "severity": severity(pid), "drown": drown, "swim": swim}]
    played, stop = 0, None
    while played < a.max_ticks and trace[-1]["severity"] <= 0:
        try:
            B.ticks(CHUNK)
        except Exception as e:        # noqa: BLE001  the governor stops on a downed colonist: that IS the event we wait for
            stop = repr(e)[:300]
        played += CHUNK
        d, _ = static(FILL_TYPE, "ProofDrown")
        s, _ = static(SWIM_TYPE, "ProofSwim")
        trace.append({"tick": played, "severity": severity(pid), "drown": d, "swim": s})
        if stop:
            break
    res["trace"] = trace
    res["governor_stop"] = stop
    st, det = drowning_verdict(trace)
    row("JS4_drowning_fires_there", st, dict(det, governorStop=stop))
    B.call("jawa/pawn_health", pawn=pid, action="remove", hediff="RM_PitDrowning")
    save()
    print("VERIFY cell=%d,%d %s" % (x, z, " ".join("%s=%s" % (r["id"], r["status"]) for r in rows
                                                     if r["id"].startswith("JS"))), flush=True)
    return exit_code(rows)


def exit_code(rows):
    """The live round's contract: 0 PASS, 1 FAIL, 2 UNMEASURED. FAIL only when a measured JS1-JS4 row says FAIL; a
    missing or UNMEASURED row means the proof did not see, never that the mod is wrong (2026-11-04 run: a bridge-client
    refusal traceback exited 1 and was recorded as a mod FAIL)."""
    rows = [r for r in rows if r["id"].startswith(("JS1_", "JS2_", "JS3_", "JS4_"))]
    if any(r["status"] == "FAIL" for r in rows):
        print("VERDICT: FAIL", flush=True)
        return 1
    if len(rows) == 4 and all(r["status"] == "PASS" for r in rows):
        print("VERDICT: PASS", flush=True)
        return 0
    print("VERDICT: UNMEASURED (%d of 4 rows measured)" % sum(r["status"] in ("PASS", "FAIL") for r in rows), flush=True)
    return 2


def guarded(fn):
    """Run the live proof; an uncaught harness/bridge error is UNMEASURED (exit 2) with its reason, never a FAIL."""
    try:
        return fn()
    except SystemExit:
        raise
    except Exception as e:            # noqa: BLE001  any bridge/harness fault: the proof did not see
        import traceback
        traceback.print_exc()
        print("VERDICT: UNMEASURED (harness: %s: %s)" % (type(e).__name__, str(e).splitlines()[0][:200] if str(e) else ""),
              flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(guarded(main))
