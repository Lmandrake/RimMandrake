import sys, json, io, re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=200); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
objs=(c('jawa/world_objects_get',{'limit':400}).get('objects') or [])
print("objects:", len(objs))
mine=[q for q in objs if str(q.get('faction')) in ('PlayerColony','Player') or 'Map' in str(q.get('def'))]
print("player / map-parent objects:", json.dumps(mine)[:500])
tools=json.load(io.open(r"D:\Luke\dev\Rimworld\world\_lf\tools166.json",encoding='utf-8'))
hits=[n for n,q in tools.items() if re.search(r'current map.*tile|tile.*current map|map.?parent|Tile of the map', q['d'], re.I)]
print("\ntools whose description mentions the current map's tile:", hits)
# does world_view centre on it? and does get_camera_state know?
print("camera:", json.dumps(c('rimworld/get_camera_state'))[:200])
