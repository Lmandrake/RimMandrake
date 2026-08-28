import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
ts=b.list_tools()
out=[{"name":x.get("name"),"description":(x.get("description") or "")[:400],
      "params":sorted((x.get("inputSchema",{}).get("properties") or {}).keys())} for x in ts]
io.open(r"D:\Luke\dev\Rimworld\world\_lf\live_tools.json","w",encoding="utf-8").write(
    json.dumps(sorted(out,key=lambda q:q["name"]), indent=1, ensure_ascii=False))
print("wrote", len(out), "tools;", sum(1 for q in out if q["name"].startswith("jawa/")), "jawa")
