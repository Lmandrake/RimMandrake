import sys, csv
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    r = rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\v24_tiles_after_rot_tail.csv"})
    print("export:", r.get("tilesTotal"))
old = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_live.csv'))}
new = {int(r['tile']): r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\Transient\v24_tiles_after_rot_tail.csv'))}
changed = [t for t in new if old[t] != new[t]]
bio_changed = [t for t in new if old[t]['biome'] != new[t]['biome']]
other_field_changed = [t for t in changed if old[t]['biome'] == new[t]['biome']]
print(f"tiles with ANY field changed: {len(changed)}; biome changed: {len(bio_changed)}; non-biome drift: {len(other_field_changed)}")
moves = Counter((old[t]['biome'], new[t]['biome']) for t in bio_changed)
print("moves:", dict(moves))
rot_cold = [t for t in new if new[t]['biome']=='AB_MycoticJungle' and float(new[t]['temperature']) < -42]
print(f"AB_MycoticJungle tiles < -42C remaining: {len(rot_cold)}")
c = Counter(r['biome'] for r in new.values())
print(f"AB_MycoticJungle: {c['AB_MycoticJungle']} (expect 2258) | RUT_NightsideIce: {c['RUT_NightsideIce']} (expect 1506)")
