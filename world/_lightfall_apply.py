import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
plan=json.load(open(r"D:\Luke\dev\Rimworld\world\lightfall_enlarge_plan.json"))
tiles=[p['tile'] for p in plan]
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r=rb.call("jawa/world_landmarks_set", {"tiles":",".join(map(str,tiles)), "def":"Chasm"})
    print("added:", r.get('added'), "success:", r.get('success'))
    rb.call("jawa/world_commit", {})
    lm=rb.call("jawa/world_landmarks_get", {"limit":4000})
    got={l['tile']:l['def'] for l in lm.get('landmarks',[])}
    ok=[t for t in tiles if got.get(t)=='Chasm']
    print(f"LIGHTFALL now {len(ok)}/{len(tiles)} Chasm tiles")
