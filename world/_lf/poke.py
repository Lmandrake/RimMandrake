import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=90); b.connect()
r=b.call('jawa/get_def',{'defName':'guy762_JawaHood','defType':'ThingDef'}); r.pop('operation',None)
print("a real jawa TOOL call ->", r.get('success'), json.dumps(r)[:120])
