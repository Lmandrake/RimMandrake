"""UNDERPASS RAID live check (SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD A7: "raiders in a 4 m moat walk under a bridge";
suspension_bridge_proof's owed row UND_raiders_walk_under_moat; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/underpass_raid_live.py [out.json] [--origin X,Z] [--fresh-map] [--ticks N]

Scene (plot from --origin, default 40,180; 30 x 9 cleared + read back): a moat x = 0..25, z = 3..4 (2 wide) dug 8 notches
(4 m); a 1-wide steel suspension bridge across it at x = 12, (12,2)-(12,5) (RM_SuspensionProofs.ProofBuild god); two
Mercenary_Slasher (melee) of a hostile faction on the moat floor at (1..2, 3) in a LordJob_AssaultColony; one colonist,
drafted, on the moat floor at (24, 4) -- the only colonist on the map, so the raid's way to him runs along the floor
under the deck.
PROVE raider positions every 60 ticks for --ticks (default 2400).
EXPECT a raider sampled on a deck-covered floor square (12, 3..4) or east of it (x > 12) on the floor.
LIES  raiders that never move (the lord sat) -> UNMEASURED; a raider ON the deck is not under it (the deck is the bridge's
      row; under = the same squares at floor level: the floor is the only place a moat-bound raider can be).
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
SPROOF = "RimMandrake.FlowWorks.Pits.RM_SuspensionProofs"
ITEM = "SUSPENSION_UNDERPASS_BUILD_MIND_YOUR_HEAD"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="40,180")
    ap.add_argument("--fresh-map", action="store_true")
    ap.add_argument("--ticks", type=int, default=2400)
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "underpass_raid_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "underpass_raid_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(st, cls, det):
        rows.append({"id": "UND_raiders_walk_under_moat", "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-28s %-10s %-6s %s" % ("UND_raiders_walk_under_moat", st, cls, json.dumps(det, default=str)[:600]), flush=True)
        save()

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        row("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox - 1, oz, 30, 9)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "underpass_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        row("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    moat = {P(x, z) for x in range(0, 26) for z in (3, 4)}
    for c in sorted(moat):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=8, setFill=-1)
    bt = str((B.call("jawa/static_call", type=SPROOF, method="ProofBuild", args="%s;%s;steel;god" % (xz(P(12, 2)), xz(P(12, 5))),
                     _answer=True) or {}).get("result"))
    if "ok=True" not in bt:
        row("UNMEASURED", "SITE", {"why": "the bridge did not build", "build": bt})
        return 2
    for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []:
        if not p.get("dead"):
            B.call("jawa/pawn_force_incapacitate", pawn=p.get("id"), action="vanish")
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(24, 4)[0], z=P(24, 4)[1], faction="player", count=1) or {}
    col = ((r.get("pawns") or [{}])[0]).get("id")
    B.call("jawa/set_draft", pawnId=col, drafted=True)
    probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Slasher", x=0, z=0, faction="?", count=1, _answer=True) or {}
    fac = next((f["def"] for f in (probe.get("details") or {}).get("available") or []
                if f.get("hostile") and str(f.get("def")).startswith("Pirate")), None)
    if not fac:
        row("UNMEASURED", "SITE", {"why": "no hostile Pirate faction"})
        return 2
    raiders = []
    for k in range(2):
        r = B.call("jawa/spawn_pawn", kindDef="Mercenary_Slasher", x=P(1 + k, 3)[0], z=P(1 + k, 3)[1], faction=fac, count=1) or {}
        pid = ((r.get("pawns") or [{}])[0]).get("id")
        if pid:
            raiders.append(pid)
    B.call("jawa/lord_assault_spawn", pawns=",".join(raiders))
    under = {P(12, 3), P(12, 4)}
    t, trail, seen_under, past, moved = 0, [], [], [], False
    first = {}
    while t < a.ticks:
        step(60)
        t += 60
        ps = {p.get("id"): p for p in (B.call("jawa/list_pawns", limit=400) or {}).get("pawns") or []}
        snap = []
        for pid in raiders:
            p = ps.get(pid) or {}
            c = (p.get("x"), p.get("z"))
            snap.append((pid, c))
            first.setdefault(pid, c)
            if c != first[pid]:
                moved = True
            if c in under:
                seen_under.append((t, pid, c))
            if c in moat and c[0] is not None and c[0] > P(12, 0)[0]:
                past.append((t, pid, c))
        trail.append({"t": t, "raiders": snap})
        if seen_under and past:
            break
    res["trail"] = trail
    det = {"bridge": bt, "under": seen_under[:6], "pastTheBridge": past[:6], "moved": moved, "ticks": t}
    if not moved:
        row("UNMEASURED", "SITE", dict(det, why="the raiders never moved"))
    else:
        row("PASS" if (seen_under or past) else "FAIL", "MOD", det)
    for pid in raiders + [col]:
        B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if rows and rows[-1]["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
