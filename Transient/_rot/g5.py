import sys, json, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.getcwd(), "src", "RimMandrake", "Utils"))
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    m=rb.call("jawa/list_things",{"defName":"RUT_PaleMoss","limit":300})
    print("moss count:", m.get("count") or len(m.get("things",[])), m.get("message"))
    ps={p["id"]:p for p in rb.call("jawa/list_pawns",{"faction":"player"}).get("pawns",[])}
    g=ps["Human122"]; print("Giggles at", (g["x"],g["z"]))
    print("psylink:", json.dumps(rb.call("jawa/pawn_psychic",{"pawn":"Human122","action":"get"}))[:400])
    print("tree:", json.dumps(rb.call("jawa/inspect_string",{"defName":"RUT_PaleTree"}).get("things"))[:500])
