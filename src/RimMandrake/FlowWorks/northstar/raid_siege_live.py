"""RAID SIEGE live check (RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP A5: "a siege against the same base only builds and shells; no
ladder, fill or jump job"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/raid_siege_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene: raid_trench_proof's island (9x9 at the plot centre, ringed by a sheer trench 2 wide, D 4 = 2 m) with 3 drafted
colonists; 5 Mercenary_Gunner of a hostile Pirate faction 30 squares east, put in a plain LordJob_AssaultColony
(jawa/lord_assault_spawn) and then switched to LordJob_Siege (jawa/lord_set_job; siegeSpot 22 east of the centre).
Rows:
  RAID_SIEGE_DECIDES_SIEGE    PROVE RM_RaiderTrench.ProofDecision for every siege pawn. EXPECT "siege" (the trench giver
                              refuses sieges in code). LIES: a lord switch that did not take reads AssaultColony decisions.
  RAID_SIEGE_NO_TRENCH_JOBS   PROVE each raider's curJob every 250 ticks for --ticks (default 3000). EXPECT no
                              RM_RaiderSetLadder / RM_RaiderFillTrench / RM_LayRaidPlank / jump job ever, and no raider ever
                              on a trench square. LIES: a siege that never got going (nobody moved) is recorded with the
                              lord list so the read can be judged.
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
RT = "RimMandrake.FlowWorks.RM_RaiderTrench"
ITEM = "RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP"
TRENCH_JOBS = ("RM_RaiderSetLadder", "RM_RaiderFillTrench", "RM_LayRaidPlank", "RM_RaiderJump", "CastAbilityOnThing", "CastJump")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="125,125", help="island centre")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=3000)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "raid_siege_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "raid_siege_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-28s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:500]), flush=True)
        save()

    def both(st, cls, det):
        for rid in ("RAID_SIEGE_DECIDES_SIEGE", "RAID_SIEGE_NO_TRENCH_JOBS"):
            row(rid, st, cls, det)

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    cx, cz = (int(v) for v in a.origin.split(","))
    cheb = lambda p: max(abs(p[0] - cx), abs(p[1] - cz))  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        both("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (cx - 10, cz - 10, 45, 21)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "siege_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        both("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    ring = [(x, z) for x in range(cx - 6, cx + 7) for z in range(cz - 6, cz + 7) if cheb((x, z)) >= 5]
    for c in ring:
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    cols = []
    for k in range(3):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=cx - 1 + k, z=cz, faction="player", count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            B.call("jawa/set_draft", pawnId=pid, drafted=True)
            cols.append(pid)
    probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=0, z=0, faction="?", count=1, _answer=True) or {}
    fac = next((f["def"] for f in (probe.get("details") or {}).get("available") or []
                if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
    raiders = []
    for k in range(5):
        r = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=cx + 30, z=cz - 2 + k, faction=fac, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            raiders.append(pid)
    if not fac or len(raiders) < 3 or len(cols) < 3:
        both("UNMEASURED", "SITE", {"why": "scene pawns missing", "faction": fac, "raiders": raiders, "colonists": cols})
        return 2
    # HARNESS (first live run): the plain assault lord is the only lord the bridge can spawn, and a pawn thinks the instant
    # it joins it -- one raider took RM_RaiderSetLadder before the switch to LordJob_Siege and kept that job through the
    # siege. The trench rules are switched OFF across the lord swap (restored right after), so every trench job sampled
    # later was given to a SIEGE pawn.
    RTS = "RimMandrake.FlowWorks.RM_RaiderTrenchSettings"
    B.call("jawa/mod_settings_field", typeName=RTS, action="set", field="raiderTrenchEnabled", value="False")
    B.call("jawa/lord_assault_spawn", pawns=",".join(raiders))
    lords = (B.call("jawa/lord_pawn_move", action="list") or {}).get("lords") or []
    li = next((i for i, l in enumerate(lords) if l.get("faction") and fac and str(l.get("job")) == "LordJob_AssaultColony"), None)
    lidx = lords[li].get("index", li) if li is not None else -1
    sj = B.call("jawa/lord_set_job", lordIndex=lidx, lordJob="LordJob_Siege",
                args="faction=%s;siegeSpot=%d,%d;blueprintPoints=300" % (fac, cx + 22, cz)) or {}
    step(2)
    B.call("jawa/mod_settings_field", typeName=RTS, action="set", field="raiderTrenchEnabled", value="True")
    lords2 = (B.call("jawa/lord_pawn_move", action="list") or {}).get("lords") or []
    res["lords"] = {"before": lords, "setJob": str(sj)[:400], "after": lords2}
    dec = {}
    for pid in raiders:
        d = B.call("jawa/static_call", type=RT, method="ProofDecision", args=pid, _answer=True) or {}
        dec[pid] = str(d.get("result") or d.get("message"))[:160]
    siege_lord = any(str(l.get("job")) == "LordJob_Siege" for l in lords2)
    if not siege_lord:
        both("UNMEASURED", "SITE", {"why": "the lord did not become LordJob_Siege", "lords": lords2, "setJob": str(sj)[:300]})
        return 2
    row("RAID_SIEGE_DECIDES_SIEGE", "PASS" if all(v == "siege" for v in dec.values()) else "FAIL", "MOD", {"decisions": dec})
    bad, seen_jobs, moved = [], {}, False
    first = {}
    t = 0
    while t < a.ticks:
        step(250)
        t += 250
        for pid in raiders:
            pr = B.call("jawa/attack_target_probe", pawn=pid, maxDist=60, _answer=True) or {}
            pos = pr.get("position") or {}
            c = (pos.get("x"), pos.get("z"))
            job = pr.get("curJob")
            seen_jobs[job] = seen_jobs.get(job, 0) + 1
            if pid in first and c != first[pid]:
                moved = True
            first.setdefault(pid, c)
            if job in TRENCH_JOBS or (c[0] is not None and cheb(c) in (5, 6)):
                bad.append((t, pid, c, job))
        save()
    det = {"bad": bad[:12], "jobsSeen": seen_jobs, "anyMoved": moved, "ticks": t, "decisions": dec}
    if not moved:
        row("RAID_SIEGE_NO_TRENCH_JOBS", "UNMEASURED", "SITE", dict(det, why="no siege pawn ever moved"))
    else:
        row("RAID_SIEGE_NO_TRENCH_JOBS", "PASS" if not bad else "FAIL", "MOD", det)
    for pid in raiders + cols:
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
