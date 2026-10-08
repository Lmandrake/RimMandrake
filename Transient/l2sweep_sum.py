import json,sys
d=json.load(open(sys.argv[1]))
if d.get("error"): print("ERROR",d["error"],d.get("tb","")[-600:]); sys.exit()
for c in d.get("chains",[]):
    print("CHAIN",c.get("name"))
    for k in c.get("components",[]) or []:
        print("   ",k.get("verdict"),k.get("name"),"|",str(k.get("detail"))[:260])
