import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t); b.connect()
ps=b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []
j=[x for x in ps if x.get('kindDef')=='Jawa_Tribal_Scavenger'][0]
for args in ({'pawnName':j['name']}, {'thingId':'Thing_'+j['id']}, {'pawnId':'Thing_'+j['id']}):
    try:
        r=b.call('rimworld/get_map_target_info',args); r.pop('operation',None)
        print(list(args)[0],"->", json.dumps(r)[:900]); print()
    except Exception as e: print(list(args)[0],"ERR",e)
