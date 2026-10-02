import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host=host, port=port, token=token).connect()
for pid in ("Human822690", "Human822693", "Human822716"):  # Holmes, Hicks, Metti
    r = rb.call("jawa/pawn_get", {"pawn": pid})
    j = r.get("job") or r.get("curJob") or {}
    print(pid, "job:", json.dumps(j)[:300])
    print(pid, "inspect:", rb.call("jawa/inspect_string", {"pawn": pid}).get("inspectString"))
