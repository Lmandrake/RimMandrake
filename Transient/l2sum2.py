import json,sys
d=json.load(open(sys.argv[1]))
for c in d.get("chains",[]):
    print("CHAIN",c.get("name") or c.get("chain"), c.get("verdict") or c.get("green"))
    for k in c.get("components",[]):
        det=str(k.get("detail",""))[:int(sys.argv[2]) if len(sys.argv)>2 else 200]
        print("  ",k.get("name"),k.get("verdict") or k.get("status"),"|",det)
