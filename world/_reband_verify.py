import sys, json, collections, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want={p['tile']:p['to'] for p in json.load(open(r"D:\Luke\dev\Rimworld\world\backside_reband_plan.json"))}
before={int(r['tile']):r['biome'] for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
with RimBridge(host, port, token) as rb:
    live={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): live[t["tile"]]=t["biome"]
    changed=[t for t in before if live.get(t)!=before[t]]
    unexpected=[t for t in changed if t not in want]
    print(f"tiles changed from committed CSV: {len(changed)} | expected: {len(want)} | UNEXPECTED: {len(unexpected)}")
    if unexpected: print("  unexpected sample:", [(t,before[t],live[t]) for t in unexpected[:5]])
    census=collections.Counter(live.values())
    for b in ['AB_RockyCrags','RUT_NightsideIce','BiomeGRimond','AB_PropaneLakes','RUT_PropaneLake','AB_MycoticJungle']:
        print(f"  live {b:20s} {census[b]}")
    ln=rb.call("jawa/world_lint", {})
    print("world_lint findings:", ln.get("findingCount", ln.get("findings")))
    rb.call("jawa/clear_ui", {}); rb.call("rimworld/close_window", {"windowType":"LudeonTK.EditWindow_Log"})
    rb.call("jawa/world_view", {"centerTile": 14301, "altitude": 340})
    s=rb.call("rimworld/take_screenshot", {})
    print("shot:", s.get("path"))
