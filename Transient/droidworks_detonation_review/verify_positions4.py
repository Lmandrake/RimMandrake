import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with open(r"D:\Luke\dev\Rimworld\Transient\droidworks_detonation_review\grid_with_ids.json") as f:
    grid = json.load(f)

with RimBridge(host, port, token) as rb:
    for cell in grid:
        pg = rb.call("jawa/pawn_get", {"pawn": cell["pawnId"]})
        row = pg["pawns"][0]
        print(cell["cell"], "count", pg["count"], "x/z:", row.get("x"), row.get("z"),
              "needs:", row.get("needs"))
