import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/ideo_of',{'precepts':False}); r.pop('operation',None)
print("top keys:", sorted(r.keys()))
for k,v in r.items():
    if isinstance(v,list):
        print("'%s' -> %d entries"%(k,len(v)))
        for q in v[:12]: print("   ", json.dumps(q)[:220])
print("note:", str(r.get('note'))[:300])
