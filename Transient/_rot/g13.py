import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    st=rb.call("rimbridge/get_bridge_status",{}).get("state",{})
    print("paused",st.get("paused"),"speed",st.get("timeSpeed"))
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    print("Giggles", (ps["Human122"]["x"],ps["Human122"]["z"]))
    print("explain:", json.dumps(rb.call("jawa/stat_explain",{"subject":"Human122","stats":"MeditationPlantGrowthOffset"}).get("stats"))[:400])
