"""Read-back only (pawns already spawned by part 5)."""
import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    pawns = lp["pawns"]
    mine = [p for p in pawns if p["kind"] in ("RSW_Cindermare", "RSW_Skarnix")]
    print("found", len(mine), "of our pawns")

    crashes = []
    for p in mine:
        try:
            insp = rb.call("jawa/inspect_string", {"thingIds": [p["id"]]})
            print(p["id"], "inspect_string:", json.dumps(insp)[:600])
        except Exception as e:
            crashes.append((p["id"], "inspect_string", str(e)))
            print(p["id"], "inspect_string EXC:", e)
        try:
            pg = rb.call("jawa/pawn_get", {"pawn": p["id"]})
            print(p["id"], "pawn_get:", json.dumps(pg)[:800])
        except Exception as e:
            crashes.append((p["id"], "pawn_get", str(e)))
            print(p["id"], "pawn_get EXC:", e)

    print("=== CRASHES:", crashes)
