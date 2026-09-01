import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
from rimbridge_client import RimBridge, resolve_endpoint
host, port, token = resolve_endpoint()
out={}
with RimBridge(host, port, token) as rb:
    for f in ["Pirate","Empire","Jawa_HuttCartel","OutlanderCivil","CASacrilegHunters","TribeCivil"]:
        out[f]=rb.call("jawa/get_def", {"defName":f,"defType":"FactionDef"})
    out["_audit"]=rb.call("jawa/pawnkind_audit", {"limit":40})
with io.open("defs.json","w",encoding="utf-8") as fh: json.dump(out,fh,indent=1,ensure_ascii=False)
d=out["Pirate"]
print("GET_DEF KEYS:", [k for k in d.keys() if k!="operation"])
print("SAMPLE:", json.dumps(d, ensure_ascii=False)[:1500])
