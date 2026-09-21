import sys, json, os, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
for i in range(40):
    try:
        with RimBridge(host, port, token) as rb:
            s = rb.call("rimbridge/get_bridge_status", {})
            st = s.get("state", {})
            print(i, st.get("programState"), "maps", st.get("mapCount"), "mapId", st.get("currentMapId"), "playable", st.get("playable"), flush=True)
            if st.get("currentMapReady"):
                g = rb.call("rimworld/get_game_info", {})
                print("GAMEINFO", json.dumps(g)[:900], flush=True)
                break
    except Exception as e:
        print(i, "err", str(e)[:120], flush=True)
    time.sleep(8)
