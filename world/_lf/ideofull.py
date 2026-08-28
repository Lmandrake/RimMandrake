import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/ideo_of',{'precepts':True}); r.pop('operation',None)
for k,v in r.items():
    if k!='ideos': print("  %-24s %s"%(k, json.dumps(v)[:200]))
print("\nFULL ideo record:")
print(json.dumps(r['ideos'][0], indent=1)[:1500])
