import sys, json, csv, collections
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
P = r"C:\Users\Mandrake\AppData\Local\Temp\ns_tiles.csv"
with Session(lock=None) as s:
    r = s.call("jawa/world_tile_export", path=P); print("export", json.dumps(r)[:300])
rows = list(csv.DictReader(open(P, encoding="utf-8")))
print(len(rows), rows[0].keys())
cnt = collections.Counter(r["biome"] for r in rows if r["hilliness"] in ("Flat",)); print(cnt.most_common(12))
cand = [r for r in rows if r["hilliness"]=="Flat" and r["biome"] in ("Desert","AridShrubland") and float(r["swampiness"])==0 and float(r["elevation"])>=0]
print("flat dry candidates", len(cand), cand[:3])
json.dump([c["index"] if "index" in c else list(c.values())[0] for c in cand[:40]], open("Transient/ns_bland_cands.json","w"))
