import sys
from collections import Counter
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    rb.call("jawa/world_tile_export", {"path": r"D:\Luke\dev\Rimworld\Transient\canonical_check.csv"})
import csv
c = Counter(r['biome'] for r in csv.DictReader(open('Transient/canonical_check.csv')))
# punch-list signatures: Rot 2258 (post cold-tail), NightsideIce 1506, Greentide 235, Webwork 161
print("AB_MycoticJungle (Rot):", c['AB_MycoticJungle'], "| punch-list=2258, pre=2348")
print("RUT_NightsideIce:", c['RUT_NightsideIce'], "| punch-list=1506, pre~1416")
print("BiomeCypreJungle (Greentide):", c['BiomeCypreJungle'], "| punch-list=235")
print("AB_FeraliskInfestedJungle (Webwork):", c['AB_FeraliskInfestedJungle'], "| punch-list=161")
print()
print("VERDICT:", "PUNCH-LIST WORLD (complete)" if c['RUT_NightsideIce'] >= 1500 else "PRE-PUNCH-LIST WORLD (missing biome repaints — V28 has them)")
