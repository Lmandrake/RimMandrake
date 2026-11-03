#!/usr/bin/env python3
"""LEANINGSCRUB_STALL_SHARED_MOVE_1: rerun the item's OWN repro live and name the job behind the Stall's shared move.

On 2026-10-07 (101652Z, 104321Z) both stall animals -- RM_Thornhold 0.4 at (x-3,z) and RM_Shirrel 0.7 at (x+3,z), faction
none, pad anchor = map centre -45,-45, RM_Stall locked -- moved the same +12,+12 in the first 250 ticks, then held. The
job was never sampled and those run files are gone. The 2026-10-16 reruns (validation.py stall_chain) did NOT follow
the repro: they drafted the site colonists first (_settle_bystanders), removed wildlife (_clear_wildlife) and sampled
every 125 ticks, so a clean result there names nothing.

This script follows the item's repro: no bystander settling, no wildlife removal, job (jawa/site_state) + x/z
(jawa/list_pawns) every 25 ticks for 300 ticks. It records the site context the suspects read (every humanlike's
position, drafted state, the map biome) and then runs a second arm with leanScentEnabled OFF at the same cells,
because BOTH suspects answer the same job def (JobDefOf.Flee): vanilla JobGiver_AnimalFlee (an AlwaysFlee thing within
18) and RM_TheLeanPatches.AnimalFlee_Postfix (lean scent, 24 cells off a humanlike upwind; it ignores drafting).
  exit 0  a move (>= MOVE cells in 300 ticks) reproduced in the scent-ON arm and the job(s) sampled during it are
          named (printed, and written to --out); the attribution line says which suspect the OFF arm points at;
  exit 1  no move reproduced, or a move with only wander-family jobs: the job is NOT named (never a pass);
  exit 2  the site could not be staged or read (UNMEASURED).
Usage: repro_stall_move.py [--out <json>]   (live; run with python.exe on archmagi)   |   repro_stall_move.py --selftest
"""
import json
import os
import sys

SMALL, BIG = "RM_Thornhold", "RM_Shirrel"
WANDER = {None, "", "GotoWander", "Wait_Wander", "Wait_MaintainPosture", "Wait"}
MOVE = 6.0              # cells in 300 ticks; the 10-07 move was ~17 (12,12 diagonal), a frozen Thornhold moves 0
STEP, STEPS = 25, 12    # the item's repro: every 25 ticks for 300 ticks
PAD = (-45, -45)
SHARE_TOL = 4.0         # cells between the two animals' net moves for a move to count as SHARED
SETTINGS = "RimMandrake.LeaningScrub.RM_LeaningScrubSettings"


def _dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def summarise(track):
    """track: [{"tick", "x", "z", "job"}...] for one pawn -> path, net vector, and the jobs seen on moving steps."""
    pts = [s for s in track if s.get("x") is not None and s["x"] >= 0]    # list_pawns reports -1 when unspawned
    path = sum(_dist((a["x"], a["z"]), (b["x"], b["z"])) for a, b in zip(pts, pts[1:]))
    net = (pts[-1]["x"] - pts[0]["x"], pts[-1]["z"] - pts[0]["z"]) if len(pts) > 1 else (0, 0)
    during = []
    for a, b in zip(pts, pts[1:]):
        if (a["x"], a["z"]) != (b["x"], b["z"]):
            for j in (a.get("job"), b.get("job")):
                if j not in during:
                    during.append(j)
    named = [j for j in during if j not in WANDER]
    return {"path": round(path, 1), "net": net, "jobsDuringMove": during, "named": named, "samples": len(track)}


def verdict(on, off):
    """on/off: {SMALL: summary, BIG: summary} (off may be None). -> (exit code, lines)."""
    lines = []
    moved = [n for n in (SMALL, BIG) if on.get(n) and on[n]["path"] >= MOVE]
    for n in (SMALL, BIG):
        s = on.get(n)
        if not s:
            return 2, ["UNMEASURED: no samples for %s in the scent-ON arm" % n]
        lines.append("ON  %s path %.1f net %s jobs-during-move %s" % (n, s["path"], s["net"], s["jobsDuringMove"]))
    if not moved:
        return 1, lines + ["NOT REPRODUCED: neither animal moved >= %.0f cells in 300 ticks; the job is not named" % MOVE]
    # The item is a SHARED move: both animals, the same vector (10-07: +12,+12 each). One animal walking alone is some
    # other mechanism (LIVE 2026-11-02: the Thornhold's RM_CompHomeTether den Goto) and names nothing about the item.
    if len(moved) < 2:
        return 1, lines + ["NOT SHARED: only %s moved >= %.0f cells; the item's move was both animals together, "
                           "so the job is not named" % (moved, MOVE)]
    a, b = on[SMALL]["net"], on[BIG]["net"]
    if _dist(a, b) > SHARE_TOL:
        return 1, lines + ["NOT SHARED: the two net moves %s and %s differ by more than %.0f cells; the job is not "
                           "named" % (a, b, SHARE_TOL)]
    named = sorted(set(j for n in moved for j in on[n]["named"]))
    if not named:
        return 1, lines + ["MOVE WITHOUT A NAME: %s moved but every job sampled on a moving step was wander-family %s"
                           % (moved, sorted(set(str(j) for n in moved for j in on[n]["jobsDuringMove"])))]
    lines.append("NAMED: the job during the move was %s (%s)" % (", ".join(named), ", ".join(moved)))
    if off is None:
        lines.append("ATTRIBUTION UNMEASURED: the leanScentEnabled-OFF arm did not run")
        return 0, lines
    for n in (SMALL, BIG):
        s = off.get(n) or {}
        lines.append("OFF %s path %s jobs-during-move %s" % (n, s.get("path"), s.get("jobsDuringMove")))
    off_named = set(j for n in moved for j in (off.get(n) or {}).get("named", []))
    if "Flee" not in named:
        # both suspects answer JobDefOf.Flee; a move under any other job is neither of them
        lines.append("ATTRIBUTION: the job is not Flee -> neither suspect (vanilla JobGiver_AnimalFlee nor the lean "
                     "scent); a third job giver made the move")
    elif "Flee" not in off_named:
        lines.append("ATTRIBUTION: gone with leanScentEnabled OFF -> RM_TheLeanPatches.AnimalFlee_Postfix (lean scent)")
    else:
        lines.append("ATTRIBUTION: persists with leanScentEnabled OFF -> vanilla JobGiver_AnimalFlee (AlwaysFlee/threat), "
                     "not the lean scent")
    return 0, lines


# ------------------------------------------------------------------------------------------------------------- live
def live(out_path):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Utils"))
    import rimbridge_client as rb  # noqa: E402

    h, p, tok = rb.resolve_endpoint()
    S = rb.RimBridge(host=h, port=p, token=tok, timeout=120.0)
    try:
        S.connect()
    except rb.RimBridgeError as e:
        # LIVE 2026-11-03 gen19: a down game read as a Python traceback, exit 1 = "not reproduced"; it measured nothing
        print("UNMEASURED: bridge unreachable: %s" % str(e)[:200])
        return 2

    def call(tool, **kw):
        try:
            return S.call(tool, kw) or {}
        except rb.RimBridgeError as e:
            return {"success": False, "error": str(e)}

    def ticks():
        return (call("rimworld/get_game_info") or {}).get("ticksGame")

    mi = call("jawa/map_info")
    if not mi.get("sizeX"):
        print("UNMEASURED: no current map: %s" % str(mi)[:200])
        return 2
    if not mi.get("mapBiome") or mi.get("mapBiome") == "RM_LeaningScrub":
        # checked BEFORE the pad is touched: the 10-07 move was on a NON-Scrub quicktest map (validation.py@f9647fd94a).
        # LIVE 2026-11-02 21:51Z ran on RM_LeaningScrub, exited 1 "not shared", and was logged game_fail although the
        # wrong site measured nothing (consult 2026-11-03; --record's own map guard never ran behind the &&)
        print("UNMEASURED: map biome %r; the item's repro needs a NON-Scrub quicktest map" % mi.get("mapBiome"))
        return 2
    x, z = mi["sizeX"] // 2 + PAD[0], mi["sizeZ"] // 2 + PAD[1]
    call("jawa/set_game_speed", speed=0)
    rec = {"map": {k: mi.get(k) for k in ("sizeX", "sizeZ", "mapBiome", "tile")}, "anchor": [x, z], "arms": {}}
    # the pad as validation._prep lays it, MINUS _settle_bystanders and _clear_wildlife (the 10-07 shape)
    rect = "%d,%d,%d,%d" % (x - 16, z - 16, 32, 32)
    call("jawa/destroy_batch", rects=rect, categories="All")
    call("jawa/set_roof_batch", ops="None:%s" % rect)
    call("jawa/set_terrain_batch", ops="Soil:%s" % rect, layer="top")
    call("jawa/weather_set", weather="RM_Stall", lockWeather=True)
    cur = (call("jawa/weather_get") or {}).get("weather")
    cur = cur.get("current") if isinstance(cur, dict) else cur
    rec["weather"] = cur
    if cur != "RM_Stall":
        print("UNMEASURED: RM_Stall did not lock (read back %r)" % cur)
        call("jawa/weather_set", unlock=True)
        return 2

    def arm(name, scent):
        r = call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="leanScentEnabled", value=str(scent))
        got = call("jawa/mod_settings_field", typeName=SETTINGS, action="get", field="leanScentEnabled").get("value")
        if str(got).strip().lower() != str(scent).lower():
            print("UNMEASURED: leanScentEnabled=%s did not take (%r, read %r)" % (scent, r, got))
            return None
        ids = {}
        for kind, dx in ((SMALL, -3), (BIG, 3)):
            sp = call("jawa/spawn_pawn", kindDef=kind, x=x + dx, z=z, faction="none", count=1)
            pid = (((sp or {}).get("pawns") or [{}])[0]).get("id")
            if not pid:
                print("UNMEASURED: spawn %s failed: %s" % (kind, str(sp)[:200]))
                return None
            ids[kind] = pid
            for need in ("Food", "Rest"):
                call("jawa/pawn_need", pawn=pid, action="need", need=need, level=1.0)
        # every humanlike the scent postfix iterates (AllHumanlikeSpawned); its job says whether it is drafted
        site = dict((q.get("id"), q) for q in (call("jawa/site_state").get("pawns") or []))
        people = [{"id": q.get("id"), "x": q.get("x"), "z": q.get("z"), "faction": q.get("faction"),
                   "job": (site.get(q.get("id")) or {}).get("job")}
                  for q in (call("jawa/list_pawns", limit=500).get("pawns") or []) if q.get("intelligence") == "Humanlike"]
        tracks = dict((k, []) for k in ids)
        t0 = ticks()
        for i in range(STEPS + 1):
            if i:
                call("rimworld/step_game_ticks", ticks=STEP, pauseFirst=True)
            now = ticks()
            rows = dict((q.get("id"), q) for q in (call("jawa/list_pawns", limit=500).get("pawns") or []))
            jobs = dict((q.get("id"), q) for q in (call("jawa/site_state").get("pawns") or []))
            for kind, pid in ids.items():
                row, js = rows.get(pid) or {}, jobs.get(pid) or {}
                # targetA of a Flee job is the cell it runs to; the threat is not on the job, hence the OFF arm
                tracks[kind].append({"tick": now, "x": row.get("x"), "z": row.get("z"), "job": js.get("job"),
                                     "targetA": js.get("targetA")})
        call("jawa/set_game_speed", speed=0)
        for pid in ids.values():
            call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
        rec["arms"][name] = {"scent": scent, "ids": ids, "startTick": t0, "humanlikes": people, "tracks": tracks}
        return dict((k, summarise(v)) for k, v in tracks.items())

    try:
        on = arm("scent_on", True)
        off = arm("scent_off", False) if on else None
    finally:
        call("jawa/mod_settings_field", typeName=SETTINGS, action="set", field="leanScentEnabled", value="True")
        call("jawa/weather_set", weather="Clear", lockWeather=True)
        call("jawa/weather_set", unlock=True)
    if not on:
        return 2
    code, lines = verdict(on, off)
    rec["verdict"] = {"exit": code, "lines": lines}
    for ln in lines:
        print(ln)
    if out_path:
        with open(out_path, "w") as fh:
            json.dump(rec, fh, indent=1)
        print("record: %s" % out_path)
    return code


# ---------------------------------------------------------------------------------------------------------- selftest
def selftest():
    def tr(points, jobs):
        return [{"tick": 25 * i, "x": a, "z": b, "job": j} for i, ((a, b), j) in enumerate(zip(points, jobs))]

    flee_pts = [(77, 80), (81, 84), (85, 88), (89, 92)] + [(89, 92)] * 9
    held_pts = [(83, 80)] * 13
    flee = summarise(tr(flee_pts, [None, "Flee", "Flee", "Flee"] + ["Wait_Wander"] * 9))
    assert flee["path"] > 16 and flee["net"] == (12, 12) and flee["named"] == ["Flee"], flee
    held = summarise(tr(held_pts, ["Wait_Wander"] * 13))
    assert held["path"] == 0 and held["named"] == [], held
    # the 10-07 shape, attributed to the scent when the OFF arm holds still
    code, lines = verdict({SMALL: flee, BIG: flee}, {SMALL: held, BIG: held})
    assert code == 0 and any("NAMED: the job during the move was Flee" in l for l in lines), lines
    assert any("AnimalFlee_Postfix" in l for l in lines), lines
    # same move with scent OFF: vanilla flee
    code, lines = verdict({SMALL: flee, BIG: flee}, {SMALL: flee, BIG: held})
    assert code == 0 and any("vanilla JobGiver_AnimalFlee" in l for l in lines), lines
    # the 10-16 shape: no move -> NOT a pass
    code, lines = verdict({SMALL: held, BIG: held}, None)
    assert code == 1 and "NOT REPRODUCED" in lines[-1], lines
    # a move made only of wander jobs names nothing -> NOT a pass
    wand = summarise(tr(flee_pts, ["GotoWander"] * 13))
    code, lines = verdict({SMALL: held, BIG: wand}, None)
    assert code == 1 and ("MOVE WITHOUT A NAME" in lines[-1] or "NOT SHARED" in lines[-1]), lines
    code, lines = verdict({SMALL: wand, BIG: wand}, None)
    assert code == 1 and "MOVE WITHOUT A NAME" in lines[-1], lines
    # a missing pawn is UNMEASURED
    assert verdict({SMALL: flee}, None)[0] == 2
    # an unspawned sample (x -1) is not a 100-cell jump
    gap = summarise(tr([(77, 80), (-1, -1), (77, 80)], [None, None, None]))
    assert gap["path"] == 0, gap
    # a job seen only while standing still is not "during the move"
    still = summarise(tr(held_pts, ["Flee"] * 13))
    assert still["jobsDuringMove"] == [] and verdict({SMALL: still, BIG: held}, None)[0] == 1
    # LIVE 2026-11-02 run1 shape: the Thornhold alone walks a den Goto, the Shirrel wanders < MOVE -> NOT a pass
    den = summarise(tr([(77, 80), (76, 79), (75, 78), (74, 77), (73, 76), (72, 75), (70, 74), (69, 74), (68, 74),
                        (67, 74), (65, 75)], [None] + ["Goto"] * 10))
    code, lines = verdict({SMALL: den, BIG: held}, {SMALL: den, BIG: held})
    assert code == 1 and "NOT SHARED" in lines[-1], lines
    # both move, but in different directions -> not the item's shared move
    away = summarise(tr([(83, 80), (87, 76), (91, 72), (95, 68)], [None, "Flee", "Flee", "Flee"]))
    code, lines = verdict({SMALL: flee, BIG: away}, None)
    assert code == 1 and "NOT SHARED" in lines[-1], lines
    # a shared move under a non-Flee job is attributed to neither flee suspect
    gflee = summarise(tr(flee_pts, [None, "Goto", "Goto", "Goto"] + ["Wait_Wander"] * 9))
    code, lines = verdict({SMALL: gflee, BIG: gflee}, {SMALL: gflee, BIG: held})
    assert code == 0 and "neither suspect" in lines[-1], lines
    print("selftest ok")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    sys.exit(live(out))
