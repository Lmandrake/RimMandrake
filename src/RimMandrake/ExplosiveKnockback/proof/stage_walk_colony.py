#!/usr/bin/env python3
"""Stage walk_storeroom_raid's storeroom colony on the running quicktest map and save it, so the frame arms can run on the
small list on ANY game (RIMMANDRAKE_RUN_KNOCKBACK_WALK_FRAME_ARMS_SMALL_COLONY_ABSENT: the colony lived on one machine only;
the full-list walk save cannot load on a small list). Cell for cell from EK_WALK_RAID_BASE_20261115T173148: granite walls
96..104 x 36..44, the LWM weapons locker, both shelves, the 11 stacks, the 4 drafted colonists in the room, and the drafted
rider on the faction-less woven scrap cover at 102,36 over a 2 m pit.

    python.exe src\\RimMandrake\\ExplosiveKnockback\\proof\\stage_walk_colony.py --save EK_WALK_SMALL_COLONY_<stamp>

The map must be a quicktest map (live_site.py --biome AridShrubland). Every thing is read back; a miss prints NOT STAGED and
exits 1, nothing saved. Exit 2: no game. The flags for validation.py are printed."""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "Utils"))
import validation_core as V  # noqa: E402
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402

RECT = (92, 31, 18, 19)
COVER = (102, 36)
WALL = [(x, z) for x in range(96, 105) for z in range(37, 45) if x in (96, 104) or z == 44]   # the south side is open, as saved
SOLDIERS = [(101, 40), (100, 39), (98, 38), (103, 43)]
GOODS = [("Cloth", 20, 101, 42), ("MedicineIndustrial", 4, 101, 42), ("Silver", 40, 102, 42), ("ComponentIndustrial", 3, 102, 42),
         ("Beer", 6, 98, 42), ("Chocolate", 8, 98, 42), ("Gun_Autopistol", 1, 98, 40), ("Gun_Revolver", 1, 98, 40),
         ("Steel", 75, 101, 41), ("WoodLog", 8, 99, 41), ("Cloth", 10, 102, 39)]


class B(V._BridgeBase):
    def __init__(self, rb):
        self.rb = rb

    def _raw(self, tool, kw):
        return self.rb.call(tool, kw, check=False)

    def ticks(self, n):
        return self.call("rimworld/step_game_ticks", ticks=n, pauseFirst=True, timeoutMs=120000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", required=True)
    a = ap.parse_args()
    host, port, token = resolve_endpoint()
    with RimBridge(host=host, port=port, token=token, timeout=180.0) as rb:
        b = B(rb)
        b.call("rimworld/set_time_speed", speed=0)
        rows = []
        here = [p.get("id") for p in b.call("jawa/list_pawns", rect="%d,%d,%d,%d" % RECT).get("pawns") or [] if not p.get("dead")
                and p.get("isPlayer")]         # wild animals and strangers are cleared by prepare_site
        if here:                        # live 2026-11-23: a second staging on one map left two colonists on every cell
            print("NOT STAGED: pawns already stand on the site %s; use a fresh quicktest map" % here)
            return 1
        if not V.prepare_site(b, RECT, rows, "walk_colony"):
            print("NOT STAGED: site not prepared: %s" % rows)
            return 1

        def build(ops, **kw):
            r = b.call("jawa/build_batch", ops=ops, **kw)
            print("build", ops[:70], {k: r.get(k) for k in ("placed", "survived", "error")})
        build(";".join("Wall:%d,%d" % c for c in WALL), stuff="BlocksGranite", faction="player")
        build("LWM_WeaponsLocker:98,40", stuff="Steel", faction="player")
        build("ShelfSmall:98,42;Shelf:101,42", stuff="WoodLog", faction="player")
        b.call("jawa/flowworks_excavation_drive", x=COVER[0], z=COVER[1], deepenLevels=4, setBodyWaterM=-1)
        b.ticks(5)
        build("RM_PitCover_WovenScrap:%d,%d" % COVER, wipeExisting=False)
        b.ticks(2)                      # the cover's first load scan runs now, with nobody on it; the next is a countdown away
        for d, n, x, z in GOODS:
            b.call("rimworld/spawn_thing", defName=d, stackCount=n, x=x, z=z)
        pids = []
        for c in SOLDIERS + [COVER]:
            r = b.call("jawa/spawn_pawn", kindDef="Colonist", x=c[0], z=c[1], faction="player", count=1)
            pid = ((r.get("pawns") or [{}])[0]).get("id")
            pids.append(pid)
            b.call("jawa/set_draft", pawnId=pid, drafted=True)
        # no tick once the rider stands on the cover: at the next scan its rating (40 kg) drops a 60 kg rider (live 2026-11-23);
        # the saved full-list colony was written the same way, its ticksUntilScan 28
        things = b.call("jawa/list_things", rect="92,31,18,19", limit=1000).get("things") or []
        defs = [(t.get("def"), t.get("x"), t.get("z")) for t in things]
        pawns = [(p.get("id"), p.get("x"), p.get("z")) for p in b.call("jawa/list_pawns", rect="92,31,18,19").get("pawns") or []]
        miss = ["%s at %d,%d" % (d, x, z) for d, n, x, z in GOODS if not any(t[0] == d for t in defs)]
        miss += ["%s" % d for d in ("LWM_WeaponsLocker", "ShelfSmall", "Shelf") if not any(t[0] == d for t in defs)]
        if not any(str(t[0]).startswith("RM_PitCover") and t[1:] == COVER for t in defs):
            miss.append("the cover")
        if sum(1 for t in defs if t[0] == "Wall") != len(WALL):
            miss.append("%d of %d walls" % (sum(1 for t in defs if t[0] == "Wall"), len(WALL)))
        for pid, c in zip(pids, SOLDIERS + [COVER]):
            if (pid, c[0], c[1]) not in pawns:
                miss.append("pawn %s not at %s" % (pid, c))
        strangers = [p for p in pawns if p[0] not in pids]
        if strangers:
            miss.append("strangers on the site %s" % strangers)
        print("goods read back:", [t for t in defs if t[0] in {g[0] for g in GOODS}])
        print("pawns:", pawns)
        if miss:
            print("NOT STAGED:", "; ".join(miss))
            return 1
        r = b.call("rimworld/save_game", saveName=a.save)
        if r.get("success") is False:
            print("NOT STAGED: save refused %s" % r)
            return 1
        print("STAGED %s   --storeroom 97,37,7,7 --cover 102,36 --gas 100,41 --save %s" % (a.save, a.save))
        return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ConnectionError) as e:
        print("no game reachable: %r" % e)
        sys.exit(2)
