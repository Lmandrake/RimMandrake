#!/usr/bin/env python3
"""Build the owner's labelled walk save of visit 6 (python.exe; a fresh AridShrubland quicktest on the proof build).

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\visit_6\\scripts\\walk_save.py NAME [--ticks 300]

RIMMANDRAKE_SHOW_START_STATE_BESIDE_EACH_AFTERMATH_HE_COULD_NOT_JUDGE (owner, 2026-11-23: "replicate their frozen initial
states beside them so I can see before / after"): each station is two sites in one column: the AFTERMATH (stepped to rest,
its verdict read) on the lower row, and the START twin above it, the same scene staged and its explosion removed before
any tick, so it stays as it stood. The clock goes to day first. Signs say only what is there. Settings are put back.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
for p in ("Utils", "Utils/modcheck", "ExplosiveKnockback"):
    sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", *p.split("/")))

# (scene, what stood there and what the blast did, what to decide)
STATIONS = [
    ("calibration", "a colonist one cell from a shell is thrown three cells", "is the distance believable?"),
    ("over_sandbags", "a colonist is thrown clean over a sandbag line", "does it read as flying over?"),
    ("wall_stop", "a colonist is stopped dead at a wall and hurt", "does the stop read as hard?"),
    ("door_stop", "a colonist is stopped at a closed door", "does the door stop the throw?"),
    ("pawn_hits_pawn", "thrown colonists are stopped by standing ones", "does the stop look right?"),
    ("goods_fly_wild", "one component beside a wall is thrown and bounces back off it", "is the bounce believable?"),
    ("open_storage", "goods on open shelves are blown off", "are the shelves emptied as open storage should be?"),
    ("closed_containers", "lockers, a safe and a crate keep their goods; light ones are thrown whole", "do closed containers feel protective?"),
    ("heavy_knock", "a heavy steel stack strikes a colonist and stops; cloth flies past", "is the knock fair?"),
    ("gas_chain", "a cloud of the Cauldron's vent gas burns clump by clump; the yellow haze after is its toxic smoke", "did it scatter the goods?"),
    ("cover_breaks", "a blast breaks pit covers and whoever stood on them falls in", "do the falls read right?"),
    ("pit_colonist", "a colonist and a stack are thrown into pits, open and covered", "is falling in clear?"),
    ("killed_by_blast", "three colonists are killed and their corpses thrown, spinning", "grim but right?"),
    ("storeroom_bomb_pit", "FLAGSHIP: a bomb in a storeroom beside a pit; goods and people go into the pit. Four shelf stacks stay: the blast is too weak that far away", "is the showcase convincing?"),
    ("shield_counter", "a shield belt absorbs the blast and its wearer stays put", "does the shield hold believably?"),
    ("goods_obstacles", "goods thrown at a door, sandbags and deep water", "do goods stop and bounce right?"),
]
LOW, HIGH = 12, 42
if "--high" in sys.argv:      # visit 1 of 0.2.0: a rock with a thick roof stood at 12,42 on the fresh map; the START row moves up
    HIGH = int(sys.argv[sys.argv.index("--high") + 1])


def main():
    name = sys.argv[1]
    ticks = int(sys.argv[sys.argv.index("--ticks") + 1]) if "--ticks" in sys.argv else 300
    import knockback_runner as K
    import reviewmap as RM
    import stage_review as S
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    lb = RM.LiveBridge()
    with RimBridge(host=host, port=port, token=token) as b:
        b.call("rimworld/set_time_speed", {"speed": 0})
        b.call("jawa/destroy_bulk", {"filter": "nonColonists", "dryRun": False})
        b.call("jawa/incident_queue_clear", {})
        S.daylight(b)
        snap = K.snapshot_settings(b)
        signs, rows = [], []
        try:
            K.call(b, "Settings", "reset")
            K.call(b, "Clear", "x")
            free = set(K.call(b, "Origins", "200").split(";"))
            cols = [x for x in range(12, 238, 15)]
            bad = [(x, z) for x in cols for z in (LOW, HIGH) if "%d,%d" % (x, z) not in free]
            if len(cols) < len(STATIONS) or bad:
                sys.exit("NOT STAGED: a pond under %s; use another quicktest map" % bad)
            roofed = [(x, z) for x in cols for z in (LOW, HIGH)
                      if ((b.call("rimworld/get_cell_info", {"x": x, "z": z}).get("cell") or {}).get("roofDefName"))]
            if roofed:
                sys.exit("NOT STAGED: %d sites are under a roof %s; use an open quicktest map" % (len(roofed), roofed[:4]))
            staged = []
            for i, (scene, what, decide) in enumerate(STATIONS):
                staged.append((i, scene, what, decide, K.call(b, "Stage", "%s,%d,%d" % (scene, cols[i], LOW))))
            K.advance_scene(b, ticks)
            for i, scene, what, decide, r in staged:
                st, _, _ = K.parse_verdict(r)
                v = K.parse_verdict(K.call(b, "Verdict", scene))[0] if st == "STAGED" else st
                rows.append((i + 1, scene, v))
                print("STATION %02d %-20s %s" % (i + 1, scene, v), flush=True)
                signs.append(RM.sign_book(cols[i], LOW - 3, "%02d" % (i + 1), "%s AFTER" % scene, look=what + ". Compare with the START site straight above (z %d)" % HIGH,
                                          decide=decide, more="proof verdict %s" % v))
            for i, (scene, what, decide) in enumerate(STATIONS):
                x = cols[i]
                if scene == "gas_chain":        # its Stage lights the gas at once: the same things by hand, the cloud unlit
                    K.call(b, "Settings", "reset")
                    b.call("jawa/destroy_batch", {"rects": "%d,%d,11,11" % (x - 5, HIGH - 5), "categories": "Building,Plant,Item"})
                    for dx, dz in ((1, 0), (-1, 1), (0, -2)):
                        b.call("rimworld/spawn_thing", {"defName": "Steel", "stackCount": 10, "x": x + dx, "z": HIGH + dz})
                    p = b.call("jawa/spawn_pawn", {"kindDef": "Colonist", "x": x - 1, "z": HIGH - 1, "faction": "player", "count": 1})
                    pid = ((p.get("pawns") or [{}])[0]).get("id")
                    b.call("jawa/set_draft", {"pawnId": pid, "drafted": True})
                    ok = b.call("jawa/static_call", {"type": "RimMandrake.Cauldron.RM_MapComponent_VentGas", "method": "SeedCloud",
                                                     "args": "current|%d,%d|2|250" % (x, HIGH)})
                    print("START  10 gas_chain by hand:", str(ok.get("result"))[:80], flush=True)
                else:
                    r = K.call(b, "Stage", "%s,%d,%d" % (scene, x, HIGH))
                    ex = b.call("jawa/list_things", {"defName": "Explosion", "limit": 50}).get("things") or []
                    for t in ex:
                        b.call("jawa/destroy_batch", {"rects": "%d,%d,1,1" % (t["x"], t["z"]), "categories": "Ethereal"})
                    left = b.call("jawa/list_things", {"defName": "Explosion", "limit": 50}).get("things") or []
                    print("START  %02d %-20s %s explosions removed %d left %d" % (i + 1, scene, str(r)[:60], len(ex), len(left)), flush=True)
                    if left:
                        sys.exit("NOT STAGED: an explosion is still on the map")
                signs.append(RM.sign_book(x, HIGH - 3, "%02d" % (i + 1), "%s START" % scene, look="as it stood before the blast; nothing is armed. The AFTER site is straight below (z %d)" % LOW))
            # 0.2.0's blast show lays its scar on a rendered frame after the shell goes off, even paused, so a START twin whose
            # explosion was removed before any tick still gets the scar of a blast that never happened (visit 1 of 0.2.0: a
            # crater on every START site). Let frames pass, then take our scars off the START row and read it back.
            import time
            time.sleep(3)
            scarred = []
            for i, (scene, _w, _d) in enumerate(STATIONS):
                rect = "%d,%d,15,15" % (cols[i] - 7, HIGH - 7)
                scars = [t for t in (b.call("jawa/list_things", {"rect": rect, "limit": 400}).get("things") or [])
                         if str(t.get("defName") or t.get("def") or "").startswith("RM_KnockbackBlast")]
                for t in scars:
                    b.call("jawa/destroy_batch", {"rects": "%d,%d,1,1" % (t["x"], t["z"]), "categories": "Filth"})
                time.sleep(0.5)
                still = [t.get("defName") or t.get("def") for t in (b.call("jawa/list_things", {"rect": rect, "limit": 400}).get("things") or [])
                         if str(t.get("defName") or t.get("def") or "").startswith("RM_KnockbackBlast")]
                print("START  %02d scars removed %d left %d" % (i + 1, len(scars), len(still)), flush=True)
                if still:
                    scarred.append((cols[i], HIGH, still))
            if scarred:
                sys.exit("NOT STAGED: blast scars still on START sites %s" % scarred)
        finally:
            K.restore_settings(b, snap)
        b.call("jawa/set_fog", {"action": "unfog", "rect": "0,0,250,60"})
    pr = RM.place_signs(lb, signs)
    print("signs placed: %s" % len(pr.get("placed") or []))
    out = RM.save_keeper(RM.LiveBridge(), name, saves=RM.SAVES, signs=signs)
    print(json.dumps({"save": out, "stations": rows}))


if __name__ == "__main__":
    main()
