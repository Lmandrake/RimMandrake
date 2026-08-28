import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=300); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
print("restore tile 18393 to its original 14.72 C")
print(json.dumps(c('jawa/world_tile_set',{'tiles':'18393','temperature':14.7229729,'readBack':1}))[:230])
print("commit:", c('jawa/world_commit',{}).get('success'))
c('rimworld/step_game_ticks',{'ticks':400,'timeoutMs':120000})
ct=c('jawa/cell_temperature',{'cell':'160,160'})
print("map now: outdoor=%.1f seasonal=%.1f"%(ct.get('outdoorTemp') or 0, ct.get('seasonalTemp') or 0))
