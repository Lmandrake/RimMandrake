"""Visit 5 diagnostic (no verdict): the raw inspect-pane lines of ember grass and Plant_Grass on the site, by defName
and by a 4x4 rect around the first one, to see why _ten_embergrass_regrow_growth read None. Exit 0 always."""
import json, os, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 7))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils"))
sys.path.insert(0, os.path.join(ROOT, "src", "RimMandrake", "Utils", "modcheck"))
from rimbridge_client import RimBridge, resolve_endpoint  # noqa: E402
import clockgate  # noqa: E402
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as raw:
    class _S:
        def call(self, name, **kw):
            return clockgate._unwrap(raw.call(name, kw))
    rb = _S()
    for d in ("RM_FE_Plant_EmberGrass", "Plant_Grass", "RM_FE_Plant_Quickgrass"):
        r = rb.call("jawa/inspect_string", defName=d, limit=2)
        rows = r.get("things") or []
        print("BYDEF", d, r.get("message"), json.dumps([{k: x.get(k) for k in ("id", "x", "z", "inspect", "lowPriority", "error")} for x in rows])[:900])
        if rows:
            x, z = rows[0]["x"], rows[0]["z"]
            rr = rb.call("jawa/inspect_string", rect="%d,%d,4,4" % (x - 1, z - 1), limit=100)
            print("BYRECT", d, rr.get("message"), json.dumps([(y.get("defName"), y.get("inspect")) for y in (rr.get("things") or [])])[:1500])
