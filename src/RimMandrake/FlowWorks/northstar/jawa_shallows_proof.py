"""JAWA IN THE SHALLOWS live proof (JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS).

  python.exe src/RimMandrake/FlowWorks/northstar/jawa_shallows_proof.py [out.json] [--cell X,Z] [--kind RUT_Jawa_Colonist]
                                                                       [--fresh-map] [--max-ticks 6000]

Run from the repo root with python.exe; the bridge must be held. Exit 0 = every row PASS. Read-only to the ledger.

What it settles. 2026-10-21 (JAWA_DROWNING_PROVE_RAT_SIZED_IN_SHALLOWS): Captain's eight RM_PitDrowning downs on the GSS
theft run were natural brine, not a pit: RM_Drowning.HeightOf gave a Jawa the small climb band's 0.5 m (BodySize under the
0.75 band edge), so a vanilla-passable 0.5 m shallow pool was over its head standing (0.45 m); RM_Swim made it swim until
RM_SwimExhaustion reached 1, then it drowned. 2026-11-25 (RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR, the same
cause seen on the pawn-in-liquid grid): a humanlike's height now follows its body size (1.75 m x sqrt(size): a Jawa is
1.24 m), so this proof now holds the FIXED behaviour: the shallows are wading water to a Jawa, and it does not drown there.

Scene: a 5x5 RM_WaterBrineShallow pool (the RM_Stillsand pool terrain, isSourceCell) painted at --cell (default 120,120) on
soil, inside a cleared 11x11 site; one Jawa colonist spawned at the pool's centre and drafted there (two brine squares to any
shore, so no exit in reach). Reads are jawa/static_call RM_PitFillEffects.ProofDrown and RM_Swim.ProofSwim at that cell.

Rows (MEASURED, all on the record with the cell coordinates):
  JS1_cell_is_shallow_brine      the pawn's cell reads RM_WaterBrineShallow
  JS2_jawa_is_not_rat_sized      ProofDrown H >= 1.0 m for the Jawa (the rat's band was 0.50)
  JS3_shallows_under_its_head    ProofDrown water <= 0.9 H and under=False standing: the shallows are wading water
  JS4_no_drowning_there          for --max-ticks, RM_PitDrowning never appears on the Jawa in that cell, and RM_Swim never
                                 reads it swimming
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
JAWA_MIN_H = 1.0               # a Jawa's height floor (HumanlikeHeightMetres(0.5) = 1.24 m; the rat's band was 0.5 m)
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
    return ("PASS" if h >= JAWA_MIN_H else "FAIL"), {"H": h, "want_at_least": JAWA_MIN_H}


def under_head_verdict(drown):
    """Standing (lying=False) in water at or under 0.9 H, and the mod agrees (under=False)."""
    h, w = _f(drown, "H"), _f(drown, "water")
    if h is None or w is None:
        return "UNMEASURED", {"why": "no DROWN line", "drown": drown}
    det = {"water": w, "H": h, "headUnderAt": round(h * HEAD_FRACTION, 4), "lying": drown.get("lying"),
           "under": drown.get("under")}
    if drown.get("lying") != "False":
        return "UNMEASURED", dict(det, why="the Jawa was not standing at the first read (the standing threshold is the claim)")
    if not w > 0:
        return "UNMEASURED", dict(det, why="no water read at the cell (the claim is about 0.5 m shallows)")
    ok = w <= h * HEAD_FRACTION + 1e-4 and drown.get("under") == "False"
    return ("PASS" if ok else "FAIL"), det


def no_drowning_verdict(trace, max_ticks):
    """trace: [{tick, severity, drown{}, swim{}}] in order, severity = RM_PitDrowning on the Jawa (0 when absent).
    PASS: the reads cover max_ticks, RM_PitDrowning never appears, and no read has the Jawa swimming (class != None)."""
    if not trace:
        return "UNMEASURED", {"why": "no reads"}
    swam = next((i for i, r in enumerate(trace) if (r.get("swim") or {}).get("class") not in (None, "None")), None)
    fired = next((i for i, r in enumerate(trace) if (r.get("severity") or 0) > 0), None)
    det = {"reads": len(trace), "firstSwimRead": swam, "firstDrowningRead": fired,
           "lastTick": trace[-1].get("tick"), "lastSeverity": trace[-1].get("severity")}
    if fired is not None:
        r = trace[fired]
        return "FAIL", dict(det, why="RM_PitDrowning appeared on the Jawa in 0.5 m shallows", tickAtFire=r.get("tick"),
                            drownAtFire=r.get("drown"), swimAtFire=r.get("swim"))
    if swam is not None:
        return "FAIL", dict(det, why="RM_Swim read the Jawa swimming in 0.5 m shallows", swimAt=trace[swam].get("swim"))
    if (trace[-1].get("tick") or 0) < max_ticks:
        return "UNMEASURED", dict(det, why="the reads stopped before --max-ticks (%d)" % max_ticks)
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
    res = {"script": "jawa_shallows_proof.py", "item": "RIMMANDRAKE_CLASS_DROID_AND_JAWA_GONE_IN_SHALLOW_TAR",
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
    row("JS2_jawa_is_not_rat_sized", st, dict(det, txt=dtxt))
    st, det = under_head_verdict(drown)
    row("JS3_shallows_under_its_head", st, dict(det, txt=dtxt, swim=stxt))

    trace = [{"tick": 0, "severity": severity(pid), "drown": drown, "swim": swim}]
    played, stop = 0, None
    while played < a.max_ticks and trace[-1]["severity"] <= 0:
        try:
            B.ticks(CHUNK)
        except Exception as e:        # noqa: BLE001  the governor stops on a downed colonist: a down here is the fault this proof refuses
            stop = repr(e)[:300]
        played += CHUNK
        d, _ = static(FILL_TYPE, "ProofDrown")
        s, _ = static(SWIM_TYPE, "ProofSwim")
        trace.append({"tick": played, "severity": severity(pid), "drown": d, "swim": s})
        if stop:
            break
    res["trace"] = trace
    res["governor_stop"] = stop
    st, det = no_drowning_verdict(trace, a.max_ticks)
    row("JS4_no_drowning_there", st, dict(det, governorStop=stop))
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
