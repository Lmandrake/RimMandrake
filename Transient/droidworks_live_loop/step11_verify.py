import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()

with RimBridge(host, port, token) as rb:
    print("=== hediffs on kg[0] post-597-tick (full) ===")
    g = rb.call("jawa/pawn_get", {"pawn": "RSW_DW_Race_guy762_DroidRace_ADMkI18331"})
    p = g.get("pawns", [{}])[0]
    print("hediffs field:", json.dumps(p.get("hediffs"), default=str))
    print("all top keys:", list(p.keys()))

    print("=== filth/fire near GNK site (rect 128,88,20,15) ===")
    things = rb.call("jawa/list_things", {"rect": "128,88,20,15"})
    for t in things.get("things", []):
        d = t.get("def","")
        if "Filth" in d or "Fire" in d or "Burn" in d or "Rubble" in d or "Corpse" in d:
            print(" ", d, t.get("x"), t.get("z"))
