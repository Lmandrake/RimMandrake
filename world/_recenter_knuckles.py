import sys, csv, math
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
geo={int(r['tile']):r for r in csv.DictReader(open(r"D:\Luke\dev\Rimworld\world\ASHKARR_WORLDMAP_tiles.csv"))}
kn=[t for t,g in geo.items() if g['region'] in ('Level','Knuckles')]  # combined by original CSV region
# 3D centroid on sphere (lat/lon), then nearest tile
import statistics
def xyz(lat,lon):
    la,lo=math.radians(lat),math.radians(lon); return (math.cos(la)*math.cos(lo),math.cos(la)*math.sin(lo),math.sin(la))
cx=sum(xyz(float(geo[t]['lat']),float(geo[t]['lon']))[0] for t in kn)/len(kn)
cy=sum(xyz(float(geo[t]['lat']),float(geo[t]['lon']))[1] for t in kn)/len(kn)
cz=sum(xyz(float(geo[t]['lat']),float(geo[t]['lon']))[2] for t in kn)/len(kn)
center=max(kn, key=lambda t:(lambda p:p[0]*cx+p[1]*cy+p[2]*cz)(xyz(float(geo[t]['lat']),float(geo[t]['lon']))))
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    kn_id={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":300}).get("features",[])}['Knuckles']['uniqueID']
    r=rb.call("jawa/world_features_set", {"action":"update","featureId":kn_id,"centerOnTile":center})
    rb.call("jawa/world_commit", {})
    print("recentered Knuckles on tile", center, "success:", r.get('success'))
