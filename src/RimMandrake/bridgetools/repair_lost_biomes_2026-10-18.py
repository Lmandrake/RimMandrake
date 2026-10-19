"""Put back the 1,903 world tiles that lost their biome to three renames.

WORLDMAP_REPAIR_LOST_BIOMES_ROCKY_TEXTURES. Run under Windows python.exe, game up
with CANONICAL_ASHKARR_START_2026-10-18_DONORFREE.rws loaded on its own mod list:

    python.exe D:\\Luke\\dev\\RimMandrake\\src\\RimMandrake\\bridgetools\\repair_lost_biomes_2026-10-18.py [--apply]

Without --apply it only checks the world is the one the data was measured on.

WHY LIVE AND NOT OFFLINE: owner 2026-08-18/19 - nothing writes a painted world into
a .rws (two dead loads); the planet reaches the game over the bridge. So the tile ids
were measured offline (tileBiome diff, world/lost_biomes_repair_2026-10-18.json) and
are written here, then the game saves under a NEW name. The adopted save is never
overwritten.

WHAT IT RESTORES: the same def under its new name, not a repaint -
    RUT_ForsakenCrags -> RUT_Abyss     1135  (a534284e43)
    RUT_PoisonForest  -> RUT_Cauldron   546  (CAULDRON_FULL_RENAME_1)
    RM_FE_Pyrelands   -> RM_Pyrelands   222  (PYRELANDS_DEFNAME_RENAME_1)
The RM_ twins move at the terminal paint (BIOME_PAINT_ONCE_AT_THE_END_1), not here.
"""
_RM_ROOT = __import__("pathlib").Path(__file__).resolve().parents[3]
import json, sys
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
sys.path.insert(0, str(_RM_ROOT / "src" / "RimMandrake" / "Utils"))
import rimbridge_client as rb

DATA = _RM_ROOT / "world" / "lost_biomes_repair_2026-10-18.json"
SAVE_AS = "CANONICAL_ASHKARR_START_2026-10-18_DONORFREE_REPAIRED"
CHUNK = 400

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=900.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

def biomes_of(ids):
    """RAW biome per tile, read back 100 at a time (every world_*_get caps at 100)."""
    out = {}
    for i in range(0, len(ids), 100):
        part = ids[i:i + 100]
        r = call("jawa/world_tile_get", tiles=",".join(map(str, part)), limit=100)
        for row in r.get("tiles") or []:
            out[int(row.get("tile", row.get("id", -1)))] = row.get("biome")
    return out

data = json.loads(DATA.read_text())
fallback = data["fallback_now"]
bad = 0
for g in data["groups"]:
    now = biomes_of(g["tiles"])
    wrong = [t for t in g["tiles"] if now.get(t) not in (fallback, g["target"])]
    print("%-14s %4d tiles  now: %s  unexpected: %d" % (
        g["target"], g["count"], sorted(set(now.values())), len(wrong)))
    bad += len(wrong) + (g["count"] - len(now))
if bad:
    sys.exit("STOP: %d tiles are not %s/target or did not read back - wrong world loaded?" % (bad, fallback))
if "--apply" not in sys.argv:
    sys.exit("check only; rerun with --apply")

for g in data["groups"]:
    t = g["tiles"]
    for i in range(0, len(t), CHUNK):
        w = call("jawa/world_tile_set", tiles=",".join(map(str, t[i:i + CHUNK])),
                 biome=g["target"], readBack=0)
        if not w.get("success"):
            sys.exit("world_tile_set failed for %s: %s" % (g["target"], str(w)[:300]))
call("jawa/world_commit")

bad = 0
for g in data["groups"]:
    now = biomes_of(g["tiles"])
    miss = [t for t in g["tiles"] if now.get(t) != g["target"]]
    print("after %-14s %4d / %d" % (g["target"], g["count"] - len(miss), g["count"]))
    bad += len(miss)
if bad:
    sys.exit("STOP: %d tiles did not take; NOT saving" % bad)
print(json.dumps(call("jawa/world_stats", limit=80))[:1500])
r = call("rimworld/save_game", saveName=SAVE_AS)
print("saved:", SAVE_AS, str(r)[:200])
print("NEXT: re-read the new .rws offline (worldmap.WorldGrid) - TemperateForest must be 0,"
      " every non-target tile identical to the donor-free save.")
