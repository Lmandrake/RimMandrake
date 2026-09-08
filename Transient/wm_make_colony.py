import sys, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
cands = open(r"D:\Luke\dev\Rimworld\Transient\wm_candidates.txt").read().strip()
h,p,t = resolve_endpoint()
with RimBridge(h,p,t) as rb:
    before = rb.call("rimworld/get_game_info", {})
    mc0 = before.get("mapCount")
    print("mapCount BEFORE:", mc0)
    s = rb.call("jawa/tile_settleable", {"tiles": cands})
    rows = s.get("tiles") or s.get("results") or []
    ok = [r for r in rows if r.get("settleable") or r.get("valid")]
    print("candidates tested:", len(rows), " settleable:", len(ok))
    if not ok:
        print("NO SETTLEABLE CANDIDATE:", json.dumps(s)[:600]); raise SystemExit(1)
    tile = ok[0].get("tile")
    print("chosen tile:", tile, json.dumps(ok[0])[:200])
    f = rb.call("jawa/colony_found", {"tile": tile, "faction": "Player", "name": "Utinni Landing"})
    print("colony_found:", json.dumps(f)[:300])
    g = rb.call("jawa/world_tile_map_generate", {"tile": tile})
    print("map_generate (RETURN VALUE - NOT TRUSTED):", json.dumps(g)[:300])
    after = rb.call("rimworld/get_game_info", {})
    mc1 = after.get("mapCount")
    print(f"mapCount AFTER: {mc1}   delta={mc1-mc0}   VERDICT={'REAL' if mc1==mc0+1 else 'FABRICATED - map NOT created'}")
