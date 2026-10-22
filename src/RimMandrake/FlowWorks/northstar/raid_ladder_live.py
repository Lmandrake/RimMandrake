"""RAID LADDER live check (RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP A6 + A7; BENCH belt 2026-10-22).

  python.exe src/RimMandrake/FlowWorks/northstar/raid_ladder_live.py [out.json] [--origin X,Z] [--fresh-map]

Scene (plot from --origin, default 150,190; 14 x 13 cleared + read back): a sheer pit x = 5..8, z = 2..10, dug D 4 (2 m: a
person is trapped, climb_proof). An RM_LadderPortable OWNED BY A HOSTILE FACTION (a raider's scaling ladder, as
JobDriver_RM_RaiderTrenchWork leaves it) on the west wall square (5, 6), rot West: its top square is the bank (4, 6).
Rows:
  RAID_LADDER_COLONIST_CLIMBS_OUT   A7 "your people climb any lowered ladder": a drafted colonist on the pit floor (7, 6) is
                                    ordered to the bank (1, 6). EXPECT he arrives. Can-fail: the same order with no ladder
                                    is refused/stays in (the control is run after the ladder is gone, row A6 below).
  RAID_LADDER_OTHER_HOSTILE_HELD    A7 second half "another hostile faction cannot": a pawn of a DIFFERENT hostile faction
                                    on the pit floor reads held=True (RM_NorthstarProofs.ProofClimb pawn:<id>).
  RAID_LADDER_OWNERS_NOT_HELD       the ladder's own faction on the pit floor reads held=False (it can leave by its ladder):
                                    the can-fail for A6.
  RAID_LADDER_LOST_STRANDS          A6: the ladder destroyed, the same owner-faction raider reads held=True.
HARNESS (first live run): `held` is the pocket's hold (true for anyone in a sheer pit, ladder or not); the faction-aware
answer is `trapped` (other hostile True, the ladder's owners False, then True once the ladder is gone): the rows read trapped.
LIES: a read taken before the pocket grid sees the ladder (70 ticks are waited after every change); a raider that walked
out before the read (its cell is recorded: held is only scored when it is still on the pit floor).
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
ITEM = "RAIDERS_TRENCH_BUILD_BREACH_AND_JUMP"


def kv(txt):
    out = {}
    for tok in (txt or "").replace("|", " ").split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out", nargs="?", default=None)
    ap.add_argument("--origin", default="150,190")
    ap.add_argument("--fresh-map", action="store_true")
    a = ap.parse_args()
    import proof_hose as PH  # noqa: E402
    V = PH.V
    B = PH.PB()
    out = a.out or os.path.join(HERE, "raid_ladder_result_%s.json" % time.strftime("%Y%m%dT%H%M%S"))
    rows = []
    res = {"script": "raid_ladder_live.py", "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "rows": rows, "args": vars(a)}
    IDS = ("RAID_LADDER_COLONIST_CLIMBS_OUT", "RAID_LADDER_OTHER_HOSTILE_HELD", "RAID_LADDER_OWNERS_NOT_HELD",
           "RAID_LADDER_LOST_STRANDS")

    def save():
        with open(out + ".tmp", "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(out + ".tmp", out)

    def row(rid, st, cls, det):
        rows.append({"id": rid, "status": st, "class": cls, "item": ITEM, "detail": det})
        print("%-32s %-10s %-6s %s" % (rid, st, cls, json.dumps(det, default=str)[:400]), flush=True)
        save()

    def all_rows(st, cls, det):
        for rid in IDS:
            if rid not in [r["id"] for r in rows]:
                row(rid, st, cls, det)

    def step(n):
        return B.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=max(60000, n * 40)) or {}

    def climb(pid):
        r = B.call("jawa/static_call", type=NSP, method="ProofClimb", args="pawn:%s" % pid, _answer=True) or {}
        t = str(r.get("result") or r.get("message") or "")
        return kv(t), t

    ox, oz = (int(v) for v in a.origin.split(","))
    P = lambda dx, dz: (ox + dx, oz + dz)  # noqa: E731
    xz = lambda c: "%d,%d" % c  # noqa: E731
    if a.fresh_map:
        B.call("rimworld/go_to_main_menu")
        B.call("rimworld/start_debug_game_ready", readiness="mapData", pauseIfNeeded=True, timeoutMs=280000)
    ok, _ = V._wait_playing(B, leave_s=0)
    if not ok:
        all_rows("UNMEASURED", "HARNESS", {"why": "no game in Playing"})
        return 2
    res["site_calm"] = V.site_calm(B)
    B.call("jawa/kill_hostiles")
    rect = (ox, oz, 14, 13)
    B.call("jawa/static_call", type=NSP, method="ProofResetRect", args="%d;%d;%d;%d" % rect)
    site_rows = []
    V.prepare_site(B, rect, site_rows, "ladder_site")
    if [r for r in site_rows if r.get("status") not in (None, "PASS")]:
        all_rows("UNMEASURED", "SITE", {"why": "site not prepared", "site": site_rows[:2]})
        return 2
    pit = {P(x, z) for x in range(5, 9) for z in range(2, 11)}
    for c in sorted(pit):
        B.call("jawa/flowworks_excavation_drive", x=c[0], z=c[1], deepenLevels=4, setFill=-1)
    probe = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=0, z=0, faction="?", count=1, _answer=True) or {}
    avail = [f.get("def") for f in (probe.get("details") or {}).get("available") or [] if f.get("hostile")]
    owner = next((f for f in avail if str(f).startswith("Pirate")), None)
    other = next((f for f in avail if f and f != owner and f not in ("Entities", "Mechanoid", "Insect")
                  and not str(f).startswith("Pirate")), None)
    res["factions"] = {"owner": owner, "other": other}
    if not owner or not other:
        all_rows("UNMEASURED", "SITE", {"why": "two hostile humanlike factions needed", "available": avail})
        return 2
    lad = P(5, 6)
    bb = B.call("jawa/build_batch", ops="RM_LadderPortable:%d,%d,3" % lad, faction=owner, wipeExisting=False) or {}
    step(70)
    lt = (B.call("jawa/list_things", defName="RM_LadderPortable", rect="%d,%d,1,1" % lad, limit=2) or {}).get("things") or []
    res["ladder"] = {"build": str(bb)[:300], "things": lt}
    if not lt:
        all_rows("UNMEASURED", "SITE", {"why": "the raider ladder did not stand", "build": str(bb)[:300]})
        return 2
    # A7: colonist climbs out by the raider's ladder
    r = B.call("jawa/spawn_pawn", kindDef="Colonist", x=P(7, 6)[0], z=P(7, 6)[1], faction="player", count=1) or {}
    col = ((r.get("pawns") or [{}])[0]).get("id")
    step(70)
    o = B.call("jawa/order_pawn", pawnId=col, x=P(1, 6)[0], z=P(1, 6)[1], waitTicks=1500, draft=True) or {}
    pr = next((p for p in o.get("pawns") or [] if p.get("id") == col), {})
    end = pr.get("end") or {}
    e = (end.get("x"), end.get("z"))
    row("RAID_LADDER_COLONIST_CLIMBS_OUT", "PASS" if e == P(1, 6) else "FAIL", "MOD",
        {"start": P(7, 6), "dest": P(1, 6), "end": e, "ladderFaction": owner, "order": {k: pr.get(k) for k in ("arrived", "canReach", "ticksElapsed")}})
    B.call("jawa/pawn_force_incapacitate", pawn=col, action="vanish")
    # hostile reads
    ids = {}
    for nm, fac, c in (("owner", owner, P(7, 4)), ("other", other, P(7, 8))):
        r = B.call("jawa/spawn_pawn", kindDef="Mercenary_Gunner", x=c[0], z=c[1], faction=fac, count=1) or {}
        ids[nm] = ((r.get("pawns") or [{}])[0]).get("id")
    step(2)
    ko, to = climb(ids["other"])
    kw, tw = climb(ids["owner"])

    def on_floor(k):
        try:
            return tuple(int(v) for v in k["cell"].split(",")) in pit
        except (KeyError, ValueError):
            return False
    if not on_floor(ko):
        row("RAID_LADDER_OTHER_HOSTILE_HELD", "UNMEASURED", "SITE", {"why": "not on the pit floor at the read", "read": to})
    else:
        row("RAID_LADDER_OTHER_HOSTILE_HELD", "PASS" if ko.get("trapped") == "True" else "FAIL", "MOD", {"read": to, "faction": other})
    if not on_floor(kw):
        row("RAID_LADDER_OWNERS_NOT_HELD", "UNMEASURED", "SITE", {"why": "not on the pit floor at the read", "read": tw})
    else:
        row("RAID_LADDER_OWNERS_NOT_HELD", "PASS" if kw.get("trapped") == "False" else "FAIL", "MOD", {"read": tw, "faction": owner})
    # A6: the ladder destroyed
    B.call("jawa/destroy_batch", rects="%d,%d,1,1" % lad, categories="Building")
    step(70)       # the pocket grid sees the loss (a stranded raider cannot leave in the meantime; one that can is the finding)
    gone = not ((B.call("jawa/list_things", defName="RM_LadderPortable", rect="%d,%d,1,1" % lad, limit=2) or {}).get("things"))
    kw2, tw2 = climb(ids["owner"])
    if not gone or not on_floor(kw2):
        row("RAID_LADDER_LOST_STRANDS", "UNMEASURED", "SITE", {"why": "ladder still stands or raider left the floor", "gone": gone, "read": tw2})
    else:
        row("RAID_LADDER_LOST_STRANDS", "PASS" if kw2.get("trapped") == "True" else "FAIL", "MOD", {"before": tw, "after": tw2})
    for pid in ids.values():
        if pid:
            B.call("jawa/pawn_force_incapacitate", pawn=pid, action="vanish", _answer=True)
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    save()
    return 0 if all(r["status"] == "PASS" for r in rows) else 1


if __name__ == "__main__":
    sys.exit(main())
