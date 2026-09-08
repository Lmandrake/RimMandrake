import sys
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
# old -> new (terrain-fitting, matches the world's evocative-compound style)
RENAMES={
  'Venom Wood':'Fuelmere',    # 96% propane lakes -> a mere (lake) of fuel
  'Thornend':'Frostvein',     # 62% blue desert -> cold hydrocarbon vein
  'South Crags':'Sootreach',  # blue desert/Rot/fungal, no crags -> dark mixed reach
  'Coldshelf':'Sunshelf',     # 87% warm terminator desert -> keep 'shelf', swap cold->sun
}
host, port, token = resolve_endpoint()
with RimBridge(host, port, token) as rb:
    feats={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":400}).get("features",[])}
    for old,new in RENAMES.items():
        if old not in feats: print(f"  {old}: NOT FOUND, skip"); continue
        fid=feats[old]['uniqueID']
        r=rb.call("jawa/world_features_set", {"action":"update","featureId":fid,"name":new})
        print(f"  {old} -> {new}: {r.get('success')}")
    rb.call("jawa/world_commit", {})
    n2={f['name']:f for f in rb.call("jawa/world_features_get", {"limit":400}).get("features",[])}
    for old,new in RENAMES.items():
        print(f"  verify {new}: exists={new in n2} | old {old} gone={old not in n2}")
