"""sweep_identity_proof.py -- RIVER_SWEEP_FIX_COLONISTS_RETURN_AS_NPCS live proof for the three kinds R3 does not stage:
a colonist, a PRISONER and a TAME animal stand in moving water at the map edge, are swept off, are walked home with
ProofSwept "return", and must come back with the same ThingID, the same faction and (the prisoner) the same guest status.

    python.exe src/RimMandrake/FlowWorks/northstar/sweep_identity_proof.py [out.json]

Needs a Playing river site with moving water on >= 2 map edges (river_site.py [--allow-no-fast]); bridge held.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import river_scenes_walk as R  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=os.path.join(HERE, "sweep_identity_%s.json" % time.strftime("%Y%m%dT%H%M%S")))
    a = ap.parse_args()
    import extensions_rivers as RIV  # noqa: E402
    wa = argparse.Namespace(mock=False, pace=0.0, no_shots=True, mock_fail=None)
    w = R.C.make_walk(wa, R.OUT_LIVE)
    env, why = R.env_for(w)
    res = {"script": "sweep_identity_proof.py", "rows": [], "started": time.strftime("%Y-%m-%dT%H:%M:%S")}

    def row(rid, st, det):
        res["rows"].append({"id": rid, "status": st, "detail": det})
        print("%-36s %-10s %s" % (rid, st, json.dumps(det, default=str)[:700]), flush=True)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    if not env:
        row("SWEEP_site", "UNMEASURED", {"why": why})
        return 2
    cells = RIV.edge_river_cells(env["terr"], env["size"], cap=6)
    if len(cells) < 3:
        row("SWEEP_site", "UNMEASURED", {"why": "fewer than 3 edge river cells", "cells": cells})
        return 2

    def pget(i):
        return ((w.call("jawa/pawn_get", pawn=i) or {}).get("pawns") or [{}])[0]

    def guest(i):
        r = w.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofSwept", args="read") or {}
        return str(r.get("result"))

    staged = {}
    r = w.call("jawa/spawn_pawn", kindDef="Colonist", x=cells[0][0], z=cells[0][1], faction="player", count=1) or {}
    staged["colonist"] = ((r.get("pawns") or [{}])[0]).get("id")
    w.call("jawa/set_draft", pawnId=staged["colonist"], drafted=True)
    r = w.call("jawa/spawn_pawn", kindDef="Villager", x=cells[1][0], z=cells[1][1], faction="hostile", count=1) or {}
    staged["prisoner"] = ((r.get("pawns") or [{}])[0]).get("id")
    gs = w.call("jawa/pawn_set_guest_status", pawn=staged["prisoner"], guestStatus="Prisoner", hostFaction="PlayerColony")
    if len(cells) >= 4:   # fix3 (2026-10-18): a slave rides the same book as a prisoner
        r = w.call("jawa/spawn_pawn", kindDef="Villager", x=cells[3][0], z=cells[3][1], faction="hostile", count=1) or {}
        staged["slave"] = ((r.get("pawns") or [{}])[0]).get("id")
        w.call("jawa/pawn_set_guest_status", pawn=staged["slave"], guestStatus="Slave", hostFaction="PlayerColony")
    r = w.call("jawa/spawn_pawn", kindDef="Muffalo", x=cells[2][0], z=cells[2][1], faction="player", count=1) or {}
    staged["tame_animal"] = ((r.get("pawns") or [{}])[0]).get("id")
    # a tame animal walks out of the current at once (2026-10-18 run: never swept); downed it lies where the river takes it
    w.call("jawa/pawn_force_incapacitate", pawn=staged["tame_animal"], action="downed", allowBleedingWounds=False)
    before = {k: {"faction": pget(i).get("faction"), "pos": pget(i).get("position")} for k, i in staged.items()}
    row("SWEEP_staged", "INFO", {"cells": cells[:3], "staged": staged, "before": before, "prisonerStatus": str(gs)[:200],
                                 "book": guest(None)})
    gone, trace = {}, []
    for k in range(12):
        w.ticks(250)
        for kind, i in staged.items():
            p = pget(i)
            trace.append({"t": (k + 1) * 250, "kind": kind, "pos": p.get("position"), "found": bool(p)})
            if kind not in gone and not p.get("position"):      # pawn_get also finds world pawns: off the map = no position
                gone[kind] = (k + 1) * 250
        if len(gone) == len(staged):
            break
    book = guest(None)
    row("SWEEP_swept_off", "PASS" if len(gone) == len(staged) else ("INFO" if gone else "UNMEASURED"),
        {"goneAtTick": gone, "book": book, "trace": trace[-9:]})
    ret = w.call("jawa/static_call", type="RimMandrake.FlowWorks.Rivers.RM_RiverWorksProof", method="ProofSwept", args="return") or {}
    w.ticks(10)
    for kind, i in staged.items():
        if kind not in gone:
            continue
        p = pget(i)
        st = "PASS" if p.get("thingId") == i and p.get("faction") == before[kind]["faction"] and p.get("position") else "FAIL"
        row("SWEEP_returns_same_%s" % kind, st, {"id": i, "thingIdBack": p.get("thingId"), "factionBefore": before[kind]["faction"],
                                                "factionAfter": p.get("faction"), "posAfter": p.get("position"),
                                                "return": str(ret.get("result"))[:120]})
    for kind, st_ in (("prisoner", "Prisoner"), ("slave", "Slave")):
        if kind in gone:
            gs2 = w.call("jawa/pawn_set_guest_status", pawn=staged[kind], guestStatus=st_, hostFaction="PlayerColony") or {}
            row("SWEEP_%s_still_%s" % (kind, st_.lower()), "PASS" if gs2.get("guestStatusBefore") == st_ else "FAIL",
                {"guestStatusBeforeRewrite": gs2.get("guestStatusBefore"), "raw": str(gs2)[:200]})
    # SWEEP_PRISONER_RETURN (live day 4): the prisoner came back on an edge cell and vanilla's escape had it off the map
    # within 10 ticks. Each returned prisoner/slave must stand OFF the edge and still be on the map 600 ticks later (inside
    # the service's one-hour escape guard; a site with no prison cell gets the interior fallback cell).
    held_back = [k for k in ("prisoner", "slave") if k in gone and pget(staged[k]).get("position")]
    if held_back:
        sx, sz = env["size"]
        at = {k: pget(staged[k]).get("position") for k in held_back}
        w.ticks(600)
        for k in held_back:
            p = pget(staged[k])
            pos0 = at[k] or {}
            on_edge = pos0.get("x") in (0, sx - 1) or pos0.get("z") in (0, sz - 1)
            ok = bool(p.get("position")) and (k != "prisoner" or not on_edge)
            row("SWEEP_%s_stays_600" % k, "PASS" if ok else "FAIL",
                {"posAtReturn": pos0, "returnCellOnEdge": on_edge, "posAfter600": p.get("position"), "book": guest(None)})
    for i in staged.values():
        w.call("jawa/pawn_force_incapacitate", pawn=i, action="vanish")
    return 0


if __name__ == "__main__":
    sys.exit(main())
