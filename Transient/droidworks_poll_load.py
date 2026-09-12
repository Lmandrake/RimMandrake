import sys, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
deadline = time.time() + 180
ready = False
while time.time() < deadline:
    try:
        with RimBridge(host, port, token) as rb:
            st = rb.call("rimbridge/get_bridge_status", {})
            s = st.get("state", {})
            print(s.get("programState"), s.get("hasCurrentGame"), s.get("mapCount"), s.get("longEventPending"))
            if s.get("programState") == "Playing" and s.get("mapCount", 0) > 0 and not s.get("longEventPending"):
                ready = True
                break
    except Exception as e:
        print("poll err:", repr(e)[:150])
    time.sleep(6)
print("READY" if ready else "NOT_READY_TIMEOUT")
