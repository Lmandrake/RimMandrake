import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\grid_with_ids.json") as f:
    grid = json.load(f)

with RimBridge(host, port, token) as rb:
    pg = rb.call("jawa/pawn_get", {"pawn": "", "limit": 60})
    by_id = {row["thingId"]: row for row in pg["pawns"]}
    ok = True
    for cell in grid:
        row = by_id.get(cell["pawnId"])
        if row is None:
            print(cell["cell"], "NOT FOUND in listing for id", cell["pawnId"])
            ok = False
            continue
        match = (row["x"] == cell["x"] and row["z"] == cell["z"])
        print(cell["cell"], cell["pawnId"], "expected", (cell["x"], cell["z"]),
              "actual", (row["x"], row["z"]), "kindDef", row["kindDef"], "MATCH" if match else "MISMATCH")
        ok = ok and match
    print("ALL MATCH:", ok)
