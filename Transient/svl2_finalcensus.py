import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint

host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    lp = rb.call("jawa/list_pawns", {})
    print("TOTAL_PAWNS", len(lp.get("pawns", [])))
    for p in lp.get("pawns", []):
        if p.get("faction") == "PlayerColony":
            print(" ", p.get("id"), p.get("name"), "dead=", p.get("dead"))
    letters = rb.call("jawa/letter_list", {})
    deaths = [l for l in letters.get("letters", []) if l.get("defName") == "Death"]
    for d in deaths:
        print("DEATH_LETTER", d.get("label", {}).get("RawText"), d.get("arrivalTick"))
