"""Precious caves across several Stillsand maps. usage: caves.py tile [tile...]"""
import sys, json, time
from bx import call
L = r"C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Player.log"
def nlines(): return sum(1 for _ in open(L, encoding="utf-8", errors="replace"))
def since(n): return open(L, encoding="utf-8", errors="replace").read().splitlines()[n:]
out = json.load(open("caves.json")) if len(sys.argv) > 1 and sys.argv[1] == "--append" else {}
tiles = [int(t) for t in sys.argv[1:] if t != "--append"]
call("jawa/world_tile_set", {"tiles": ",".join(map(str, tiles)), "biome": "RM_Stillsand", "temperature": 48, "readBack": 0}, 60)
call("jawa/world_commit", {}, 180)
for t in tiles:
    n = nlines(); t0 = time.time()
    try:
        r = call("jawa/world_tile_map_generate", {"tile": t}, 400)
        res = {k: r.get(k) for k in ("success", "message", "mapId", "mapIndex")}
    except Exception as e:
        res = {"err": str(e)[:200]}
        for i in range(30):
            time.sleep(10)
            try:
                if call("rimbridge/get_bridge_status", {}, 20)["state"].get("currentMapReady") is not None: break
            except Exception: pass
    ls = since(n)
    cave = [l[:400] for l in ls if "[Stillsand]" in l or "Rock island" in l]
    errs = [l[:250] for l in ls if ("Exception" in l or "rror" in l) and "MCR" not in l][:8]
    try:
        rm = call("jawa/settlement_remove", {"mode": "map", "tile": t}, 120); rmr = {k: rm.get(k) for k in ("success", "message")}
    except Exception as e:
        rmr = str(e)[:200]
    out[str(t)] = {"gen": res, "secs": round(time.time() - t0), "stillsand": cave, "errors": errs, "remove": rmr}
    print(t, json.dumps(out[str(t)], default=str)[:1500], flush=True)
    json.dump(out, open("caves.json", "w"), indent=1, default=str)
