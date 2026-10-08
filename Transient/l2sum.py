import json,sys,collections
for m in sys.argv[1:]:
    d=json.load(open("Transient/l2sweep_%s.json"%m))
    if "error" in d: print(m,"ERROR",d["error"]); continue
    c=collections.Counter(); fails=[]
    for ch in d["chains"]:
        for co in ch["components"]:
            c[co["verdict"]]+=1
            if co["verdict"] not in("PASS","UNMEASURED"): fails.append((ch["name"],co["name"],co["verdict"],co["detail"][:400]))
    print(m,dict(c))
    for f in fails: print("  ",f)
