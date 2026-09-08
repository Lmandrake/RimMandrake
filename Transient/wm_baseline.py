import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st = rb.call("jawa/world_stats", {})
    print("== world_stats ==")
    print(json.dumps({k: v for k, v in st.items() if k != "operation"})[:2500])
    print()
    lv = rb.call("jawa/world_links_validate", {})
    print("== links_validate ==")
    print(json.dumps({k: v for k, v in lv.items() if k not in ("operation",)})[:1800])
    print()
    ln = rb.call("jawa/world_lint", {})
    print("== world_lint ==")
    d = {k: v for k, v in ln.items() if k != "operation"}
    print(json.dumps(d)[:2500])
