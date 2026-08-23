"""Do the 28 biomes the authored planet uses actually EXIST in the running game?

READ-ONLY. Calls `jawa/get_defs` and nothing else: it does not start a game, does
not instantiate a map, and writes nothing. Safe to run at the main menu or on the
world screen.

    python.exe D:\\Luke\\dev\\Rimworld\\src\\RimMandrake\\bridgetools\\check_map_biomes_live.py
    python3 /mnt/d/Luke/dev/Rimworld/src/RimMandrake/bridgetools/check_map_biomes_live.py

WHY THIS AND NOT THE DEF DUMP. The DefDump is a snapshot taken at ONE point in the
load, and Cherry Picker removes defs late - the 2026-08-23T05-05-29Z capture still
holds every biome Cherry Picker is configured to cut, so it is a PRE-REMOVAL
reading and cannot answer what the game finally has. The live bridge can.

A biome reported missing here is real: world/ASHKARR_WORLDMAP_tiles.csv names it on
N tiles and the stamp would have nothing to put there.
"""
import csv, collections, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
for cand in (os.path.join(REPO, "src", "RimMandrake", "Utils"),
             r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils",
             "/mnt/d/Luke/dev/Rimworld/src/RimMandrake/Utils"):
    if os.path.isdir(cand):
        sys.path.insert(0, cand)
        break
try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception: pass
import rimbridge_client as rb

TILES_CSV = None
for cand in (os.path.join(REPO, "world", "ASHKARR_WORLDMAP_tiles.csv"),
             r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv",
             "/mnt/d/Luke/dev/Rimworld/world/ASHKARR_WORLDMAP_tiles.csv"):
    if os.path.isfile(cand):
        TILES_CSV = cand
        break
if not TILES_CSV:
    sys.exit("could not find ASHKARR_WORLDMAP_tiles.csv")

counts = collections.Counter()
with io.open(TILES_CSV, encoding="utf-8", newline="") as fh:
    for row in csv.DictReader(fh):
        counts[row["biome"]] += 1
total = sum(counts.values())
print("map: %d tiles over %d distinct biomes  (%s)" % (total, len(counts), TILES_CSV))

host, port, token = rb.resolve_endpoint()
S = rb.RimBridge(host=host, port=port, token=token, timeout=120.0); S.connect()

def call(t, **p):
    r = S.call(t, p) or {}
    if isinstance(r, dict) and r.get("content"):
        try: r = json.loads(r["content"][0]["text"])
        except Exception: pass
    return r

res = call("jawa/get_defs",
           defs=";".join("BiomeDef/%s" % b for b in sorted(counts)),
           fields="label", limit=200)
if not res.get("success", True) and not res.get("defs"):
    sys.exit("REFUSED: %s" % res.get("message"))

found = {r.get("defName") for r in (res.get("defs") or res.get("rows") or [])
         if isinstance(r, dict) and r.get("found", True)}
notfound = set(res.get("notFound") or [])
missing = [(b, n) for b, n in counts.most_common()
           if b not in found or ("BiomeDef/%s" % b) in notfound or b in notfound]

lost = sum(n for _, n in missing)
print("LIVE: %d of %d biomes resolve." % (len(counts) - len(missing), len(counts)))
for b, n in missing:
    print("   MISSING  %-32s %6d tiles  (%.1f%% of planet)" % (b, n, 100.0 * n / total))
if missing:
    print("\n\U0001f534 %d tiles (%.1f%% of the planet) name a biome the running game does "
          "not have.\n   Do NOT stamp the planet until this is resolved." % (lost, 100.0 * lost / total))
else:
    print("\n\u2705 every biome the map names exists in the running game.")
