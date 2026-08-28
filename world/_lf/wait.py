import sys, io, time, json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
for i in range(60):
    try:
        h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=25); b.connect()
        r=b.call('rimworld/get_game_info',{})
        print("BRIDGE BACK after ~%ds: %s"%(i*30, json.dumps({k:v for k,v in r.items() if k!='operation'})))
        sys.exit(0)
    except Exception as e:
        print("  still busy (%d): %s"%(i, str(e)[:70]), flush=True)
    time.sleep(5)
print("BRIDGE STILL WEDGED after ~30 min")
