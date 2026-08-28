import sys, io, time, json
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
LOG=r"D:\Luke\dev\Rimworld\world\_lf\wait2.log"
t0=time.time()
def w(s):
    with io.open(LOG,"a",encoding="utf-8") as f: f.write("%6.0fs %s\n"%(time.time()-t0,s))
w("start")
for i in range(40):
    try:
        h,p,tk = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=tk,timeout=45); b.connect()
        r=b.call('rimworld/get_game_info',{})
        w("BRIDGE BACK: %s"%json.dumps({k:v for k,v in r.items() if k!='operation'}))
        break
    except Exception as e:
        w("busy: %s"%str(e)[:60])
    time.sleep(20)
else:
    w("STILL WEDGED")
