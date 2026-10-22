"""TRENCH CAST live check (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT A3, owner Q5 "raiders use canals, never one they could
not climb out of"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/trench_cast_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene (plot from --origin, default 40,110; 50 x 34 cleared + read back by validation_core.prepare_site):
  three drafted colonists at (2..4, 16) -- the colony the raid shoots at;
  a 1 m canal (2 notches, a person climbs it) two squares wide, x = 14..15, z = 2..30: the raid's approach crosses it;
  a 1.5 m SHEER canal (3 notches: a person is trapped, climb_proof) x = 18..19, z = 18..26, just east of the 1 m canal and
  beside the approach: an equally covered cast spot (first run had it at x 22..23 z 24..32 and no raider came within 6);
  six Mercenary_Gunner of a hostile faction at (44, 12..17) in a plain LordJob_AssaultColony (jawa/lord_assault_spawn).
Rows:
  TRENCH_raiders_cast_from_canal   PROVE raider positions + jobs (jawa/attack_target_probe curJob) every 250 ticks.
                                   EXPECT at least one raider sampled ON a 1 m canal square with a ranged attack/wait job.
                                   LIES: raiders that never come within range of the colony measure the AI, not the canal
                                   (UNMEASURED when no raider ever fired); a raider merely walking across the canal is not
                                   casting (the job must be AttackStatic / Wait_Combat / UseVerbOnThing).
  TRENCH_raiders_skip_sheer_cage   EXPECT no raider is ever sampled on a 1.5 m sheer canal square. LIES: a raid that never
                                   came near it; recorded as the closest any raider came.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

CASTING = ("AttackStatic", "Wait_Combat", "UseVerbOnThing", "AttackMelee")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,110")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=4000)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "trench_cast_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "trench_cast_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": "TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "detail": det})
        print("%-32s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:500]), flush=True)
        save()

    def both(st, cls, det):
        for rid in ("TRENCH_raiders_cast_from_canal", "TRENCH_raiders_skip_sheer_cage"):
            row(rid, st, cls, det)

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        both("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 50, 34)
    site_rows = []
    # a rerun on the same map would deepen the old cut again: the dug state of the plot is reset first
    B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    V.prepare_site(B, rect, site_rows, "cast_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        both("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    canal = {P(x, z) for x in (14, 15) for z in range(2, 31)}
    sheer = {P(x, z) for x in (18, 19) for z in range(18, 27)}
    for c, n in [(c, 2) for c in sorted(canal)] + [(c, 3) for c in sorted(sheer)]:
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=n, setFill=-1)
    bad = [c for c, n in ((P(14, 16), 2), (P(18, 22), 3))
           if (B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=0, setFill=-1) or {}).get("depth") != n]
    if bad:
        both("UNMEASURED", "SITE", {"why": "canal depths did not read back", "cells": bad})
        return 2
    # every pawn already on the map leaves (start colonists would give the raid a second, uncontrolled target)
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    cols = []
    for k in range(3):
        r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(2 + k, 16)[0], z=P(2 + k, 16)[1], faction="player", count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            B.call("jawa/set_draft", pawnId=pid, drafted=True)
            cols.append(pid)
    probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=0, z=0, faction="?", count=1, _answer=True) or {}
    avail = (probe.get("details") or {}).get("available") or []
    fac = next((f["def"] for f in avail if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
    if not fac or len(cols) < 3:
        both("UNMEASURED", "SITE", {"why": "no hostile Pirate faction or colonists missing", "faction": fac, "colonists": cols})
        return 2
    raiders = []
    for k in range(6):
        r = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=P(44, 12 + k)[0], z=P(44, 12 + k)[1], faction=fac, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            raiders.append(pid)
    B.call("jawa/lord_assault_spawn", pawns=",".join(raiders))

    def step(n):   # the governed clock (B.ticks) stops on the hostiles this row stages on purpose: the plain stepper
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}
    step(70)
    samples, cast, inSheer, fired = [], [], [], False
    closest_sheer = None
    t = 0
    while t < a.ticks:
        step(250)
        t += 250
        snap = []
        for pid in raiders:
            pr = B.call("jawa/attack_target_probe", pawn=pid, maxDist=60, _answer=True) or {}
            pos = pr.get("position") or {}
            c = (pos.get("x"), pos.get("z"))
            job = pr.get("curJob")
            snap.append((pid, c, job))
            if job in CASTING:
                fired = True
                if c in canal:
                    cast.append((t, pid, c, job))
            if c in sheer:
                inSheer.append((t, pid, c))
            if c[0] is not None:
                d = min(max(abs(c[0] - s[0]), abs(c[1] - s[1])) for s in sheer)
                closest_sheer = d if closest_sheer is None else min(closest_sheer, d)
        samples.append({"t": t, "raiders": snap})
        save()
    res["samples"] = samples
    det = {"castOnCanal": cast[:12], "firedAtAll": fired, "raiders": raiders, "colonists": cols, "ticks": t}
    if cast:
        row("TRENCH_raiders_cast_from_canal", "PASS", "MOD", det)
    else:
        row("TRENCH_raiders_cast_from_canal", "FAIL" if fired else "UNMEASURED", "MOD" if fired else "SITE",
            dict(det, why=None if fired else "no raider ever took a ranged job: the raid measured nothing"))
    row("TRENCH_raiders_skip_sheer_cage", "PASS" if not inSheer else "FAIL", "MOD",
        {"inSheer": inSheer[:12], "closestChebyshevToSheer": closest_sheer})
    for pid in raiders + cols:
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
