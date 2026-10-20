"""G13 dry run on the live 374 game (AREAFIX2 world): per biome, set a scratch tile's biome (+temperature), generate a
150x150 map with a Camp parent, count wild animals (list_pawns, no faction, alive) and plants (list_things Plant),
read Player.log after Log.Clear for exceptions, then drop the map, remove the Camp, restore the tile.
Usage: python.exe mapgen.py <biome,biome,...> [tempC] [outname]"""
import sys, json, time
from bc import call, j, out, log_clear, log_lines

biomes = sys.argv[1].split(",")
temp = float(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] != "-" else None
oname = sys.argv[3] if len(sys.argv) > 3 else "mapgen.jsonl"
home = call("jawa/map_info")
home_id, htile = home.get("mapId"), int(home.get("tile") or 0)
cands = [htile + d for d in range(40, 40 * 60, 37)]
r = call("jawa/tile_settleable", tiles=",".join(str(c) for c in cands))
rows = r.get("tiles") or r.get("rows") or r.get("results") or []
tiles = [int(x["tile"]) for x in rows if isinstance(x, dict) and x.get("tile") is not None and
         (x.get("settleable") or "not implemented" in str(x.get("reason")))]
print("settleable reply", j({k: v for k, v in r.items() if k != "tiles"}, 300))
print("home", home.get("mapBiome"), htile, "scratch tiles", len(tiles))
f = open(out(oname), "a")
for b, tile in zip(biomes, tiles):
    t0 = time.time()
    orig = (call("jawa/world_tile_get", tiles=str(tile)).get("tiles") or [{}])[0]
    kw = {"tiles": str(tile), "biome": b}
    if temp is not None:
        kw["temperature"] = temp
    ws = call("jawa/world_tile_set", **kw); call("jawa/world_commit")
    log_clear(); mark = len(log_lines())
    before = {m.get("mapId") for m in (call("jawa/list_maps").get("maps") or []) if isinstance(m, dict)}
    g = call("jawa/world_tile_map_generate", tile=tile, suggestedMapParent="Camp", sizeX=150, sizeZ=150)
    mid = g.get("mapId")
    row = {"biome": b, "tile": tile, "temperature": temp, "origBiome": orig.get("biome"),
           "origTemp": orig.get("temperature"), "tileSet": ws.get("success"), "generate": g.get("success"),
           "genMsg": str(g.get("message") or g.get("error"))[:200]}
    if mid is not None and g.get("success") is not False:
        call("jawa/set_current_map", mapId=mid)
        info = call("jawa/map_info")
        ps = call("jawa/list_pawns", limit=3000).get("pawns") or []
        wild = [p for p in ps if not p.get("faction") and not p.get("dead")]
        kinds = {}
        for p in wild:
            kinds[p.get("kind")] = kinds.get(p.get("kind"), 0) + 1
        pl = call("jawa/list_things", group="Plant", limit=1)
        lines = log_lines()[mark:]
        exc = [l for l in lines if "Exception" in l]
        err = [l for l in lines if "rror" in l]
        row.update(mapBiome=info.get("mapBiome"), mapTemp=info.get("outdoorTemp") or info.get("temperature"),
                   wildAnimals=len(wild), pawnsAll=len(ps), kinds=dict(sorted(kinds.items(), key=lambda kv: -kv[1])[:8]),
                   plants=pl.get("countMatched"), plantsRaw=None if pl.get("countMatched") is not None else j(pl, 200),
                   exceptions=exc[:3], nExceptions=len(exc), nErrorLines=len(err), errSample=err[:2], logLines=len(lines))
        call("jawa/set_current_map", mapId=home_id)
        idx = g.get("mapIndex")
        row["drop"] = call("jawa/map_drop", mapIndex=idx, notifyPlayer=False).get("success") if idx is not None else \
            call("jawa/map_drop", mapId=mid, notifyPlayer=False).get("success")
    wr = call("jawa/world_objects_get", tiles=str(tile)); wo = wr.get("objects") or wr.get("worldObjects") or []
    for o in wo:
        if isinstance(o, dict) and o.get("def") == "Camp":
            row["campRemoved"] = call("jawa/world_objects_remove", ids=str(o.get("id"))).get("success")
    kw = {"tiles": str(tile), "biome": orig.get("biome")}
    if orig.get("temperature") is not None:
        kw["temperature"] = orig.get("temperature")
    call("jawa/world_tile_set", **kw); call("jawa/world_commit")
    row["secs"] = round(time.time() - t0, 1)
    f.write(json.dumps(row, default=str) + "\n"); f.flush()
    print(b, "map", row.get("mapBiome"), "animals", row.get("wildAnimals"), "plants", row.get("plants"),
          "exc", row.get("nExceptions"), "err", row.get("nErrorLines"), "drop", row.get("drop"), "camp", row.get("campRemoved"),
          "%ss" % row["secs"], row["genMsg"][:80] if not row.get("generate") else "")
call("jawa/set_current_map", mapId=home_id)
