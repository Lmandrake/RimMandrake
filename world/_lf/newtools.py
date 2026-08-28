import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=120); b.connect()
ts=b.list_tools()
out={x['name']:{"d":(x.get('description') or '')[:200],
                "p":sorted((x.get('inputSchema',{}).get('properties') or {}).keys())} for x in ts}
io.open(r"D:\Luke\dev\Rimworld\world\_lf\tools166.json","w",encoding='utf-8').write(json.dumps(out,indent=1,ensure_ascii=False))
old=set(json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\live_tools.json",encoding="utf-8"))[0].keys()) if False else None
prev={q['name'] for q in json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\live_tools.json",encoding="utf-8"))}
new=sorted(set(out)-prev)
print("live %d tools; NEW since this morning: %d"%(len(out), len(new)))
for n in new: print("  %-34s %s"%(n, out[n]['d'].split('.')[0][:96]))
