#!/usr/bin/env python3
"""Build the owner's labelled walk save for visit 5: stage proof scenes at the map's scene origins (one station each),
step each to rest, read its verdict, pin a sign book on each station (SIGN nn <scene> <VERDICT>, LOOK / DO / DECIDE),
then save through reviewmap.save_keeper (refuses an existing name, proves one new file and none changed).

    python.exe design\\concepts\\ExplosiveKnockback\\version\\in_game\\visit_5\\scripts\\walk_save.py NAME [--ticks 300]

Prints one line per station and the save_keeper result as JSON on the last line. Settings are put back after.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 7))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "Utils", "modcheck"))
sys.path.insert(0, os.path.join(REPO, "src", "RimMandrake", "ExplosiveKnockback"))

# (scene, what to look at, what to do, what to decide); the check each one belongs to is in version/test_table.json
STATIONS = [
    ("calibration", "the colonist thrown 3 cells along the blast ray", "unpause briefly or read its health", "is the throw distance and stun believable?"),
    ("over_sandbags", "two colonists thrown over a sandbag line", "look where they landed", "do they clear the line and land standing ground?"),
    ("wall_stop", "a colonist stopped dead at a wall", "check its injuries", "does the wall stop read as a hard stop?"),
    ("door_stop", "a colonist stopped at a door, a second at deep water", "check the door's hit points", "do door and water stop the throw?"),
    ("pawn_hits_pawn", "a thrown colonist stopped by a standing pawn", "look at both pawns", "does the stop look right?"),
    ("goods_fly_wild", "a storeroom of goods thrown by a mortar", "look at the scatter", "does it read as a wild scatter?"),
    ("open_storage", "goods blown off open shelves", "look at the shelves", "are shelves emptied as open storage should be?"),
    ("closed_containers", "closed lockers that kept their goods; some thrown", "open a locker", "do closed containers feel protective?"),
    ("heavy_knock", "a heavy steel stack that struck a colonist", "check the colonist's bruise", "is the knock fair for the mass?"),
    ("gas_chain", "a burned gas cloud and the goods it shoved", "look at the goods near the cloud", "did it go off clump by clump?"),
    ("cover_breaks", "pit covers broken by a blast", "look at the pits", "do the broken covers and falls read right?"),
    ("pit_colonist", "a colonist and a stack thrown into a pit", "look into the pit", "is falling in by a blast clear?"),
    ("killed_by_blast", "colonists killed by a blast, thrown as corpses", "look at the corpses", "is it grim but right?"),
    ("storeroom_bomb_pit", "the showcase storeroom: people and goods into a pit", "look at the cover cell (known: it stays)", "is the showcase convincing?"),
    ("shield_counter", "a shielded colonist who stayed put", "check its shield energy", "does the shield hold believably?"),
    ("goods_obstacles", "goods thrown at a door, sandbags and deep water", "look at each lane", "do goods stop and bounce right?"),
]


def main():
    name = sys.argv[1]
    ticks = int(sys.argv[sys.argv.index("--ticks") + 1]) if "--ticks" in sys.argv else 300
    import knockback_runner as K
    import reviewmap as RM
    from rimbridge_client import RimBridge, resolve_endpoint
    host, port, token = resolve_endpoint()
    lb = RM.LiveBridge()
    with RimBridge(host=host, port=port, token=token) as b:
        snap = K.snapshot_settings(b)
        signs, rows = [], []
        try:
            K.call(b, "Settings", "reset")
            K.call(b, "Clear", "x")
            origins = K.call(b, "Origins", str(len(STATIONS))).split(";")
            staged = []
            for i, ((scene, look, do, decide), org) in enumerate(zip(STATIONS, origins)):
                r = K.call(b, "Stage", "%s,%s" % (scene, org))
                staged.append((i, scene, look, do, decide, org, r))
            K.advance_scene(b, ticks)
            for i, scene, look, do, decide, org, r in staged:
                st, _, det = K.parse_verdict(r)
                v = K.parse_verdict(K.call(b, "Verdict", scene))[0] if st == "STAGED" else st
                x, z = (int(c) for c in org.split(","))
                key = "%02d" % (i + 1)
                signs.append(RM.sign_book(x, z - 3, key, "%s %s" % (scene, v), look=look, do=do, decide=decide,
                                          more="visit 5 proof verdict %s; check rows in design/concepts/ExplosiveKnockback/version/in_game/visit_5/rows.jsonl" % v))
                rows.append((key, scene, v, org))
                print("SIGN %s %-20s %-8s at %s" % (key, scene, v, org), flush=True)
        finally:
            K.restore_settings(b, snap)
    pr = RM.place_signs(lb, signs)
    print("signs placed: %s" % (len(pr.get("placed") or []) if isinstance(pr, dict) else pr))
    b2 = RM.LiveBridge()
    out = RM.save_keeper(b2, name, saves=RM.SAVES, signs=signs)
    print(json.dumps({"save": out, "stations": rows}))


if __name__ == "__main__":
    main()
