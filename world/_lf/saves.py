import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
r=b.call('jawa/ideo_of',{'precepts':False}); r.pop('operation',None)
for k in ('ideologyActive','ideosTotal','ideosReturned','believersCounted','pawnsScanned','message'):
    print("  %-18s %s"%(k, json.dumps(r.get(k))[:160]))
s=b.call('rimworld/list_saves',{}); s.pop('operation',None)
sv=s.get('saves') or s.get('files') or []
print("\nsaves on disk: %d"%len(sv))
for q in sv[:8]: print("   ", json.dumps(q)[:180])
