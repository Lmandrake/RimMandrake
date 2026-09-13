import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    try:
        rb.call("rimworld/apply_architect_designator", {"zzz": 1})
    except Exception as e:
        print("params:", str(e).split("Declared:")[-1])
    # what tool sits at JawaBenchMapTools line ~2405? probe prefab_place faction handling not needed;
    # try designator route:
    r = rb.call("rimworld/apply_architect_designator", {"designatorType": "Designator_Claim", "cellRect": "143,59,86,133", "dryRun": True})
    print("dry:", r.get("success"), str(r)[:200])
