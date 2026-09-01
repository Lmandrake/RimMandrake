import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    ch = rb.call("rimworld/list_debug_action_children", {"path": "Actions\\Spawn Pawn..."})["children"]
    jk = [c["path"] for c in ch if "Jawa_Homestead" in c["path"] or "Jawa_DeepDesert" in c["path"]]
    print("kinds found:", len(jk), [p.split(chr(92))[-1] for p in jk[:6]])
    spawned = 0
    for i, p in enumerate((jk*3)[:6]):
        r = rb.call("rimworld/execute_debug_action", {"path": p, "x": 40+i*3, "z": 40})
        spawned += 1 if r.get("success") else 0
    print("spawned:", spawned)
    # substitution probe: jawa/spawn_pawn requesting a named kind
    try:
        rb.call("jawa/spawn_pawn", {"bogus":1})
    except Exception as e:
        print("spawn_pawn declared:", str(e).split("Declared:")[-1].strip()[:120])
