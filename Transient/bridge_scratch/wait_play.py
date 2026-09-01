import sys, json, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
rb = RimBridge(host, port, token, timeout=300.0); rb.connect()
def call(t, **p):
    r = rb.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r
for i in range(120):
    st = call("rimworld/get_ui_state")
    bs = call("rimbridge/get_bridge_status").get("state") or {}
    print("t=%3ds state=%s longEvent=%s hasGame=%s" % (i*5, st.get("programState"),
          bs.get("longEventPending"), bs.get("hasCurrentGame"))); sys.stdout.flush()
    if st.get("programState") == "Playing": break
    time.sleep(5)
