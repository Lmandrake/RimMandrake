import json, sys
d=json.load(open(sys.argv[1]))
from collections import Counter
c=Counter(); 
for ch in d["chains"]:
    for comp in ch["components"]: c[comp["verdict"]]+=1
print(sys.argv[2], dict(c), "ticks", sum((ch["situational"] or {}).get("ticks_spent",0) for ch in d["chains"]), "surprises", sum(len((ch["situational"] or {}).get("surprises",[])) for ch in d["chains"]))
for ch in d["chains"]:
    for comp in ch["components"]:
        if comp["verdict"] not in ("PASS",): print("   ", comp["verdict"], comp["name"], "|", (comp["detail"] or "")[:170])
    s=ch["situational"] or {}
    for h in s.get("hits_seen",[]):
        if h["severity"] in ("SURPRISE","FATAL"): print("    HIT", h["severity"], h["detector"], h["summary"][:120])
