import sys, json, time
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
deadline = time.time() + 240
with RimBridge(host, port, token) as rb:
    while time.time() < deadline:
        st = rb.call("rimbridge/get_bridge_status", {})
        s = st.get("state", {})
        print(time.time(), "playable=", s.get("playable"), "hasCurrentGame=", s.get("hasCurrentGame"),
              "mapCount=", s.get("mapCount"), "programState=", s.get("programState"),
              "longEventPending=", s.get("longEventPending"))
        if s.get("playable") and s.get("hasCurrentGame"):
            print("READY")
            break
        time.sleep(5)
