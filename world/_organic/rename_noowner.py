import sys, json, csv
sys.path.insert(0,r'D:\Luke\dev\Rimworld\src\RimMandrake\Utils')
from rimbridge_client import RimBridge, resolve_endpoint
h,p,t = resolve_endpoint()
rb = RimBridge(h,p,t); rb.connect()
b=lambda r:{k:v for k,v in r.items() if k!="operation"}
print("rename:", json.dumps(b(rb.call("jawa/world_objects_set",{"ids":"244","name":"Unbound Exception"})))[:70])
print("commit:", json.dumps(b(rb.call("jawa/world_commit",{})))[:70])
objs = rb.call("jawa/world_objects_get", {"limit":5000})["objects"]
json.dump(objs, open(r'D:\Luke\dev\Rimworld\world\_organic\objects_live15.json','w'))
T={int(r['tile']):r for r in csv.DictReader(open(r'D:\Luke\dev\Rimworld\world\_now7.csv'))}
o=[x for x in objs if x.get('name')=="Unbound Exception"]
print("VERIFY:", o[0]['tile'], o[0]['label'], o[0]['factionName'], T[o[0]['tile']]['feature'] if o else "ABSENT")
print("No Owner gone?", not any(x.get('name')=='No Owner' for x in objs))
