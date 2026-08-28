import sys, json, io
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=100); b.connect()
r=b.call('rimworld/get_game_info',{})
print("ALIVE", json.dumps({k:v for k,v in r.items() if k!='operation'}))
