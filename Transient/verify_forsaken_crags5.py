"""FORSAKEN_CRAGS_PREDATORS_BUILD_1 live verify, part 5: spawn batch, check for the AgeTracker crash."""
import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

CINDER_PATH = r"Actions\Spawn Pawn...\RSW_Cindermare"
SKARNIX_PATH = r"Actions\Spawn Pawn...\RSW_Skarnix"

# Away from the colony (colonists around x=128-130, z=130-135). Map size 250.
SPOTS_CINDER = [(20, 20), (25, 22), (30, 25)]
SPOTS_SKARNIX = [(220, 220), (215, 222), (210, 225)]

with RimBridge(host, port, token) as rb:
    for (x, z) in SPOTS_CINDER:
        r = rb.call("rimworld/execute_debug_action", {"path": CINDER_PATH, "x": x, "z": z})
        print("spawn cindermare", x, z, "->", r.get("success"), r.get("message"))
    for (x, z) in SPOTS_SKARNIX:
        r = rb.call("rimworld/execute_debug_action", {"path": SKARNIX_PATH, "x": x, "z": z})
        print("spawn skarnix", x, z, "->", r.get("success"), r.get("message"))

    time.sleep(1)
    lp = rb.call("jawa/list_pawns", {})
    pawns = lp["pawns"]
    mine = [p for p in pawns if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")]
    print("found", len(mine), "of our pawns via list_pawns (no crash iterating list)")
    for p in mine:
        print(" ", p["id"], p["kind"], p["x"], p["z"])

    # Now the crash test: read back each one individually via inspect_string and pawn_get.
    crashes = []
    for p in mine:
        try:
            insp = rb.call("jawa/inspect_string", {"thingIds": [p["id"]]})
            ok1 = insp.get("success")
            print(p["id"], "inspect_string result:", json.dumps(insp)[:500])
        except Exception as e:
            ok1 = False
            crashes.append((p["id"], "inspect_string", str(e)))
        try:
            pg = rb.call("jawa/pawn_get", {"pawn": p["id"]})
            ok2 = pg.get("success")
            print(p["id"], "pawn_get result:", json.dumps(pg)[:500])
        except Exception as e:
            ok2 = False
            crashes.append((p["id"], "pawn_get", str(e)))
        print(p["id"], "inspect_string ok=", ok1, "pawn_get ok=", ok2)

    print("CRASHES:", crashes)
