import sys, json, io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, r"D:\Luke\dev\Rimworld\src\RimMandrake\Utils")
import rimbridge_client as rc
h,p,t = rc.resolve_endpoint(); b = rc.RimBridge(host=h,port=p,token=t,timeout=120); b.connect()
print("game_info:", json.dumps({k:v for k,v in b.call('rimworld/get_game_info',{}).items() if k!='operation'}))
print("pawns:", len(b.call('jawa/list_pawns',{'limit':999}).get('pawns') or []))
