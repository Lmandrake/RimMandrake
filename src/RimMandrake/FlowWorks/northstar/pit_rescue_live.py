"""PIT RESCUE live check (PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS A4: "a colonist downed in a sheer pit nobody can reach gets
a ladder job queued at the nearest wall (portable if spare/shallow, else fixed), it is built and the colonist rescued";
BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/pit_rescue_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene (plot from --origin, default 30,30; 16 x 12 cleared + read back): a sheer pit x = 6..8, z = 4..6 dug D 4 (2 m: nobody
without gear climbs it, climb_proof); a colonist DOWNED on its floor (7, 5) (pawn_force_incapacitate, no bleeding); every
other colonist on the map vanished, then two fresh rescuers on the rim (2, 5), (2, 6), undrafted; a wooden bed at (12, 9)
(a rescue needs a bed); 100 steel + 100 wood at (3, 9) for the ladder.
Rows:
  RESCUE_LADDER_QUEUED   EXPECT within 500 ticks (RM_MapComponent_PitRescueLadder checks every 250) a ladder blueprint,
                         frame or ladder stands on a pit square.
  RESCUE_LADDER_BUILT    EXPECT within --ticks a built RM_LadderPortable / RM_Ladder in the pit.
  RESCUE_COLONIST_OUT    EXPECT within --ticks the downed colonist is off the pit floor (carried out; in the bed or on
                         the way). LIES: a colonist who died is not rescued (dead is read); the plain stepper is used
                         (the governed clock stops on a downed colonist by design).
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
ITEM = "PIT_ACCESS_BUILD_LADDERS_CLIMBING_JUMPS"
LADDERS = ("RM_LadderPortable", "RM_Ladder")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="30,30")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=8000)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "pit_rescue_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "pit_rescue_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    IDS = ("RESCUE_LADDER_QUEUED", "RESCUE_LADDER_BUILT", "RESCUE_COLONIST_OUT")

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-24s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def all_rows(st, cls, det):
        for rid in IDS:
            if rid not in [r["id"] for r in rows]:
                row(rid, st, cls, det)

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        all_rows("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 16, 12)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "rescue_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        all_rows("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    pit = {P(x, z) for x in range(6, 9) for z in range(4, 7)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead") and p.get("isPlayer"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    B.call("jawa/build_batch", ops="Bed:%d,%d" % P(12, 9), faction="player", wipeExisting=False, stuff="WoodLog")
    for d, c in (("Steel", P(3, 9)), ("WoodLog", P(4, 9))):
        B.call("rimworld/spawn_thing", defName=d, stackCount=100, x=c[0], z=c[1])

    def spawn(c):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
        return ((r.get("pawns") or [{}])[0]).get("id")
    victim = spawn(P(7, 5))
    rescuers = [spawn(P(2, 5)), spawn(P(2, 6))]
    inc = B.call("jawa/pawn_force_incapacitate", pawn=victim, action="downed", allowBleedingWounds=False) or {}
    # can-fail control (belt run 3: nobody rescued even after the ladder stood): a colonist downed on OPEN ground; if he is
    # not rescued either, the scene cannot rescue at all (SITE), whatever the pit does
    control = spawn(P(13, 3))
    B.call("jawa/pawn_force_incapacitate", pawn=control, action="downed", allowBleedingWounds=False)
    res["control"] = control
    B.call("jawa/build_batch", ops="Bed:%d,%d" % P(14, 9), faction="player", wipeExisting=False, stuff="WoodLog")
    res["scene"] = {"victim": victim, "rescuers": rescuers, "incap": str(inc)[:200]}

    def ladder_in_pit():
        hits = []
        lt = B.call("jawa/list_things", rect="%d,%d,3,3" % P(6, 4), limit=60) or {}
        for t in lt.get("things") or []:
            d = str(t.get("def") or t.get("defName") or "")
            if any(l in d for l in LADDERS) or "Blueprint" in d or "Frame" in d:
                hits.append((d, t.get("x"), t.get("z")))
        return hits

    def victim_state(who=None):
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400, includeCorpses=True) or {}).get("pawns") or []}
        p = ps.get(who or victim) or {}
        return (p.get("x"), p.get("z")), p.get("downed"), p.get("dead"), p.get("spawned")
    control_moved = None

    t, queued_at, built_at, out_at = 0, None, None, None
    trail = []
    while t < a.ticks:
        step(250)
        t += 250
        lad = ladder_in_pit()
        pos, downed, dead, spawned = victim_state()
        cpos = victim_state(control)
        if control_moved is None and (cpos[0] != P(13, 3) or cpos[3] is False):
            control_moved = t
        jobs = []
        for r_ in rescuers:
            pr = B.call("jawa/attack_target_probe", pawn=r_, maxDist=60, _answer=True) or {}
            jobs.append([r_, pr.get("position"), pr.get("curJob")])
        trail.append({"t": t, "ladder": lad, "victim": [pos, downed, dead, spawned], "rescuers": jobs})
        if lad and queued_at is None:
            queued_at = t
        if built_at is None and any(d in LADDERS for d, _x, _z in lad):
            built_at = t
        if out_at is None and (pos not in pit and pos[0] is not None or spawned is False) and not dead:
            out_at = t
        if dead:
            break
        if out_at is not None:
            break
        # belt live 2026-10-22: idle rescuers hauled the wood into the frame and then never took FinishFrame (8000 ticks,
        # 'Work left' untouched) while an ORDERED FinishFrame completed it. After 2000 stalled ticks the frame is finished
        # by order (recorded as an assist) so the rescue half can still be measured; RESCUE_LADDER_BUILT stays FAIL.
        frames = [x for x in lad if x[0].startswith("Frame_")]
        if frames and built_at is None and t >= 2000 and not res.get("assist"):
            fid = (B.call("jawa/list_things", defName=frames[0][0], rect="%d,%d,1,1" % (frames[0][1], frames[0][2]), limit=1)
                   or {}).get("things") or [{}]
            o = B.call("jawa/ordered_job", pawnId=rescuers[0], jobDef="FinishFrame", targetAId=fid[0].get("id")) or {}
            res["assist"] = {"t": t, "frame": fid[0].get("id"), "order": {k: o.get(k) for k in ("accepted", "afterJobDef")}}
        if t % 1000 == 0:
            save()
    res["trail"] = trail
    det = {"queuedAt": queued_at, "builtAt": built_at, "outAt": out_at, "last": trail[-1] if trail else None}
    row("RESCUE_LADDER_QUEUED", "PASS" if queued_at is not None and queued_at <= 500 else "FAIL", "MOD", det)
    det["assist"] = res.get("assist")
    row("RESCUE_LADDER_BUILT", "PASS" if built_at is not None and not res.get("assist") else "FAIL", "MOD", det)
    dead = trail and trail[-1]["victim"][2]
    det["controlRescuedAt"] = control_moved
    no_rescue_here = control_moved is None
    row("RESCUE_COLONIST_OUT", "UNMEASURED" if (dead or (no_rescue_here and out_at is None)) else ("PASS" if out_at is not None else "FAIL"),
        "SITE" if (dead or no_rescue_here) else "MOD", det)
    for pid in [victim, control] + rescuers:
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
