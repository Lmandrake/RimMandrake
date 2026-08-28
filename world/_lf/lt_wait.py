import sys, json, io, time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=120); b.connect()
def c(m,a=None):
    try:
        r=b.call(m,a or {}); r.pop('operation',None); return r
    except Exception as e: return {"success":False,"EXC":str(e)}
for i in range(24):
    st=c('rimworld/get_cell_info',{'x':10,'z':10}).get('state') or {}
    gi=c('rimworld/get_game_info')
    print("  t+%3ds programState=%-14s currentMapId=%-8s mapCount=%s ticks=%s"%(
        i*5, st.get('programState'), st.get('currentMapId'), gi.get('mapCount'), gi.get('ticksGame')))
    if st.get('currentMapId'):
        print("MAP IS DRIVABLE"); break
    time.sleep(5)
