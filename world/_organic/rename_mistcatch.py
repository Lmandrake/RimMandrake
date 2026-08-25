import sys, json, csv
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
b=lambda r:{k:v for k,v in r.items() if k!="operation"}
print("rename:", json.dumps(b(rb.call("jawa/world_objects_set",{"ids":"197","name":"Misty Isles"})))[:70])
print("commit:", json.dumps(b(rb.call("jawa/world_commit",{})))[:70])
objs = rb.call("jawa/world_objects_get", {"limit":5000})["objects"]
json.dump(objs, open(r'D:\Luke\dev\Rimworld\world\_organic\objects_live20.json','w'))
T={int(r['tile']):r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_now7.csv'))}
nb={int(r['tile']):[int(r['n%d'%i]) for i in range(6) if int(r['n%d'%i])>=0] for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_organic\neighbors.csv'))}
o=[x for x in objs if x.get('name')=="Misty Isles"]
t=o[0]['tile']; r=T[t]
water=[n for n in nb[t] if int(T[n]['waterCovered'])]
print("VERIFY:", t, o[0]['factionName'], r['biome'], r['feature'], "elev", r['elevation'], "waterNeighbours", len(water))
print("Mistcatch gone?", not any(x.get('name')=='Mistcatch' for x in objs))
