import json,sys,collections
for mod in sys.argv[1:]:
    try: d=json.load(open("Transient/l2sweep_%s.json"%mod))
    except Exception as e: print(mod,"NOJSON",e); continue
    if d.get("error"): print(mod,"ERROR",d["error"]); continue
    cnt=collections.Counter(); rows=[]
    for c in d.get("chains",[]):
        for k in c.get("components",[]) or []:
            v=k.get("verdict"); cnt[v]+=1
            rows.append((v,c.get("name"),k.get("name"),str(k.get("detail"))[:200]))
    print("##",mod,"all_green=",d.get("all_green"),dict(cnt))
    for r in rows:
        if r[0]!="PASS": print("  ",r[0],r[1],"/",r[2],"|",r[3])
