import sys, json, collections, csv
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
want={p['tile']:p['to'] for p in json.load(open(r"D:\Luke\dev\Rimworld\world\pf_terminator_plan.json"))}
with RimBridge(host, port, token) as rb:
    live={}
    for i in range(0,21872,2000):
        rr=rb.call("jawa/world_tile_get", {"range": f"{i}-{min(i+1999,21871)}", "limit": 2500})
        for t in rr.get("tiles",[]): live[t["tile"]]=t["biome"]
    ok=sum(1 for t,b in want.items() if live.get(t)==b)
    print(f"moved tiles correct: {ok}/{len(want)}")
    census=collections.Counter(live.values())
    for b in ['PoisonForest','Desert','Wasteland','ZBiome_Badlands','AridShrubland','AB_RockyCrags','RUT_NightsideIce','BiomeGRimond','AB_PropaneLakes','AB_MycoticJungle']:
        print(f"  live {b:20s} {census[b]}")
    ln=rb.call("jawa/world_lint", {}); print("lint:", ln.get("findingCount", ln.get("findings")))
    rb.call("jawa/clear_ui", {}); rb.call("rimworld/close_window", {"windowType":"LudeonTK.EditWindow_Log"})
    rb.call("jawa/world_view", {"centerTile": 12798, "altitude": 200})
    s=rb.call("rimworld/take_screenshot", {}); print("shot:", s.get("path"))
