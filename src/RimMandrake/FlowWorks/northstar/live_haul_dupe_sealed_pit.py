#!/usr/bin/env python3
"""Live scene (kind A): a haul out of an open pit is not retargeted at a stack in a sealed pit next door.

RIMMANDRAKE_VETO_DUPLICATE_PICKUP_ACROSS_SEALED_PIT_DROPS_HAUL (live 2026-11-16, ExplosiveKnockback's pit fetch, the hauler's
job log): after picking up a steel stack in a pit with a lowered ladder, vanilla's duplicate pickup
(Toils_Haul.CheckForGetOpportunityDuplicate, a REGION search that never asks Reachability.CanReach) retargeted the haul at a
same-def stack in a second pit 6 cells off whose ladder was raised; the path errored, the stack was dropped, the same haul
repeated all day. The fix: RM_Patch_HaulDupeReach (Superdeep/RM_PitAccess.cs) asks CanReach in the duplicate search.

Contract.
- claim: steel lying in an open pit is carried to the stockpile, and a steel stack in a sealed pit 6 cells away stays where it is.
- entry point: the colonists' own hauling (the scene calls no job; vanilla's haul WorkGiver and Toils_Haul run unaided).
- valid opportunity: two 3x3 pits 4 m deep, 6 cells apart; each has a fixed ladder in its north edge square; pit A's ladder is
  lowered, pit B's raised; by ProofReachPair the hauler can reach A's stack and cannot reach B's (both read before the wait);
  20 steel in each pit; a one-square stockpile outside both; rain does not fill the pits during the scene; and A's stack is
  picked up at least once during the wait (A's square no longer holds all 20).
- success: after the wait, all 20 of A's steel stand in the stockpile, B's 20 still lie on B's square, and no steel lies anywhere
  else in the site.
- failure (MOD FAILURE): A's steel is short of the stockpile (dropped or stuck), or B's stack moved.
- forbidden effects: B's stack touched; a pawn hurt.
- end: rows written to the out file; the rain setting restored; the stockpile deleted.
- red reading: FlowWorks at the parent of the fix (no RM_Patch_HaulDupeReach) must FAIL this scene; that is the planted fault.

Usage (Windows python, a game in Playing or --fresh-map):
  python.exe src/RimMandrake/FlowWorks/northstar/live_haul_dupe_sealed_pit.py <out.json> [--fresh-map] [--origin X,Z]
Exit 0 PASS, 1 FAIL, 2 UNMEASURED (could not look; the reason is in the row).
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))

ST = "RimMandrake.FlowWorks.RimMandrakeFlowWorksSettings"
NP = "RimMandrake.FlowWorks.RM_NorthstarProofs"
PP = "RimMandrake.FlowWorks.RM_PromotionProofs"
WR = "RimMandrake.FlowWorks.RM_WallReach"
DEEP = 8           # notches: 4 m, a sealed pit with its ladder raised (the 2026-11-16 control pit)
STEEL = 20
WAIT = 3000        # ticks; the old fault repeated its haul every ~500 ticks all day (job log 2026-11-16)
CHUNK = 500


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--origin", default="120,120")
    a = ap.parse_args(argv)
    import proof_hose as PH    # noqa: E402  (bridge-side import on a live run only)
    B = PH.PB()
    rows = []
    res = {"script": "live_haul_dupe_sealed_pit.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows}

    def save():
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    def row(rid, st, det):
        rows.append({"id": rid, "status": st, "detail": det})
        print("%-40s %-10s %s" % (rid, st, json.dumps(det, default=str)[:500]), flush=True)
        save()

    def call(tool, **kw):
        return B.call(tool, **kw) or {}

    def static(t, m, arg):
        r = call("jawa/static_call", type=t, method=m, args=arg)
        return str(r.get("result") or r.get("message") or r.get("error") or r)

    def setting(field, value=None):
        if value is None:
            return call("jawa/mod_settings_field", typeName=ST, action="get", field=field).get("value")
        return call("jawa/mod_settings_field", typeName=ST, action="set", field=field, value=str(value)).get("success")

    def steel(box):
        x0, z0, w, h = box
        out = []
        for t in call("jawa/list_things", defName="Steel", limit=200).get("things") or []:
            x, z = t.get("x"), t.get("z")
            if x is not None and x0 <= x < x0 + w and z0 <= z < z0 + h:
                out.append({"x": x, "z": z, "n": t.get("stackCount") or t.get("count") or t.get("stack")})
        return out

    def n_at(st, c):
        return sum(int(s["n"] or 0) for s in st if (s["x"], s["z"]) == c)

    if a.fresh_map:
        call("rimworld/go_to_main_menu")
        call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    import validation_core as V    # noqa: E402
    if not V._wait_playing(B, leave_s=0)[0]:
        row("DUPE_site", "UNMEASURED", {"why": "no game reached Playing"})
        return 2
    call("jawa/kill_hostiles")
    call("jawa/weather_set", weather="Clear", lockWeather=True)
    ox, oz = (int(v) for v in a.origin.split(","))
    box = (ox - 4, oz - 4, 18, 16)
    pa = [(ox + dx, oz + dz) for dx in range(3) for dz in range(3)]
    pb = [(ox + 6 + dx, oz + dz) for dx in range(3) for dz in range(3)]
    sa, sb = (ox + 1, oz + 1), (ox + 7, oz + 1)          # the two stacks, 6 squares apart
    la, lb = (ox + 1, oz + 2), (ox + 7, oz + 2)          # the ladders, north edge squares, hung north to the rim
    pile = (ox + 4, oz + 6)
    rain, zone_label = None, None
    try:
        rain = setting("rainFillsExcavationsEnabled")
        call("jawa/static_call", type=NP, method="ProofResetRect", args="%d;%d;%d;%d" % box)
        call("jawa/set_fog", action="unfog", rect="%d,%d,%d,%d" % box)
        setting("rainFillsExcavationsEnabled", False)
        depths = [call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=DEEP, setBodyWaterM=-1).get("depth")
                  for c in pa + pb]
        if any(d != DEEP for d in depths):
            row("DUPE_site", "UNMEASURED", {"why": "the pits did not dig to 4 m", "depths": depths})
            return 2
        B.ticks(70) if hasattr(B, "ticks") else call("rimworld/step_game_ticks", ticks=70, pauseFirst=True, timeoutMs=60000)
        lad = call("jawa/spawn_batch", ops="RM_Ladder:%d,%d;RM_Ladder:%d,%d" % (la + lb), stuff="WoodLog", rot=0)
        ra, rb = static(PP, "ProofLadder", "%d,%d,lower" % la), static(PP, "ProofLadder", "%d,%d,raise" % lb)
        st = call("jawa/spawn_batch", ops="Steel:%d,%d,%d;Steel:%d,%d,%d" % (sa + (STEEL,) + sb + (STEEL,)))
        z = call("jawa/map_zones", action="createZone", zoneType="stockpile", rect="%d,%d,1,1" % pile)
        zone_label = z.get("created")       # map_zones createZone names the zone it made in 'created'
        if not zone_label:
            row("DUPE_site", "UNMEASURED", {"why": "no stockpile made", "reply": str(z)[:200]})
            return 2
        sp = call("jawa/spawn_pawn", kindDef="Colonist", x=pile[0], z=pile[1] + 2, faction="player", count=1)
        pid = ((sp.get("pawns") or [{}])[0]).get("id")
        if not pid:
            row("DUPE_site", "UNMEASURED", {"why": "no hauler spawned", "reply": str(sp)[:200]})
            return 2
        num = str(pid).lstrip("Human")
        call("jawa/set_work_priority", pawnId=pid, workType="Hauling", priority=1)
        call("rimworld/step_game_ticks", ticks=10, pauseFirst=True, timeoutMs=60000)
        reach_a = static(WR, "ProofReachPair", "%s;%d,%d;touch" % ((num,) + sa))
        reach_b = static(WR, "ProofReachPair", "%s;%d,%d;touch" % ((num,) + sb))
        s0 = steel(box)
        valid = ("canReach=True" in reach_a and "canReach=False" in reach_b and "present=True raised=False" in ra
                 and "present=True raised=True" in rb and n_at(s0, sa) == STEEL and n_at(s0, sb) == STEEL)
        row("DUPE_site", "PASS" if valid else "UNMEASURED",
            {"ladders": lad.get("success"), "ladderA": ra[:160], "ladderB": rb[:160], "steel": st.get("success"),
             "zone": zone_label, "reachA": reach_a[:200], "reachB": reach_b[:200], "steelBefore": s0})
        if not valid:
            return 2
        seen_a_taken = False
        trace = []
        for k in range(WAIT // CHUNK):
            call("rimworld/step_game_ticks", ticks=CHUNK, pauseFirst=True, timeoutMs=180000)
            s = steel(box)
            trace.append({"tick": (k + 1) * CHUNK, "steel": s})
            if n_at(s, sa) < STEEL:
                seen_a_taken = True
        s1 = steel(box)
        at_pile, at_b = n_at(s1, pile), n_at(s1, sb)
        stray = [s for s in s1 if (s["x"], s["z"]) not in (pile, sb)]
        if not seen_a_taken and at_pile == 0:
            row("DUPE_haul_from_open_pit", "UNMEASURED", {"why": "nobody picked up pit A's steel in %d ticks" % WAIT,
                                                          "steelAfter": s1})
            return 2
        ok = at_pile == STEEL and at_b == STEEL and not stray
        row("DUPE_haul_from_open_pit", "PASS" if ok else "FAIL",
            {"atStockpile": at_pile, "atSealedPitB": at_b, "stray": stray, "trace": trace,
             "why": ("all of A's steel reached the stockpile; B's stack untouched" if ok else
                     "A's steel short of the stockpile or B's stack moved: the duplicate pickup crossed into the sealed pit")})
        return 0 if ok else 1
    finally:
        if rain is not None:
            setting("rainFillsExcavationsEnabled", rain)
        if zone_label:
            call("jawa/map_zones", action="deleteZone", zone=zone_label)
        save()


if __name__ == "__main__":
    sys.exit(main())
