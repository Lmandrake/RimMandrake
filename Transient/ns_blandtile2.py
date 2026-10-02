import sys, json, csv
sys.path.insert(0, r"src\RimMandrake\Utils")
from rimdrive import Session
rows = list(csv.DictReader(open(r"C:\Users\Mandrake\AppData\Local\Temp\ns_tiles.csv", encoding="utf-8")))
cand = [r for r in rows if r["hilliness"]=="Flat" and r["biome"]=="AridShrubland" and float(r["swampiness"])==0 and 0<=float(r["elevation"])<400 and 15<=float(r["temperature"])<=30]
print("cands", len(cand))
with Session(lock=None) as s:
    for c in cand[:6]:
        g = s.call("jawa/world_tile_get", tiles=c["tile"])
        print(c["tile"], json.dumps(g)[:700])
