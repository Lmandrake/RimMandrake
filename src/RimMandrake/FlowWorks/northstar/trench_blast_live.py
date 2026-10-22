"""TRENCH BLAST live check (TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT A4, owner Q7 "no blast cover"; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/trench_blast_live.py [out.json] [--origin X,Z] [--fresh-map] [--trials N]

PROVE  N trials: a drafted colonist standing in a dry 1 m trench (2 notches, the trench_cover_proof depth) and a drafted
       control colonist on open ground 20 squares east; one jawa/explosion_at (GenExplosion.DoExplosion, the utility every
       grenade calls; Bomb, radius 1.9 like a frag grenade, damAmount 20, armorPenetration 2 so armour rolls cancel) on each
       pawn's own square. The damage each victim was DEALT is read from jawa/damage_log (victim, tick window).
EXPECT the trench victims' mean dealt damage is the control's within +/-25% (no blast cover), and the control took damage
       at all (the can-fail: a blast that hurts nobody proves nothing -> UNMEASURED).
LIES   damage dealt after armour differs per body part hit (the part roll): N trials and a +/-25% band, never one pair; a
       trench the dig drive never cut (read back: depth 2) would compare open ground with open ground -> UNMEASURED/SITE.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="70,200")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--trials", type=int, default=6)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "trench_blast_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "trench_blast_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": "TRENCH_COVER_BUILD_SANDBAGS_MADE_OF_DIRT", "detail": det})
        print("%-26s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    ox, oz = (int(v) for v in a.origin.split(","))
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("TRENCH_no_blast_cover", "UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 34, 4 * a.trials + 4)
    site_rows = []
    # a rerun on the same map would deepen the old cut again: the dug state of the plot is reset first
    B.call("jawa/static_call", type="RimMandrake.FlowWorks.RM_NorthstarProofs", method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    V.prepare_site(B, rect, site_rows, "blast_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("TRENCH_no_blast_cover", "UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    dealt = {"trench": [], "open": []}
    trials = []
    for k in range(a.trials):
        z = oz + 2 + 4 * k
        tc, oc = (ox + 4, z), (ox + 24, z)
        for x in range(ox + 1, ox + 8):          # a 7-square east-west trench, 1 m
            B.call("jawa/flowworks_excavation_drive", x=x, z=z, deepenLevels=2, setFill=-1)
        d = (B.call("jawa/flowworks_excavation_drive", x=tc[0], z=tc[1], deepenLevels=0, setFill=-1) or {}).get("depth")
        if d != 2:
            row("TRENCH_no_blast_cover", "UNMEASURED", "SITE", {"why": "trench square not at 1 m", "depth": d, "cell": tc})
            return 2
        ids = {}
        for nm, c in (("trench", tc), ("open", oc)):
            r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1) or {}
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            if pid:
                B.call("jawa/set_draft", pawnId=pid, drafted=True)
            ids[nm] = pid
        B.ticks(70)                                # the pocket grid sees the dug squares
        t0 = (B.call("rimworld/get_game_info") or {}).get("ticksGame")
        for nm, c in (("trench", tc), ("open", oc)):
            B.call("jawa/explosion_at", at="%d,%d" % c, radius=1.9, damType="Bomb", damAmount=20, armorPenetration=2.0)
        B.ticks(2)
        log = B.call("jawa/damage_log", limit=200) or {}
        ev = log.get("events") or log.get("entries") or []
        tr = {"tick0": t0, "ids": ids}
        for nm, pid in ids.items():
            tot = 0.0
            for e in ev:
                vic = e.get("victim") or e.get("victimId")
                vid = vic.get("id") if isinstance(vic, dict) else vic
                if str(vid) == str(pid) and (e.get("tick") or 0) >= (t0 or 0) and e.get("kind", "damage") == "damage":
                    tot += float(e.get("dealt") or e.get("amount") or 0)
            dealt[nm].append(tot)
            tr[nm] = tot
        trials.append(tr)
        for pid in ids.values():
            if pid:
                B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish")
    mt = sum(dealt["trench"]) / len(dealt["trench"])
    mo = sum(dealt["open"]) / len(dealt["open"])
    det = {"meanTrench": mt, "meanOpen": mo, "ratio": (mt / mo) if mo else None, "dealt": dealt, "trials": trials,
           "logKeys": sorted((ev[0] if ev else {}).keys())}
    if mo <= 0:
        row("TRENCH_no_blast_cover", "UNMEASURED", "HARNESS", dict(det, why="the open-ground control took no damage"))
        return 2
    good = 0.75 <= mt / mo <= 1.25
    row("TRENCH_no_blast_cover", "PASS" if good else "FAIL", "MOD", det)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
